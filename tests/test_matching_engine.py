"""Tests for the matching engine and order book."""
import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from src.core.matching.order_book import OrderBook, OrderEntry, Fill, MatchResult


class TestOrderBook:
    def _make_order(self, side: str, price: str, qty: str, account: str = "user1") -> OrderEntry:
        return OrderEntry(
            order_id=uuid4(),
            account_id=account,
            price=Decimal(price),
            quantity=Decimal(qty),
            remaining=Decimal(qty),
            side=side,
            timestamp=datetime.utcnow(),
            sequence=0,
        )

    def test_empty_book(self):
        book = OrderBook("BTC-USDT-SPOT")
        assert book.best_bid is None
        assert book.best_ask is None
        assert book.spread is None

    def test_add_bid(self):
        book = OrderBook("BTC-USDT-SPOT")
        order = self._make_order("BUY", "50000", "1.0")
        result = book.match_order(order)
        assert result.status == "ACCEPTED"
        assert result.remaining_quantity == Decimal("1.0")
        assert book.best_bid == Decimal("50000")

    def test_add_ask(self):
        book = OrderBook("BTC-USDT-SPOT")
        order = self._make_order("SELL", "51000", "0.5")
        result = book.match_order(order)
        assert result.status == "ACCEPTED"
        assert book.best_ask == Decimal("51000")

    def test_match_crossing_orders(self):
        book = OrderBook("BTC-USDT-SPOT")
        # Place resting bid
        bid = self._make_order("BUY", "50000", "1.0", "buyer")
        book.match_order(bid)
        # Place crossing ask
        ask = self._make_order("SELL", "49000", "0.5", "seller")
        result = book.match_order(ask)
        assert result.status == "FILLED"
        assert len(result.fills) == 1
        assert result.fills[0].quantity == Decimal("0.5")
        assert result.fills[0].price == Decimal("50000")  # Maker price

    def test_partial_fill(self):
        book = OrderBook("BTC-USDT-SPOT")
        bid = self._make_order("BUY", "50000", "0.3", "buyer")
        book.match_order(bid)
        ask = self._make_order("SELL", "49000", "1.0", "seller")
        result = book.match_order(ask)
        assert result.status == "PARTIALLY_FILLED"
        assert len(result.fills) == 1
        assert result.fills[0].quantity == Decimal("0.3")
        assert result.remaining_quantity == Decimal("0.7")

    def test_no_self_trade(self):
        book = OrderBook("BTC-USDT-SPOT")
        bid = self._make_order("BUY", "50000", "1.0", "same_user")
        book.match_order(bid)
        ask = self._make_order("SELL", "49000", "0.5", "same_user")
        result = book.match_order(ask)
        # Should not fill against own order
        assert len(result.fills) == 0

    def test_price_time_priority(self):
        book = OrderBook("BTC-USDT-SPOT")
        # Place two bids at same price
        bid1 = self._make_order("BUY", "50000", "1.0", "first")
        bid2 = self._make_order("BUY", "50000", "1.0", "second")
        book.match_order(bid1)
        book.match_order(bid2)
        # Sell should match first bid (time priority)
        ask = self._make_order("SELL", "49000", "0.5", "seller")
        result = book.match_order(ask)
        assert result.fills[0].maker_account_id == "first"

    def test_cancel_order(self):
        book = OrderBook("BTC-USDT-SPOT")
        order = self._make_order("BUY", "50000", "1.0")
        book.match_order(order)
        assert book.best_bid == Decimal("50000")
        cancelled = book.cancel_order(order.order_id)
        assert cancelled is not None
        assert book.best_bid is None

    def test_multiple_price_levels(self):
        book = OrderBook("BTC-USDT-SPOT")
        book.match_order(self._make_order("BUY", "49000", "1.0", "a"))
        book.match_order(self._make_order("BUY", "50000", "1.0", "b"))
        book.match_order(self._make_order("BUY", "48000", "1.0", "c"))
        assert book.best_bid == Decimal("50000")

    def test_spread_calculation(self):
        book = OrderBook("BTC-USDT-SPOT")
        book.match_order(self._make_order("BUY", "49900", "1.0", "buyer"))
        book.match_order(self._make_order("SELL", "50100", "1.0", "seller"))
        assert book.spread == Decimal("200")

    def test_multi_level_match(self):
        book = OrderBook("BTC-USDT-SPOT")
        book.match_order(self._make_order("SELL", "50000", "0.5", "s1"))
        book.match_order(self._make_order("SELL", "50100", "0.5", "s2"))
        # Large buy sweeps both levels
        buy = self._make_order("BUY", "51000", "1.0", "buyer")
        result = book.match_order(buy)
        assert result.status == "FILLED"
        assert len(result.fills) == 2
        assert result.fills[0].price == Decimal("50000")
        assert result.fills[1].price == Decimal("50100")
