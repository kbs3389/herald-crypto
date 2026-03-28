"""
Herald Crypto Exchange - Order Book and Matching Engine

Deterministic matching engine with price-time priority.
No synchronous I/O in the matching loop (HC-005).
Single writer per order book shard (HC-001).
All accepted commands journaled before execution (HC-002).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class OrderEntry:
    """An order resting in the book."""
    order_id: UUID
    account_id: str
    price: Decimal
    quantity: Decimal
    remaining: Decimal
    side: str
    timestamp: datetime
    sequence: int
    self_trade_prevention: bool = True


@dataclass(frozen=True)
class Fill:
    """A fill produced by the matching engine."""
    fill_id: UUID = field(default_factory=uuid4)
    maker_order_id: UUID = field(default_factory=uuid4)
    taker_order_id: UUID = field(default_factory=uuid4)
    maker_account_id: str = ""
    taker_account_id: str = ""
    price: Decimal = Decimal("0")
    quantity: Decimal = Decimal("0")
    maker_side: str = "BUY"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence: int = 0


@dataclass
class MatchResult:
    """Result of processing an incoming order."""
    fills: List[Fill] = field(default_factory=list)
    remaining_quantity: Decimal = Decimal("0")
    status: str = "ACCEPTED"


class PriceLevel:
    """Orders at a single price level, ordered by time priority."""

    def __init__(self, price: Decimal):
        self.price = price
        self.orders: List[OrderEntry] = []
        self.total_quantity: Decimal = Decimal("0")

    def add_order(self, order: OrderEntry) -> None:
        self.orders.append(order)
        self.total_quantity += order.remaining

    def remove_order(self, order_id: UUID) -> Optional[OrderEntry]:
        for i, order in enumerate(self.orders):
            if order.order_id == order_id:
                removed = self.orders.pop(i)
                self.total_quantity -= removed.remaining
                return removed
        return None

    @property
    def is_empty(self) -> bool:
        return len(self.orders) == 0


class OrderBook:
    """
    Price-time priority order book for a single instrument.

    Hard Constraints:
    - HC-001: Single writer per order book (enforced by caller)
    - HC-005: No synchronous I/O in matching loop
    """

    def __init__(self, instrument_id: str):
        self.instrument_id = instrument_id
        self._bids: Dict[Decimal, PriceLevel] = {}
        self._asks: Dict[Decimal, PriceLevel] = {}
        self._orders: Dict[UUID, OrderEntry] = {}
        self._sequence: int = 0
        self._fill_sequence: int = 0

    def match_order(self, order: OrderEntry) -> MatchResult:
        """Match an incoming order against the book. Pure computation - no I/O."""
        fills: List[Fill] = []
        remaining = order.remaining

        if order.side == "BUY":
            opposite_levels = sorted(self._asks.keys())
        else:
            opposite_levels = sorted(self._bids.keys(), reverse=True)

        for price in opposite_levels:
            if remaining <= 0:
                break
            if order.side == "BUY" and price > order.price:
                break
            if order.side == "SELL" and price < order.price:
                break

            level = self._asks[price] if order.side == "BUY" else self._bids[price]
            orders_to_remove = []

            for resting_order in level.orders:
                if remaining <= 0:
                    break
                if (order.self_trade_prevention and
                        order.account_id == resting_order.account_id):
                    continue

                fill_qty = min(remaining, resting_order.remaining)
                self._fill_sequence += 1

                fill = Fill(
                    fill_id=uuid4(),
                    maker_order_id=resting_order.order_id,
                    taker_order_id=order.order_id,
                    maker_account_id=resting_order.account_id,
                    taker_account_id=order.account_id,
                    price=resting_order.price,
                    quantity=fill_qty,
                    maker_side=resting_order.side,
                    timestamp=order.timestamp,
                    sequence=self._fill_sequence,
                )
                fills.append(fill)
                remaining -= fill_qty

                new_remaining = resting_order.remaining - fill_qty
                if new_remaining <= 0:
                    orders_to_remove.append(resting_order.order_id)
                else:
                    updated = OrderEntry(
                        order_id=resting_order.order_id,
                        account_id=resting_order.account_id,
                        price=resting_order.price,
                        quantity=resting_order.quantity,
                        remaining=new_remaining,
                        side=resting_order.side,
                        timestamp=resting_order.timestamp,
                        sequence=resting_order.sequence,
                        self_trade_prevention=resting_order.self_trade_prevention,
                    )
                    idx = level.orders.index(resting_order)
                    level.orders[idx] = updated
                    self._orders[resting_order.order_id] = updated

            for oid in orders_to_remove:
                level.remove_order(oid)
                self._orders.pop(oid, None)

            if level.is_empty:
                if order.side == "BUY":
                    del self._asks[price]
                else:
                    del self._bids[price]

        if remaining > 0:
            self._place_on_book(order, remaining)

        if not fills:
            status = "ACCEPTED"
        elif remaining > 0:
            status = "PARTIALLY_FILLED"
        else:
            status = "FILLED"

        return MatchResult(fills=fills, remaining_quantity=remaining, status=status)

    def _place_on_book(self, order: OrderEntry, remaining: Decimal) -> None:
        self._sequence += 1
        resting = OrderEntry(
            order_id=order.order_id,
            account_id=order.account_id,
            price=order.price,
            quantity=order.quantity,
            remaining=remaining,
            side=order.side,
            timestamp=order.timestamp,
            sequence=self._sequence,
            self_trade_prevention=order.self_trade_prevention,
        )
        levels = self._bids if order.side == "BUY" else self._asks
        if order.price not in levels:
            levels[order.price] = PriceLevel(order.price)
        levels[order.price].add_order(resting)
        self._orders[order.order_id] = resting

    def cancel_order(self, order_id: UUID) -> Optional[OrderEntry]:
        order = self._orders.pop(order_id, None)
        if order is None:
            return None
        levels = self._bids if order.side == "BUY" else self._asks
        if order.price in levels:
            levels[order.price].remove_order(order_id)
            if levels[order.price].is_empty:
                del levels[order.price]
        return order

    @property
    def best_bid(self) -> Optional[Decimal]:
        return max(self._bids.keys()) if self._bids else None

    @property
    def best_ask(self) -> Optional[Decimal]:
        return min(self._asks.keys()) if self._asks else None

    @property
    def spread(self) -> Optional[Decimal]:
        if self.best_bid and self.best_ask:
            return self.best_ask - self.best_bid
        return None
