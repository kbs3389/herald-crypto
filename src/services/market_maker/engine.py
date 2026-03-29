"""
Herald Crypto Exchange - Market Making Engine

Automated market maker that continuously quotes bid/ask around reference prices.
Features inventory-aware pricing, dynamic spreads, and auto-cancel/replace.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from src.core.matching.order_book import OrderBook, OrderEntry

logger = logging.getLogger(__name__)


class MarketMakerConfig:
    """Configuration for the market maker."""

    def __init__(
        self,
        instrument_id: str,
        base_spread_bps: Decimal = Decimal("10"),  # 10 bps = 0.1%
        num_levels: int = 10,
        order_size: Decimal = Decimal("0.1"),
        max_position: Decimal = Decimal("10"),
        skew_factor: Decimal = Decimal("0.5"),  # How much to skew on inventory
        refresh_interval: float = 5.0,  # seconds
        volatility_multiplier: Decimal = Decimal("1.0"),
    ):
        self.instrument_id = instrument_id
        self.base_spread_bps = base_spread_bps
        self.num_levels = num_levels
        self.order_size = order_size
        self.max_position = max_position
        self.skew_factor = skew_factor
        self.refresh_interval = refresh_interval
        self.volatility_multiplier = volatility_multiplier


class MarketMaker:
    """
    Automated market maker with inventory management.

    Strategy:
    - Places bid/ask quotes at multiple levels around a reference price
    - Skews quotes based on current inventory to manage risk
    - Dynamically adjusts spreads based on volatility
    - Cancels and replaces stale orders on each refresh cycle
    """

    def __init__(self, config: MarketMakerConfig, order_book: OrderBook):
        self.config = config
        self.book = order_book
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._reference_price: Optional[Decimal] = None
        self._inventory: Decimal = Decimal("0")
        self._pnl: Decimal = Decimal("0")
        self._order_ids: list = []
        self._total_quotes: int = 0
        self._total_fills: int = 0
        self.account_id = f"mm-{config.instrument_id}"

    def set_reference_price(self, price: Decimal) -> None:
        """Update the reference price (e.g. from Binance feed)."""
        self._reference_price = price

    def update_inventory(self, delta: Decimal) -> None:
        """Update inventory position after a fill."""
        self._inventory += delta
        self._total_fills += 1

    @property
    def status(self) -> dict:
        return {
            "instrument_id": self.config.instrument_id,
            "running": self._running,
            "reference_price": str(self._reference_price) if self._reference_price else None,
            "inventory": str(self._inventory),
            "pnl": str(self._pnl),
            "total_quotes": self._total_quotes,
            "total_fills": self._total_fills,
            "active_orders": len(self._order_ids),
        }

    async def start(self) -> None:
        """Start the market-making loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Market maker started for {self.config.instrument_id}")

    async def stop(self) -> None:
        """Stop the market-making loop and cancel all orders."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._cancel_all_orders()
        logger.info(f"Market maker stopped for {self.config.instrument_id}")

    async def _run_loop(self) -> None:
        """Main market-making loop."""
        while self._running:
            try:
                self._refresh_quotes()
            except Exception as e:
                logger.warning(f"MM refresh error for {self.config.instrument_id}: {e}")
            await asyncio.sleep(self.config.refresh_interval)

    def _refresh_quotes(self) -> None:
        """Cancel old orders and place new quotes."""
        if self._reference_price is None:
            # Fall back to book mid-price
            if self.book.best_bid and self.book.best_ask:
                self._reference_price = (self.book.best_bid + self.book.best_ask) / 2
            else:
                return

        # Cancel existing orders
        self._cancel_all_orders()

        # Calculate inventory-adjusted mid price
        mid = self._reference_price
        inventory_skew = self._inventory * self.config.skew_factor
        adjusted_mid = mid - inventory_skew * mid * Decimal("0.0001")

        # Calculate spread
        base_spread = mid * self.config.base_spread_bps / Decimal("10000")
        spread = base_spread * self.config.volatility_multiplier

        # Place orders at multiple levels
        now = datetime.utcnow()
        for i in range(1, self.config.num_levels + 1):
            level_offset = spread * Decimal(str(i))

            # Size decreases at further levels
            size = self.config.order_size / Decimal(str(i))
            if size < Decimal("0.00001"):
                continue

            # Check position limits
            if self._inventory < self.config.max_position:
                bid_price = adjusted_mid - level_offset
                bid_order = OrderEntry(
                    order_id=uuid4(),
                    account_id=self.account_id,
                    price=bid_price,
                    quantity=size,
                    remaining=size,
                    side="BUY",
                    timestamp=now,
                    sequence=0,
                    self_trade_prevention=True,
                )
                result = self.book.match_order(bid_order)
                self._order_ids.append(bid_order.order_id)
                self._total_quotes += 1

                # Track fills
                for fill in result.fills:
                    self._inventory += fill.quantity
                    self._pnl -= fill.price * fill.quantity

            if self._inventory > -self.config.max_position:
                ask_price = adjusted_mid + level_offset
                ask_order = OrderEntry(
                    order_id=uuid4(),
                    account_id=self.account_id,
                    price=ask_price,
                    quantity=size,
                    remaining=size,
                    side="SELL",
                    timestamp=now,
                    sequence=0,
                    self_trade_prevention=True,
                )
                result = self.book.match_order(ask_order)
                self._order_ids.append(ask_order.order_id)
                self._total_quotes += 1

                for fill in result.fills:
                    self._inventory -= fill.quantity
                    self._pnl += fill.price * fill.quantity

    def _cancel_all_orders(self) -> None:
        """Cancel all resting orders placed by this market maker."""
        for oid in self._order_ids:
            self.book.cancel_order(oid)
        self._order_ids.clear()


class MarketMakerManager:
    """Manages multiple market maker instances."""

    def __init__(self):
        self._makers: dict[str, MarketMaker] = {}

    def add_maker(self, config: MarketMakerConfig, book: OrderBook) -> MarketMaker:
        mm = MarketMaker(config, book)
        self._makers[config.instrument_id] = mm
        return mm

    def get_maker(self, instrument_id: str) -> Optional[MarketMaker]:
        return self._makers.get(instrument_id)

    async def start_all(self) -> None:
        for mm in self._makers.values():
            await mm.start()

    async def stop_all(self) -> None:
        for mm in self._makers.values():
            await mm.stop()

    def get_status(self) -> list[dict]:
        return [mm.status for mm in self._makers.values()]

    def update_price(self, instrument_id: str, price: Decimal) -> None:
        mm = self._makers.get(instrument_id)
        if mm:
            mm.set_reference_price(price)
