"""
Herald Crypto Exchange - API Gateway (Agent 07)

FastAPI-based API gateway providing REST endpoints for the exchange.
Routes requests to appropriate internal services.
Integrates: Binance market data, market maker, blockchain adapters,
fiat gateway, persistent database, and WebSocket real-time feeds.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.ledger.ledger import DebitCredit, EntryType, Ledger, LedgerEntry, LedgerTransaction
from src.core.matching.journal import CommandJournal, CommandType
from src.core.matching.order_book import Fill, OrderBook, OrderEntry
from src.core.risk.risk_engine import RiskCheckRequest, RiskEngine, RiskParameters
from src.services.binance.client import INSTRUMENT_TO_BINANCE, BinanceClient
from src.services.blockchain.adapters import ChainAdapterManager
from src.services.database.models import (
    InstrumentModel,
    OrderModel,
    UserModel,
)
from src.services.database.persistence import init_db, session_scope
from src.services.fiat.gateway import PaymentGateway
from src.services.fiat.gateway import PaymentMethod as GWPaymentMethod
from src.services.iam.service import IAMService, create_access_token, get_current_user
from src.services.market_data.service import MarketDataService
from src.services.market_maker.engine import MarketMakerConfig, MarketMakerManager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared in-process singletons (wired up at startup)
# ---------------------------------------------------------------------------

order_books: dict[str, OrderBook] = {}
ledger = Ledger()
risk_engine = RiskEngine()
journal = CommandJournal(shard_id="primary")
market_data = MarketDataService()
iam_service = IAMService()

# New service instances
binance_client = BinanceClient()
mm_manager = MarketMakerManager()
chain_adapters = ChainAdapterManager()
payment_gateway = PaymentGateway()

# Fallback base prices used for seeding when Binance is unavailable
FALLBACK_PRICES: dict[str, Decimal] = {
    "BTC-USDT-SPOT": Decimal("67500"), "ETH-USDT-SPOT": Decimal("3450"),
    "BTC-USDT-PERP": Decimal("67520"), "ETH-USDT-PERP": Decimal("3452"),
    "SOL-USDT-SPOT": Decimal("178"), "XRP-USDT-SPOT": Decimal("0.62"),
    "SOL-USDT-PERP": Decimal("178.5"), "BNB-USDT-PERP": Decimal("620"),
    "BTC-20260630-80000-C": Decimal("2500"), "BTC-20260630-80000-P": Decimal("1200"),
    "ETH-20260630-5000-C": Decimal("180"), "ETH-20260630-5000-P": Decimal("95"),
    "BTC-20260930-100000-C": Decimal("1800"), "BTC-20260930-100000-P": Decimal("3500"),
}

INSTRUMENTS = [
    # ── Spot ──
    {"id": "BTC-USDT-SPOT", "base": "BTC", "quote": "USDT", "type": "SPOT",
     "tick": "0.01", "lot": "0.00001", "min_size": "0.00001", "max_size": "1000"},
    {"id": "ETH-USDT-SPOT", "base": "ETH", "quote": "USDT", "type": "SPOT",
     "tick": "0.01", "lot": "0.0001", "min_size": "0.0001", "max_size": "10000"},
    {"id": "SOL-USDT-SPOT", "base": "SOL", "quote": "USDT", "type": "SPOT",
     "tick": "0.001", "lot": "0.01", "min_size": "0.01", "max_size": "100000"},
    {"id": "XRP-USDT-SPOT", "base": "XRP", "quote": "USDT", "type": "SPOT",
     "tick": "0.0001", "lot": "1", "min_size": "1", "max_size": "10000000"},
    # ── Perpetuals ──
    {"id": "BTC-USDT-PERP", "base": "BTC", "quote": "USDT", "type": "PERPETUAL",
     "tick": "0.1", "lot": "0.001", "min_size": "0.001", "max_size": "500"},
    {"id": "ETH-USDT-PERP", "base": "ETH", "quote": "USDT", "type": "PERPETUAL",
     "tick": "0.01", "lot": "0.01", "min_size": "0.01", "max_size": "5000"},
    {"id": "SOL-USDT-PERP", "base": "SOL", "quote": "USDT", "type": "PERPETUAL",
     "tick": "0.001", "lot": "0.1", "min_size": "0.1", "max_size": "50000"},
    {"id": "BNB-USDT-PERP", "base": "BNB", "quote": "USDT", "type": "PERPETUAL",
     "tick": "0.01", "lot": "0.01", "min_size": "0.01", "max_size": "10000"},
    # ── Options ──
    {"id": "BTC-20260630-80000-C", "base": "BTC", "quote": "USDT", "type": "OPTION",
     "tick": "0.1", "lot": "0.001", "min_size": "0.001", "max_size": "100",
     "strike": "80000", "expiry": "2026-06-30", "option_type": "CALL"},
    {"id": "BTC-20260630-80000-P", "base": "BTC", "quote": "USDT", "type": "OPTION",
     "tick": "0.1", "lot": "0.001", "min_size": "0.001", "max_size": "100",
     "strike": "80000", "expiry": "2026-06-30", "option_type": "PUT"},
    {"id": "ETH-20260630-5000-C", "base": "ETH", "quote": "USDT", "type": "OPTION",
     "tick": "0.01", "lot": "0.01", "min_size": "0.01", "max_size": "1000",
     "strike": "5000", "expiry": "2026-06-30", "option_type": "CALL"},
    {"id": "ETH-20260630-5000-P", "base": "ETH", "quote": "USDT", "type": "OPTION",
     "tick": "0.01", "lot": "0.01", "min_size": "0.01", "max_size": "1000",
     "strike": "5000", "expiry": "2026-06-30", "option_type": "PUT"},
    {"id": "BTC-20260930-100000-C", "base": "BTC", "quote": "USDT", "type": "OPTION",
     "tick": "0.1", "lot": "0.001", "min_size": "0.001", "max_size": "100",
     "strike": "100000", "expiry": "2026-09-30", "option_type": "CALL"},
    {"id": "BTC-20260930-100000-P", "base": "BTC", "quote": "USDT", "type": "OPTION",
     "tick": "0.1", "lot": "0.001", "min_size": "0.001", "max_size": "100",
     "strike": "100000", "expiry": "2026-09-30", "option_type": "PUT"},
]


async def _fetch_and_seed_prices():
    """Fetch real prices from Binance and update fallback prices."""
    try:
        prices = await binance_client.fetch_prices()
        if prices:
            for iid in order_books:
                binance_price = binance_client.get_price_for_instrument(iid)
                if binance_price:
                    FALLBACK_PRICES[iid] = binance_price
                    mm_manager.update_price(iid, binance_price)
            logger.info(f"Fetched real prices from Binance: {len(prices)} symbols")
    except Exception as e:
        logger.warning(f"Failed to fetch Binance prices, using fallback: {e}")


async def _on_binance_price_update(instrument_id: str, price: Decimal, raw_data: dict):
    """Callback for real-time Binance price updates."""
    mm_manager.update_price(instrument_id, price)
    await market_data.broadcast_orderbook_update(instrument_id, {
        "type": "price_update",
        "source": "binance",
        "instrument_id": instrument_id,
        "price": str(price),
        "bid": raw_data.get("b", ""),
        "ask": raw_data.get("a", ""),
        "volume_24h": raw_data.get("v", ""),
        "change_pct": raw_data.get("P", ""),
    })


def _seed_data():
    """Seed instruments, risk params, and demo balances."""
    init_db()

    for inst in INSTRUMENTS:
        iid = inst["id"]
        order_books[iid] = OrderBook(instrument_id=iid)
        risk_engine.set_parameters(
            RiskParameters(
                instrument_id=iid,
                max_order_size=Decimal(inst["max_size"]),
                initial_margin_rate=(
                    Decimal("0.10") if "PERP" in iid
                    else Decimal("0.20") if inst["type"] == "OPTION"
                    else Decimal("1.0")
                ),
                maintenance_margin_rate=(
                    Decimal("0.05") if "PERP" in iid
                    else Decimal("0.10") if inst["type"] == "OPTION"
                    else Decimal("1.0")
                ),
                max_leverage=(
                    Decimal("20") if "PERP" in iid
                    else Decimal("5") if inst["type"] == "OPTION"
                    else Decimal("1")
                ),
            ),
            changed_by="system",
        )

        # Persist instrument to database
        try:
            with session_scope() as session:
                existing = session.query(InstrumentModel).filter_by(id=iid).first()
                if not existing:
                    session.add(InstrumentModel(
                        id=iid,
                        instrument_type=inst["type"],
                        base_asset=inst["base"],
                        quote_asset=inst["quote"],
                        tick_size=Decimal(inst["tick"]),
                        lot_size=Decimal(inst["lot"]),
                        min_order_size=Decimal(inst["min_size"]),
                        max_order_size=Decimal(inst["max_size"]),
                    ))
        except Exception as e:
            logger.warning(f"Could not save instrument {iid} to DB: {e}")

        # Seed some resting orders for demo liquidity
        _seed_book(iid)

        # Set up market maker for instruments with Binance data
        if iid in INSTRUMENT_TO_BINANCE:
            config = MarketMakerConfig(
                instrument_id=iid,
                base_spread_bps=Decimal("15"),
                num_levels=8,
                order_size=Decimal("0.1") if "BTC" in iid else Decimal("1.0"),
                max_position=Decimal("5") if "BTC" in iid else Decimal("50"),
                refresh_interval=10.0,
            )
            mm_manager.add_maker(config, order_books[iid])

    # Register demo user in IAM first to get the real user_id
    demo_user = iam_service.register_user("demo", "herald2026", "demo@herald.exchange")
    demo_user_id = demo_user["user_id"]

    # Save demo user to DB
    try:
        with session_scope() as session:
            existing = session.query(UserModel).filter_by(username="demo").first()
            if not existing:
                session.add(UserModel(
                    id=demo_user_id,
                    username="demo",
                    email="demo@herald.exchange",
                    password_hash=demo_user["password_hash"],
                ))
    except Exception as e:
        logger.warning(f"Could not save demo user to DB: {e}")

    # Seed demo user balances using the real user_id
    for asset in ["USDT", "BTC", "ETH", "SOL", "XRP"]:
        demo_amount = {
            "USDT": "1000000", "BTC": "10", "ETH": "100", "SOL": "5000", "XRP": "500000"
        }[asset]
        txn = LedgerTransaction(
            transaction_id=uuid4(),
            entries=(
                LedgerEntry(account_id="treasury", asset=asset,
                            amount=Decimal(demo_amount), direction=DebitCredit.CREDIT,
                            entry_type=EntryType.DEPOSIT),
                LedgerEntry(account_id=demo_user_id, asset=asset,
                            amount=Decimal(demo_amount), direction=DebitCredit.DEBIT,
                            entry_type=EntryType.DEPOSIT),
            ),
            entry_type=EntryType.DEPOSIT,
            idempotency_key=f"seed-{asset}",
        )
        ledger.append_transaction(txn)


# Global reservations tracker: {user_id: {asset: Decimal}}
_reservations: dict[str, dict[str, Decimal]] = {}


def _reserve_balance(user_id: str, asset: str, amount: Decimal):
    """Reserve funds for a pending order."""
    if user_id not in _reservations:
        _reservations[user_id] = {}
    current = _reservations[user_id].get(asset, Decimal("0"))
    _reservations[user_id][asset] = current + amount


def _release_reservation(user_id: str, asset: str, amount: Decimal):
    """Release reserved funds (on fill or cancel)."""
    if user_id not in _reservations:
        return
    current = _reservations[user_id].get(asset, Decimal("0"))
    _reservations[user_id][asset] = max(Decimal("0"), current - amount)


def _get_reserved(user_id: str, asset: str) -> Decimal:
    """Get the reserved amount for a user/asset."""
    return _reservations.get(user_id, {}).get(asset, Decimal("0"))


def _seed_book(iid: str):
    """Place initial resting orders to give the book some depth."""
    bp = FALLBACK_PRICES.get(iid, Decimal("100"))
    book = order_books[iid]
    spread_pct = Decimal("0.001")
    for i in range(1, 11):
        offset = bp * spread_pct * i
        ask_price = bp + offset
        bid_price = bp - offset
        qty = Decimal("1") / (Decimal(str(i)) * Decimal("0.5") + 1)
        now = datetime.utcnow()
        book.match_order(OrderEntry(
            order_id=uuid4(), account_id="market-maker", price=ask_price,
            quantity=qty, remaining=qty, side="SELL", timestamp=now, sequence=0,
        ))
        book.match_order(OrderEntry(
            order_id=uuid4(), account_id="market-maker", price=bid_price,
            quantity=qty, remaining=qty, side="BUY", timestamp=now, sequence=0,
        ))


@asynccontextmanager
async def lifespan(application: FastAPI):
    _seed_data()

    # Start Binance real-time feed
    try:
        await _fetch_and_seed_prices()
        binance_client.on_price_update(_on_binance_price_update)
        await binance_client.start_websocket()
        logger.info("Binance WebSocket feed started")
    except Exception as e:
        logger.warning(f"Binance feed failed to start (non-fatal): {e}")

    # Start market makers
    try:
        await mm_manager.start_all()
        logger.info("Market makers started")
    except Exception as e:
        logger.warning(f"Market makers failed to start (non-fatal): {e}")

    yield

    # Cleanup
    await mm_manager.stop_all()
    await binance_client.close()
    await chain_adapters.close()


app = FastAPI(
    title="Herald Crypto Exchange",
    version="0.2.0",
    description="Institutional-grade multi-product crypto exchange API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------

class PlaceOrderRequest(BaseModel):
    instrument_id: str
    side: str = Field(pattern="^(BUY|SELL)$")
    order_type: str = Field(default="LIMIT", pattern="^(LIMIT|MARKET)$")
    quantity: str
    price: Optional[str] = None
    time_in_force: str = "GTC"
    client_order_id: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    instrument_id: str
    side: str
    order_type: str
    quantity: str
    price: Optional[str]
    status: str
    fills: list[dict]
    remaining_quantity: str
    created_at: str


class CancelOrderRequest(BaseModel):
    order_id: str
    instrument_id: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str


class DepositRequest(BaseModel):
    asset: str
    amount: str


class WithdrawRequest(BaseModel):
    asset: str
    amount: str


class TransferRequest(BaseModel):
    from_wallet: str = "funding"
    to_wallet: str = "trading"
    asset: str
    amount: str


class FiatDepositRequest(BaseModel):
    amount: str
    currency: str = "USD"
    payment_method: str = "card"


class FiatWithdrawRequest(BaseModel):
    amount: str
    currency: str = "USD"
    payment_method: str = "bank_transfer"


# ---------------------------------------------------------------------------
# Auth endpoints (Agent 08 - IAM)
# ---------------------------------------------------------------------------

@app.post("/api/v1/auth/register")
async def register(req: RegisterRequest):
    user = iam_service.register_user(req.username, req.password, req.email)
    if user is None:
        raise HTTPException(400, "Username already exists")

    try:
        with session_scope() as session:
            existing = session.query(UserModel).filter_by(username=req.username).first()
            if not existing:
                session.add(UserModel(
                    id=user["user_id"],
                    username=req.username,
                    email=req.email,
                    password_hash=user["password_hash"],
                ))
    except Exception as e:
        logger.warning(f"Could not save user to DB: {e}")

    # Seed initial balance
    txn = LedgerTransaction(
        transaction_id=uuid4(),
        entries=(
            LedgerEntry(account_id="treasury", asset="USDT",
                        amount=Decimal("100000"), direction=DebitCredit.CREDIT,
                        entry_type=EntryType.DEPOSIT),
            LedgerEntry(account_id=user["user_id"], asset="USDT",
                        amount=Decimal("100000"), direction=DebitCredit.DEBIT,
                        entry_type=EntryType.DEPOSIT),
        ),
        entry_type=EntryType.DEPOSIT,
        idempotency_key=f"register-{user['user_id']}",
    )
    ledger.append_transaction(txn)
    token = create_access_token({"sub": user["user_id"], "username": req.username})
    return {"token": token, "user_id": user["user_id"], "username": req.username}


@app.post("/api/v1/auth/login")
async def login(req: LoginRequest):
    user = iam_service.authenticate(req.username, req.password)
    if user is None:
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user["user_id"], "username": user["username"]})
    return {
        "access_token": token,
        "token": token,
        "token_type": "bearer",
        "user_id": user["user_id"],
        "username": user["username"],
    }


@app.get("/api/v1/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return {"user_id": user["sub"], "username": user.get("username", "")}


# ---------------------------------------------------------------------------
# Market data endpoints (Agent 06)
# ---------------------------------------------------------------------------

@app.get("/api/v1/instruments")
async def list_instruments():
    result = []
    for inst in INSTRUMENTS:
        iid = inst["id"]
        book = order_books.get(iid)
        ticker = {
            "instrument_id": iid,
            "id": iid,
            "base": inst["base"],
            "quote": inst["quote"],
            "base_asset": inst["base"],
            "quote_asset": inst["quote"],
            "instrument_type": inst["type"],
            "product_type": inst["type"],
            "tick_size": inst["tick"],
            "lot_size": inst["lot"],
            "best_bid": str(book.best_bid) if book and book.best_bid else None,
            "best_ask": str(book.best_ask) if book and book.best_ask else None,
            "spread": str(book.spread) if book and book.spread else None,
        }
        if inst["type"] == "OPTION":
            ticker["strike"] = inst.get("strike")
            ticker["expiry"] = inst.get("expiry")
            ticker["option_type"] = inst.get("option_type")
        binance_price = binance_client.get_price_for_instrument(iid)
        if binance_price:
            ticker["binance_price"] = str(binance_price)
        result.append(ticker)
    return result


@app.get("/api/v1/market/{instrument_id}/orderbook")
async def get_orderbook(instrument_id: str, depth: int = Query(default=20, le=100)):
    book = order_books.get(instrument_id)
    if book is None:
        raise HTTPException(404, f"Instrument {instrument_id} not found")
    bids = []
    for price in sorted(book._bids.keys(), reverse=True)[:depth]:
        level = book._bids[price]
        bids.append({"price": str(price), "quantity": str(level.total_quantity),
                      "orders": len(level.orders)})
    asks = []
    for price in sorted(book._asks.keys())[:depth]:
        level = book._asks[price]
        asks.append({"price": str(price), "quantity": str(level.total_quantity),
                      "orders": len(level.orders)})
    return {
        "instrument_id": instrument_id,
        "bids": bids,
        "asks": asks,
        "best_bid": str(book.best_bid) if book.best_bid else None,
        "best_ask": str(book.best_ask) if book.best_ask else None,
        "spread": str(book.spread) if book.spread else None,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/orderbook/{instrument_id}")
async def get_orderbook_alt(instrument_id: str, depth: int = Query(default=20, le=100)):
    book = order_books.get(instrument_id)
    if book is None:
        raise HTTPException(404, f"Instrument {instrument_id} not found")
    bids = []
    for price in sorted(book._bids.keys(), reverse=True)[:depth]:
        level = book._bids[price]
        bids.append([str(price), str(level.total_quantity)])
    asks = []
    for price in sorted(book._asks.keys())[:depth]:
        level = book._asks[price]
        asks.append([str(price), str(level.total_quantity)])
    return {"bids": bids, "asks": asks}


@app.get("/api/v1/market/{instrument_id}/trades")
async def get_recent_trades(instrument_id: str, limit: int = Query(default=50, le=200)):
    trades = market_data.get_recent_trades(instrument_id, limit)
    return {"instrument_id": instrument_id, "trades": trades}


@app.get("/api/v1/trades/{instrument_id}")
async def get_trades_alt(instrument_id: str, limit: int = Query(default=50, le=200)):
    return market_data.get_recent_trades(instrument_id, limit)


@app.get("/api/v1/market/{instrument_id}/ticker")
async def get_ticker(instrument_id: str):
    book = order_books.get(instrument_id)
    if book is None:
        raise HTTPException(404, f"Instrument {instrument_id} not found")
    stats = market_data.get_ticker_stats(instrument_id)
    binance_price = binance_client.get_price_for_instrument(instrument_id)
    return {
        "instrument_id": instrument_id,
        "best_bid": str(book.best_bid) if book.best_bid else None,
        "best_ask": str(book.best_ask) if book.best_ask else None,
        "last_price": stats.get("last_price"),
        "volume_24h": stats.get("volume_24h", "0"),
        "high_24h": stats.get("high_24h"),
        "low_24h": stats.get("low_24h"),
        "change_24h_pct": stats.get("change_24h_pct", "0"),
        "binance_price": str(binance_price) if binance_price else None,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/ticker/{instrument_id}")
async def get_ticker_alt(instrument_id: str):
    return await get_ticker(instrument_id)


# ---------------------------------------------------------------------------
# Trading endpoints (Agents 02, 05)
# ---------------------------------------------------------------------------

@app.post("/api/v1/orders", response_model=OrderResponse)
async def place_order(req: PlaceOrderRequest, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    book = order_books.get(req.instrument_id)
    if book is None:
        raise HTTPException(404, f"Instrument {req.instrument_id} not found")

    qty = Decimal(req.quantity)
    price = Decimal(req.price) if req.price else None

    if req.order_type == "LIMIT" and price is None:
        raise HTTPException(400, "Limit orders require a price")

    # Use mid-price for market orders
    if req.order_type == "MARKET" and price is None:
        if book.best_ask and req.side == "BUY":
            price = book.best_ask
        elif book.best_bid and req.side == "SELL":
            price = book.best_bid
        else:
            raise HTTPException(400, "No liquidity for market order")

    # Pre-trade risk check (Agent 04)
    risk_result = risk_engine.check_pre_trade(RiskCheckRequest(
        account_id=user_id,
        instrument_id=req.instrument_id,
        side=req.side,
        order_type=req.order_type,
        quantity=qty,
        price=price,
        available_balance=ledger.get_balance(user_id, "USDT"),
        reference_price=price,
    ))
    if risk_result.name != "PASSED":
        raise HTTPException(400, f"Risk check failed: {risk_result.name}")

    # Journal command (HC-002)
    oid = uuid4()
    journal.append(CommandType.PLACE_ORDER, {
        "order_id": str(oid), "instrument_id": req.instrument_id,
        "side": req.side, "quantity": str(qty), "price": str(price),
        "account_id": user_id,
    })

    # Match
    now = datetime.utcnow()
    entry = OrderEntry(
        order_id=oid, account_id=user_id, price=price, quantity=qty,
        remaining=qty, side=req.side, timestamp=now, sequence=0,
    )
    result = book.match_order(entry)

    # Process fills -> ledger entries
    fill_dicts = []
    for fill in result.fills:
        _settle_fill(fill, req.instrument_id)
        market_data.record_trade(req.instrument_id, fill)
        fill_dicts.append({
            "fill_id": str(fill.fill_id),
            "price": str(fill.price),
            "quantity": str(fill.quantity),
            "maker_side": fill.maker_side,
            "timestamp": fill.timestamp.isoformat(),
        })

    # Reserve balance for any remaining unfilled quantity
    inst = next((i for i in INSTRUMENTS if i["id"] == req.instrument_id), None)
    remaining = result.remaining_quantity
    if remaining > 0 and price and inst:
        if req.side == "BUY":
            reserve_asset = inst["quote"]
            reserve_amount = remaining * price
        else:
            reserve_asset = inst["base"]
            reserve_amount = remaining
        _reserve_balance(user_id, reserve_asset, reserve_amount)

    # Release reservation for filled quantity
    for fill in result.fills:
        if req.side == "BUY":
            quote_asset = inst["quote"] if inst else "USDT"
            _release_reservation(user_id, quote_asset, fill.quantity * fill.price)
        else:
            _release_reservation(user_id, inst["base"] if inst else "BTC", fill.quantity)

    # Persist order to database
    try:
        with session_scope() as session:
            session.add(OrderModel(
                id=str(oid),
                client_order_id=req.client_order_id,
                user_id=user_id,
                instrument_id=req.instrument_id,
                side=req.side,
                order_type=req.order_type,
                status=result.status,
                quantity=qty,
                filled_quantity=qty - result.remaining_quantity,
                price=price,
                time_in_force=req.time_in_force,
            ))
    except Exception as e:
        logger.warning(f"Could not save order to DB: {e}")

    # Broadcast to WS subscribers
    await market_data.broadcast_trade(req.instrument_id, fill_dicts)

    return OrderResponse(
        order_id=str(oid),
        instrument_id=req.instrument_id,
        side=req.side,
        order_type=req.order_type,
        quantity=str(qty),
        price=str(price) if price else None,
        status=result.status,
        fills=fill_dicts,
        remaining_quantity=str(result.remaining_quantity),
        created_at=now.isoformat(),
    )


@app.delete("/api/v1/orders/{order_id}")
async def cancel_order(order_id: str, instrument_id: str = Query(...),
                       user: dict = Depends(get_current_user)):
    book = order_books.get(instrument_id)
    if book is None:
        raise HTTPException(404, "Instrument not found")
    journal.append(CommandType.CANCEL_ORDER, {
        "order_id": order_id, "instrument_id": instrument_id,
    })
    cancelled = book.cancel_order(UUID(order_id))
    if cancelled is None:
        raise HTTPException(404, "Order not found or already filled")
    return {"order_id": order_id, "status": "CANCELLED"}


@app.get("/api/v1/orders")
async def get_orders(user: dict = Depends(get_current_user)):
    try:
        with session_scope() as session:
            orders = (
                session.query(OrderModel)
                .filter_by(user_id=user["sub"])
                .order_by(OrderModel.created_at.desc())
                .limit(100)
                .all()
            )
            return [
                {
                    "order_id": o.id,
                    "instrument_id": o.instrument_id,
                    "side": o.side,
                    "order_type": o.order_type,
                    "status": o.status,
                    "quantity": str(o.quantity),
                    "price": str(o.price) if o.price else None,
                    "filled_quantity": str(o.filled_quantity),
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                }
                for o in orders
            ]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Account / Wallet endpoints (Agents 03, 10)
# ---------------------------------------------------------------------------

@app.get("/api/v1/account/balances")
async def get_balances(user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    assets = ["USDT", "BTC", "ETH", "SOL", "XRP", "BNB"]
    balances = {}
    for asset in assets:
        bal = ledger.get_balance(user_id, asset)
        reserved = _get_reserved(user_id, asset)
        if bal != 0 or reserved != 0:
            available = bal - reserved
            balances[asset] = {
                "available": str(available),
                "reserved": str(reserved),
                "total": str(bal),
            }
    return {"balances": balances}


@app.post("/api/v1/account/deposit")
async def deposit(req: DepositRequest, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    amount = Decimal(req.amount)
    if amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    txn = LedgerTransaction(
        transaction_id=uuid4(),
        entries=(
            LedgerEntry(account_id="treasury", asset=req.asset,
                        amount=amount, direction=DebitCredit.CREDIT,
                        entry_type=EntryType.DEPOSIT),
            LedgerEntry(account_id=user_id, asset=req.asset,
                        amount=amount, direction=DebitCredit.DEBIT,
                        entry_type=EntryType.DEPOSIT),
        ),
        entry_type=EntryType.DEPOSIT,
        idempotency_key=f"deposit-{user_id}-{uuid4()}",
    )
    ledger.append_transaction(txn)
    return {"status": "confirmed", "asset": req.asset, "amount": str(amount),
            "new_balance": str(ledger.get_balance(user_id, req.asset))}


@app.post("/api/v1/account/withdraw")
async def withdraw(req: WithdrawRequest, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    amount = Decimal(req.amount)
    balance = ledger.get_balance(user_id, req.asset)
    if amount > balance:
        raise HTTPException(400, "Insufficient balance")
    txn = LedgerTransaction(
        transaction_id=uuid4(),
        entries=(
            LedgerEntry(account_id=user_id, asset=req.asset,
                        amount=amount, direction=DebitCredit.CREDIT,
                        entry_type=EntryType.WITHDRAWAL),
            LedgerEntry(account_id="treasury", asset=req.asset,
                        amount=amount, direction=DebitCredit.DEBIT,
                        entry_type=EntryType.WITHDRAWAL),
        ),
        entry_type=EntryType.WITHDRAWAL,
        idempotency_key=f"withdraw-{user_id}-{uuid4()}",
    )
    ledger.append_transaction(txn)
    return {"status": "confirmed", "asset": req.asset, "amount": str(amount),
            "new_balance": str(ledger.get_balance(user_id, req.asset))}


@app.get("/api/v1/account/transactions")
async def get_transactions(user: dict = Depends(get_current_user),
                           limit: int = Query(default=50, le=200)):
    user_id = user["sub"]
    entries = ledger.get_entries_for_account(user_id)
    result = []
    for e in entries[-limit:]:
        result.append({
            "entry_id": str(e.entry_id),
            "asset": e.asset,
            "amount": str(e.amount),
            "direction": e.direction.name,
            "type": e.entry_type.name,
            "timestamp": e.timestamp.isoformat(),
        })
    return {"transactions": list(reversed(result))}


# ---------------------------------------------------------------------------
# Risk endpoints (Agent 04)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Blockchain / Custody endpoints (Agents 10, 11)
# ---------------------------------------------------------------------------

@app.get("/api/v1/blockchain/balance/{asset}/{address}")
async def blockchain_balance(asset: str, address: str):
    adapter = chain_adapters.get_adapter(asset.upper())
    if adapter is None:
        raise HTTPException(400, f"Unsupported chain: {asset}")
    balance = await adapter.get_balance(address)
    if balance is None:
        raise HTTPException(502, "Failed to fetch balance from blockchain")
    return {
        "address": balance.address,
        "asset": balance.asset,
        "balance": str(balance.balance),
        "last_updated": balance.last_updated.isoformat(),
    }


@app.get("/api/v1/blockchain/tx/{asset}/{tx_hash}")
async def blockchain_transaction(asset: str, tx_hash: str):
    adapter = chain_adapters.get_adapter(asset.upper())
    if adapter is None:
        raise HTTPException(400, f"Unsupported chain: {asset}")
    tx = await adapter.get_transaction(tx_hash)
    if tx is None:
        raise HTTPException(404, "Transaction not found")
    return {
        "tx_hash": tx.tx_hash,
        "from": tx.from_address,
        "to": tx.to_address,
        "amount": str(tx.amount),
        "asset": tx.asset,
        "status": tx.status,
        "block_number": tx.block_number,
    }


@app.get("/api/v1/blockchain/block-heights")
async def blockchain_heights():
    heights = await chain_adapters.get_all_block_heights()
    return {asset: height for asset, height in heights.items()}


@app.get("/api/v1/blockchain/fee/{asset}")
async def blockchain_fee(asset: str):
    adapter = chain_adapters.get_adapter(asset.upper())
    if adapter is None:
        raise HTTPException(400, f"Unsupported chain: {asset}")
    fee = await adapter.estimate_fee()
    return {"asset": asset.upper(), "estimated_fee": str(fee) if fee else None}


# ---------------------------------------------------------------------------
# Fiat Payment Gateway endpoints (Agent 13)
# ---------------------------------------------------------------------------

@app.post("/api/v1/fiat/deposit")
async def fiat_deposit(req: FiatDepositRequest, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    amount = Decimal(req.amount)
    if amount <= 0:
        raise HTTPException(400, "Amount must be positive")

    method_map = {
        "card": GWPaymentMethod.CARD,
        "bank_transfer": GWPaymentMethod.BANK_TRANSFER,
        "wire": GWPaymentMethod.WIRE,
    }
    method = method_map.get(req.payment_method, GWPaymentMethod.CARD)

    intent = payment_gateway.create_payment_intent(
        user_id=user_id, amount=amount, currency=req.currency,
        direction="deposit", payment_method=method,
    )

    confirmed = payment_gateway.confirm_payment(intent.intent_id)
    if confirmed and confirmed.status.value == "succeeded":
        txn = LedgerTransaction(
            transaction_id=uuid4(),
            entries=(
                LedgerEntry(account_id="treasury", asset="USDT",
                            amount=intent.crypto_amount, direction=DebitCredit.CREDIT,
                            entry_type=EntryType.DEPOSIT),
                LedgerEntry(account_id=user_id, asset="USDT",
                            amount=intent.crypto_amount, direction=DebitCredit.DEBIT,
                            entry_type=EntryType.DEPOSIT),
            ),
            entry_type=EntryType.DEPOSIT,
            idempotency_key=f"fiat-{intent.intent_id}",
        )
        ledger.append_transaction(txn)

    return {
        "intent_id": intent.intent_id,
        "status": confirmed.status.value if confirmed else "created",
        "amount": str(intent.amount),
        "currency": intent.currency,
        "crypto_amount": str(intent.crypto_amount),
        "fee": str(intent.fee),
        "client_secret": intent.client_secret,
    }


@app.post("/api/v1/fiat/withdraw")
async def fiat_withdraw(req: FiatWithdrawRequest, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    amount = Decimal(req.amount)
    usdt_balance = ledger.get_balance(user_id, "USDT")
    if amount > usdt_balance:
        raise HTTPException(400, "Insufficient USDT balance")

    method_map = {
        "bank_transfer": GWPaymentMethod.BANK_TRANSFER,
        "wire": GWPaymentMethod.WIRE,
    }
    method = method_map.get(req.payment_method, GWPaymentMethod.BANK_TRANSFER)

    intent = payment_gateway.create_payment_intent(
        user_id=user_id, amount=amount, currency=req.currency,
        direction="withdrawal", payment_method=method,
    )

    txn = LedgerTransaction(
        transaction_id=uuid4(),
        entries=(
            LedgerEntry(account_id=user_id, asset="USDT",
                        amount=amount, direction=DebitCredit.CREDIT,
                        entry_type=EntryType.WITHDRAWAL),
            LedgerEntry(account_id="treasury", asset="USDT",
                        amount=amount, direction=DebitCredit.DEBIT,
                        entry_type=EntryType.WITHDRAWAL),
        ),
        entry_type=EntryType.WITHDRAWAL,
        idempotency_key=f"fiat-wd-{intent.intent_id}",
    )
    ledger.append_transaction(txn)

    return {
        "intent_id": intent.intent_id,
        "status": "processing",
        "amount": str(intent.amount),
        "currency": intent.currency,
        "fee": str(intent.fee),
    }


@app.get("/api/v1/fiat/payments")
async def fiat_payments(user: dict = Depends(get_current_user)):
    payments = payment_gateway.get_user_payments(user["sub"])
    return [
        {
            "intent_id": p.intent_id,
            "direction": p.direction,
            "amount": str(p.amount),
            "currency": p.currency,
            "crypto_amount": str(p.crypto_amount),
            "status": p.status.value,
            "fee": str(p.fee),
            "created_at": p.created_at.isoformat(),
        }
        for p in payments
    ]


# ---------------------------------------------------------------------------
# Market Maker status endpoint
# ---------------------------------------------------------------------------

@app.get("/api/v1/market-maker/status")
async def market_maker_status():
    return {"market_makers": mm_manager.get_status()}


# ---------------------------------------------------------------------------
# Risk endpoints (Agent 04)
# ---------------------------------------------------------------------------

@app.get("/api/v1/risk/parameters/{instrument_id}")
async def get_risk_params(instrument_id: str):
    params = risk_engine._parameters.get(instrument_id)
    if params is None:
        raise HTTPException(404, "Instrument not found")
    return {
        "instrument_id": instrument_id,
        "max_order_size": str(params.max_order_size),
        "max_position_size": str(params.max_position_size),
        "price_band_pct": str(params.price_band_pct),
        "initial_margin_rate": str(params.initial_margin_rate),
        "maintenance_margin_rate": str(params.maintenance_margin_rate),
        "max_leverage": str(params.max_leverage),
    }


# ---------------------------------------------------------------------------
# System / health endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "instruments": len(order_books),
        "ledger_entries": ledger.entry_count,
        "journal_entries": journal.entry_count,
        "binance_connected": binance_client._running,
        "market_makers_active": len(mm_manager._makers),
    }


@app.get("/api/v1/system/info")
async def system_info():
    return {
        "exchange_name": "Herald Crypto Exchange",
        "version": "0.2.0",
        "instruments": len(order_books),
        "features": [
            "spot_trading", "perpetuals", "options",
            "real_market_data", "market_making",
            "blockchain_adapters", "fiat_gateway",
            "persistent_database", "websocket_feeds",
        ],
    }


@app.get("/api/v1/system/stats")
async def system_stats():
    return {
        "instruments": len(order_books),
        "ledger_entries": ledger.entry_count,
        "ledger_transactions": ledger.transaction_count,
        "journal_entries": journal.entry_count,
        "journal_sequence": journal.current_sequence,
        "registered_users": len(iam_service._users),
        "binance_connected": binance_client._running,
        "market_makers": len(mm_manager._makers),
        "blockchain_adapters": ["ETH", "BTC"],
        "timestamp": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# WebSocket endpoint for real-time market data (Agent 06)
# ---------------------------------------------------------------------------

@app.websocket("/ws/market/{instrument_id}")
async def websocket_market(websocket: WebSocket, instrument_id: str):
    if instrument_id not in order_books:
        await websocket.close(code=4004, reason="Instrument not found")
        return
    await websocket.accept()
    market_data.add_subscriber(instrument_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Clients can send ping/subscribe messages
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        market_data.remove_subscriber(instrument_id, websocket)


# ---------------------------------------------------------------------------
# Trade settlement helper
# ---------------------------------------------------------------------------

def _settle_fill(fill: Fill, instrument_id: str):
    """Create ledger entries for a trade fill."""
    inst = next((i for i in INSTRUMENTS if i["id"] == instrument_id), None)
    if inst is None:
        return
    quote = inst["quote"]
    base = inst["base"]
    notional = fill.price * fill.quantity
    fee_rate = Decimal("0.001")  # 10bps
    maker_fee = notional * fee_rate * Decimal("0.5")  # 5bps maker
    taker_fee = notional * fee_rate  # 10bps taker

    if fill.maker_side == "BUY":
        # Maker buys base, taker sells base
        maker_buyer_id = fill.maker_account_id
        taker_seller_id = fill.taker_account_id
    else:
        maker_buyer_id = fill.taker_account_id
        taker_seller_id = fill.maker_account_id

    # Base asset: seller -> buyer
    # Quote asset: buyer -> seller
    entries = [
        LedgerEntry(account_id=taker_seller_id, asset=base,
                    amount=fill.quantity, direction=DebitCredit.CREDIT,
                    entry_type=EntryType.TRADE_SETTLEMENT),
        LedgerEntry(account_id=maker_buyer_id, asset=base,
                    amount=fill.quantity, direction=DebitCredit.DEBIT,
                    entry_type=EntryType.TRADE_SETTLEMENT),
        LedgerEntry(account_id=maker_buyer_id, asset=quote,
                    amount=notional, direction=DebitCredit.CREDIT,
                    entry_type=EntryType.TRADE_SETTLEMENT),
        LedgerEntry(account_id=taker_seller_id, asset=quote,
                    amount=notional, direction=DebitCredit.DEBIT,
                    entry_type=EntryType.TRADE_SETTLEMENT),
        # Fees
        LedgerEntry(account_id=fill.maker_account_id, asset=quote,
                    amount=maker_fee, direction=DebitCredit.CREDIT,
                    entry_type=EntryType.FEE),
        LedgerEntry(account_id="fee-collection", asset=quote,
                    amount=maker_fee, direction=DebitCredit.DEBIT,
                    entry_type=EntryType.FEE),
        LedgerEntry(account_id=fill.taker_account_id, asset=quote,
                    amount=taker_fee, direction=DebitCredit.CREDIT,
                    entry_type=EntryType.FEE),
        LedgerEntry(account_id="fee-collection", asset=quote,
                    amount=taker_fee, direction=DebitCredit.DEBIT,
                    entry_type=EntryType.FEE),
    ]

    txn = LedgerTransaction(
        transaction_id=uuid4(),
        entries=tuple(entries),
        entry_type=EntryType.TRADE_SETTLEMENT,
        reference_id=str(fill.fill_id),
        idempotency_key=f"fill-{fill.fill_id}",
    )
    try:
        ledger.append_transaction(txn)
    except ValueError:
        pass  # Idempotency duplicate
