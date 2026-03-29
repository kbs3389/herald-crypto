"""
Herald Crypto Exchange - Market Data Service (Agent 06)

Real-time market data distribution via WebSocket.
Maintains trade history, ticker stats, and orderbook snapshots.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import WebSocket


class MarketDataService:
    """In-memory market data service with WebSocket broadcasting."""

    def __init__(self):
        self._trades: dict[str, list[dict]] = defaultdict(list)
        self._subscribers: dict[str, list[WebSocket]] = defaultdict(list)
        self._ticker_stats: dict[str, dict] = {}
        self._max_trades = 1000

    def record_trade(self, instrument_id: str, fill: Any) -> None:
        """Record a trade fill for history and stats."""
        trade = {
            "fill_id": str(fill.fill_id),
            "price": str(fill.price),
            "quantity": str(fill.quantity),
            "maker_side": fill.maker_side,
            "timestamp": fill.timestamp.isoformat(),
        }
        trades = self._trades[instrument_id]
        trades.append(trade)
        if len(trades) > self._max_trades:
            self._trades[instrument_id] = trades[-self._max_trades:]

        # Update ticker stats
        price = float(str(fill.price))
        stats = self._ticker_stats.get(instrument_id, {
            "last_price": None, "volume_24h": "0",
            "high_24h": None, "low_24h": None,
            "open_24h": None, "change_24h_pct": "0",
            "trade_count_24h": 0,
        })
        stats["last_price"] = str(fill.price)
        stats["volume_24h"] = str(Decimal(stats["volume_24h"]) + fill.quantity)
        stats["trade_count_24h"] = stats.get("trade_count_24h", 0) + 1

        if stats["high_24h"] is None or price > float(stats["high_24h"]):
            stats["high_24h"] = str(fill.price)
        if stats["low_24h"] is None or price < float(stats["low_24h"]):
            stats["low_24h"] = str(fill.price)
        if stats["open_24h"] is None:
            stats["open_24h"] = str(fill.price)
            stats["change_24h_pct"] = "0"
        else:
            open_price = float(stats["open_24h"])
            if open_price > 0:
                change = ((price - open_price) / open_price) * 100
                stats["change_24h_pct"] = f"{change:.2f}"

        self._ticker_stats[instrument_id] = stats

    def get_recent_trades(self, instrument_id: str, limit: int = 50) -> list[dict]:
        trades = self._trades.get(instrument_id, [])
        return list(reversed(trades[-limit:]))

    def get_ticker_stats(self, instrument_id: str) -> dict:
        return self._ticker_stats.get(instrument_id, {
            "last_price": None, "volume_24h": "0",
            "high_24h": None, "low_24h": None,
            "change_24h_pct": "0",
        })

    def add_subscriber(self, instrument_id: str, websocket: WebSocket) -> None:
        self._subscribers[instrument_id].append(websocket)

    def remove_subscriber(self, instrument_id: str, websocket: WebSocket) -> None:
        subs = self._subscribers.get(instrument_id, [])
        if websocket in subs:
            subs.remove(websocket)

    async def broadcast_trade(self, instrument_id: str, fills: list[dict]) -> None:
        """Broadcast trade fills to all subscribers of an instrument."""
        if not fills:
            return
        message = json.dumps({
            "type": "trade",
            "instrument_id": instrument_id,
            "trades": fills,
            "timestamp": datetime.utcnow().isoformat(),
        })
        subs = self._subscribers.get(instrument_id, [])
        dead = []
        for ws in subs:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            subs.remove(ws)

    async def broadcast_orderbook_update(self, instrument_id: str, data: dict) -> None:
        """Broadcast orderbook snapshot/delta to subscribers."""
        message = json.dumps({
            "type": "orderbook",
            "instrument_id": instrument_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })
        subs = self._subscribers.get(instrument_id, [])
        dead = []
        for ws in subs:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            subs.remove(ws)
