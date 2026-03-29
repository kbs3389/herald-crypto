"""
Herald Crypto Exchange - Binance Market Data Client

Fetches real-time prices from Binance public REST API and WebSocket streams.
No API key required for public market data endpoints.
"""
from __future__ import annotations

import asyncio
import json
import logging
from decimal import Decimal
from typing import Callable, Optional

import httpx
import websockets

logger = logging.getLogger(__name__)

BINANCE_REST_BASE = "https://api.binance.com"
BINANCE_WS_BASE = "wss://stream.binance.com:9443/ws"

# Map our instrument IDs to Binance symbols
INSTRUMENT_TO_BINANCE = {
    "BTC-USDT-SPOT": "BTCUSDT",
    "ETH-USDT-SPOT": "ETHUSDT",
    "SOL-USDT-SPOT": "SOLUSDT",
    "XRP-USDT-SPOT": "XRPUSDT",
    "BTC-USDT-PERP": "BTCUSDT",
    "ETH-USDT-PERP": "ETHUSDT",
    "SOL-USDT-PERP": "SOLUSDT",
    "BNB-USDT-PERP": "BNBUSDT",
}

BINANCE_TO_INSTRUMENTS: dict[str, list[str]] = {}
for iid, sym in INSTRUMENT_TO_BINANCE.items():
    BINANCE_TO_INSTRUMENTS.setdefault(sym.lower(), []).append(iid)


class BinanceClient:
    """Client for Binance public market data."""

    def __init__(self):
        self._http = httpx.AsyncClient(timeout=10.0)
        self._ws_task: Optional[asyncio.Task] = None
        self._running = False
        self._price_callbacks: list[Callable] = []
        self._latest_prices: dict[str, Decimal] = {}

    async def fetch_prices(self) -> dict[str, Decimal]:
        """Fetch current prices from Binance REST API."""
        try:
            symbols = list(set(INSTRUMENT_TO_BINANCE.values()))
            url = f"{BINANCE_REST_BASE}/api/v3/ticker/price"
            resp = await self._http.get(url)
            resp.raise_for_status()
            data = resp.json()
            prices: dict[str, Decimal] = {}
            for item in data:
                symbol = item["symbol"]
                if symbol in symbols:
                    prices[symbol] = Decimal(item["price"])
            self._latest_prices = prices
            return prices
        except Exception as e:
            logger.warning(f"Failed to fetch Binance prices: {e}")
            return self._latest_prices

    def get_price_for_instrument(self, instrument_id: str) -> Optional[Decimal]:
        """Get the latest Binance price for a Herald instrument."""
        binance_sym = INSTRUMENT_TO_BINANCE.get(instrument_id)
        if binance_sym is None:
            return None
        return self._latest_prices.get(binance_sym)

    def on_price_update(self, callback: Callable) -> None:
        """Register a callback for real-time price updates."""
        self._price_callbacks.append(callback)

    async def start_websocket(self) -> None:
        """Start WebSocket connection for real-time price streams."""
        if self._running:
            return
        self._running = True
        self._ws_task = asyncio.create_task(self._ws_loop())

    async def stop_websocket(self) -> None:
        """Stop the WebSocket connection."""
        self._running = False
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass

    async def _ws_loop(self) -> None:
        """Main WebSocket loop with auto-reconnect."""
        symbols = list(set(s.lower() for s in INSTRUMENT_TO_BINANCE.values()))
        streams = [f"{s}@ticker" for s in symbols]
        url = f"{BINANCE_WS_BASE}/{'/'.join(streams)}"

        while self._running:
            try:
                async with websockets.connect(url) as ws:
                    logger.info("Connected to Binance WebSocket")
                    # Subscribe to combined stream
                    subscribe_msg = {
                        "method": "SUBSCRIBE",
                        "params": streams,
                        "id": 1,
                    }
                    await ws.send(json.dumps(subscribe_msg))

                    async for message in ws:
                        if not self._running:
                            break
                        try:
                            data = json.loads(message)
                            if "s" in data and "c" in data:
                                symbol = data["s"]
                                price = Decimal(data["c"])
                                self._latest_prices[symbol] = price
                                # Notify callbacks
                                instrument_ids = BINANCE_TO_INSTRUMENTS.get(
                                    symbol.lower(), []
                                )
                                for iid in instrument_ids:
                                    for cb in self._price_callbacks:
                                        try:
                                            await cb(iid, price, data)
                                        except Exception as e:
                                            logger.warning(
                                                f"Price callback error: {e}"
                                            )
                        except (json.JSONDecodeError, KeyError):
                            pass
            except Exception as e:
                if self._running:
                    logger.warning(f"Binance WS disconnected: {e}, reconnecting...")
                    await asyncio.sleep(5)

    async def fetch_orderbook(
        self, instrument_id: str, limit: int = 20
    ) -> Optional[dict]:
        """Fetch order book snapshot from Binance."""
        binance_sym = INSTRUMENT_TO_BINANCE.get(instrument_id)
        if binance_sym is None:
            return None
        try:
            url = f"{BINANCE_REST_BASE}/api/v3/depth"
            resp = await self._http.get(
                url, params={"symbol": binance_sym, "limit": limit}
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"Failed to fetch Binance orderbook: {e}")
            return None

    async def fetch_klines(
        self, instrument_id: str, interval: str = "1h", limit: int = 24
    ) -> Optional[list]:
        """Fetch kline/candlestick data from Binance."""
        binance_sym = INSTRUMENT_TO_BINANCE.get(instrument_id)
        if binance_sym is None:
            return None
        try:
            url = f"{BINANCE_REST_BASE}/api/v3/klines"
            resp = await self._http.get(
                url,
                params={"symbol": binance_sym, "interval": interval, "limit": limit},
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"Failed to fetch Binance klines: {e}")
            return None

    async def close(self) -> None:
        """Clean up resources."""
        await self.stop_websocket()
        await self._http.aclose()
