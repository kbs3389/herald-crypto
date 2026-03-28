"""
Herald Crypto Exchange - Order Management Service (Agent 05)

Centralized order lifecycle management: submission, validation,
routing, modification, cancellation, and status tracking.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID, uuid4
from collections import defaultdict


class OrderStatus(Enum):
    PENDING = auto()
    ACCEPTED = auto()
    PARTIALLY_FILLED = auto()
    FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()
    EXPIRED = auto()


class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()
    STOP_LIMIT = auto()
    STOP_MARKET = auto()
    TRAILING_STOP = auto()
    ICEBERG = auto()
    TWAP = auto()


class TimeInForce(Enum):
    GTC = auto()  # Good Till Cancel
    IOC = auto()  # Immediate Or Cancel
    FOK = auto()  # Fill Or Kill
    GTD = auto()  # Good Till Date
    DAY = auto()  # Day order


@dataclass
class ManagedOrder:
    order_id: str = field(default_factory=lambda: str(uuid4()))
    client_order_id: str = ""
    account_id: str = ""
    instrument_id: str = ""
    side: str = "BUY"
    order_type: OrderType = OrderType.LIMIT
    time_in_force: TimeInForce = TimeInForce.GTC
    quantity: Decimal = Decimal("0")
    filled_quantity: Decimal = Decimal("0")
    remaining_quantity: Decimal = Decimal("0")
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    trailing_offset: Optional[Decimal] = None
    display_quantity: Optional[Decimal] = None  # For iceberg orders
    status: OrderStatus = OrderStatus.PENDING
    fills: list = field(default_factory=list)
    average_fill_price: Optional[Decimal] = None
    total_fee: Decimal = Decimal("0")
    reject_reason: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    expiry: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)


class OrderManagementService:
    """Central order lifecycle management service."""

    def __init__(self):
        self._orders: dict[str, ManagedOrder] = {}
        self._user_orders: dict[str, list[str]] = defaultdict(list)
        self._instrument_orders: dict[str, list[str]] = defaultdict(list)
        self._client_order_map: dict[str, str] = {}

    def submit_order(self, account_id: str, instrument_id: str, side: str,
                     order_type: str, quantity: Decimal,
                     price: Optional[Decimal] = None,
                     stop_price: Optional[Decimal] = None,
                     time_in_force: str = "GTC",
                     client_order_id: str = "",
                     display_quantity: Optional[Decimal] = None,
                     expiry: Optional[datetime] = None) -> ManagedOrder:
        """Submit a new order to the order management system."""
        # Validate order type
        try:
            ot = OrderType[order_type]
        except KeyError:
            order = ManagedOrder(
                account_id=account_id, instrument_id=instrument_id,
                side=side, status=OrderStatus.REJECTED,
                reject_reason=f"Invalid order type: {order_type}",
            )
            return order

        try:
            tif = TimeInForce[time_in_force]
        except KeyError:
            tif = TimeInForce.GTC

        # Validate price for limit orders
        if ot in (OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.ICEBERG) and price is None:
            order = ManagedOrder(
                account_id=account_id, instrument_id=instrument_id,
                side=side, order_type=ot, status=OrderStatus.REJECTED,
                reject_reason="Limit orders require a price",
            )
            return order

        # Validate stop price for stop orders
        if ot in (OrderType.STOP_LIMIT, OrderType.STOP_MARKET) and stop_price is None:
            order = ManagedOrder(
                account_id=account_id, instrument_id=instrument_id,
                side=side, order_type=ot, status=OrderStatus.REJECTED,
                reject_reason="Stop orders require a stop price",
            )
            return order

        order = ManagedOrder(
            account_id=account_id, instrument_id=instrument_id,
            side=side, order_type=ot, time_in_force=tif,
            quantity=quantity, remaining_quantity=quantity,
            price=price, stop_price=stop_price,
            display_quantity=display_quantity, expiry=expiry,
            client_order_id=client_order_id or str(uuid4())[:8],
            status=OrderStatus.ACCEPTED,
        )

        self._orders[order.order_id] = order
        self._user_orders[account_id].append(order.order_id)
        self._instrument_orders[instrument_id].append(order.order_id)
        if client_order_id:
            self._client_order_map[client_order_id] = order.order_id

        return order

    def cancel_order(self, order_id: str, account_id: str = "") -> Optional[ManagedOrder]:
        order = self._orders.get(order_id)
        if order is None:
            return None
        if account_id and order.account_id != account_id:
            return None
        if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED):
            return None
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        return order

    def mass_cancel(self, account_id: str, instrument_id: str = "",
                    side: str = "") -> list[ManagedOrder]:
        """Cancel all open orders matching criteria."""
        cancelled = []
        for oid in self._user_orders.get(account_id, []):
            order = self._orders.get(oid)
            if order is None:
                continue
            if order.status not in (OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED):
                continue
            if instrument_id and order.instrument_id != instrument_id:
                continue
            if side and order.side != side:
                continue
            order.status = OrderStatus.CANCELLED
            order.cancelled_at = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            cancelled.append(order)
        return cancelled

    def record_fill(self, order_id: str, fill_price: Decimal,
                    fill_quantity: Decimal, fee: Decimal = Decimal("0")) -> Optional[ManagedOrder]:
        order = self._orders.get(order_id)
        if order is None:
            return None
        order.filled_quantity += fill_quantity
        order.remaining_quantity = order.quantity - order.filled_quantity
        order.total_fee += fee
        order.fills.append({
            "price": str(fill_price), "quantity": str(fill_quantity),
            "fee": str(fee), "timestamp": datetime.utcnow().isoformat(),
        })
        # Calculate average fill price
        total_value = sum(Decimal(f["price"]) * Decimal(f["quantity"]) for f in order.fills)
        total_qty = sum(Decimal(f["quantity"]) for f in order.fills)
        if total_qty > 0:
            order.average_fill_price = total_value / total_qty

        if order.remaining_quantity <= 0:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIALLY_FILLED
        order.updated_at = datetime.utcnow()
        return order

    def get_order(self, order_id: str) -> Optional[ManagedOrder]:
        return self._orders.get(order_id)

    def get_order_by_client_id(self, client_order_id: str) -> Optional[ManagedOrder]:
        oid = self._client_order_map.get(client_order_id)
        if oid:
            return self._orders.get(oid)
        return None

    def get_open_orders(self, account_id: str,
                        instrument_id: str = "") -> list[ManagedOrder]:
        result = []
        for oid in self._user_orders.get(account_id, []):
            order = self._orders.get(oid)
            if order and order.status in (OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED):
                if not instrument_id or order.instrument_id == instrument_id:
                    result.append(order)
        return result

    def get_order_history(self, account_id: str, limit: int = 50,
                          instrument_id: str = "") -> list[ManagedOrder]:
        result = []
        for oid in reversed(self._user_orders.get(account_id, [])):
            order = self._orders.get(oid)
            if order:
                if not instrument_id or order.instrument_id == instrument_id:
                    result.append(order)
            if len(result) >= limit:
                break
        return result

    def expire_orders(self) -> list[ManagedOrder]:
        """Expire orders past their expiry time."""
        now = datetime.utcnow()
        expired = []
        for order in self._orders.values():
            if (order.expiry and order.expiry <= now
                    and order.status in (OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED)):
                order.status = OrderStatus.EXPIRED
                order.updated_at = now
                expired.append(order)
        return expired
