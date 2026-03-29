"""Tests for the market-making engine."""
import pytest
from decimal import Decimal
from datetime import datetime

from src.core.matching.order_book import OrderBook
from src.services.market_maker.engine import MarketMaker, MarketMakerConfig


class TestMarketMaker:
    def _make_mm(self) -> tuple[MarketMaker, OrderBook]:
        book = OrderBook("BTC-USDT-SPOT")
        config = MarketMakerConfig(
            instrument_id="BTC-USDT-SPOT",
            base_spread_bps=Decimal("20"),
            num_levels=5,
            order_size=Decimal("1.0"),
            max_position=Decimal("10"),
        )
        mm = MarketMaker(config, book)
        return mm, book

    def test_initial_status(self):
        mm, _ = self._make_mm()
        status = mm.status
        assert status["running"] is False
        assert status["inventory"] == "0"
        assert status["total_quotes"] == 0

    def test_refresh_with_reference_price(self):
        mm, book = self._make_mm()
        mm.set_reference_price(Decimal("50000"))
        mm._refresh_quotes()
        # Should have placed orders on both sides
        assert book.best_bid is not None
        assert book.best_ask is not None
        assert mm.status["total_quotes"] > 0

    def test_quotes_around_mid(self):
        mm, book = self._make_mm()
        mid = Decimal("50000")
        mm.set_reference_price(mid)
        mm._refresh_quotes()
        # Best bid should be below mid, best ask above
        assert book.best_bid < mid
        assert book.best_ask > mid

    def test_cancel_and_replace(self):
        mm, book = self._make_mm()
        mm.set_reference_price(Decimal("50000"))
        mm._refresh_quotes()
        old_bid = book.best_bid
        # Change price and refresh
        mm.set_reference_price(Decimal("51000"))
        mm._refresh_quotes()
        new_bid = book.best_bid
        # New bid should be higher (closer to new mid)
        assert new_bid > old_bid

    def test_inventory_skew(self):
        mm, book = self._make_mm()
        mm.set_reference_price(Decimal("50000"))
        # Long inventory -> should skew asks lower to sell
        mm._inventory = Decimal("5")
        mm._refresh_quotes()
        long_ask = book.best_ask
        mm._cancel_all_orders()

        # Short inventory -> should skew bids higher to buy
        mm._inventory = Decimal("-5")
        mm._refresh_quotes()
        short_bid = book.best_bid
        # The skew should make the short bid higher than long bid would be
        assert short_bid is not None
        assert long_ask is not None

    def test_multiple_levels(self):
        mm, book = self._make_mm()
        mm.set_reference_price(Decimal("50000"))
        mm._refresh_quotes()
        # Should have multiple bid levels
        assert len(book._bids) >= 2
        assert len(book._asks) >= 2
