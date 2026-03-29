"""
Herald Crypto Exchange - Database Models (Agent 09)

SQLAlchemy ORM models for persistent storage.
Supports PostgreSQL in production, SQLite for development.
"""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────

class AccountTypeDB(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    INSTITUTIONAL = "INSTITUTIONAL"
    MARKET_MAKER = "MARKET_MAKER"
    TREASURY = "TREASURY"


class KycLevelDB(str, enum.Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    INSTITUTIONAL = "INSTITUTIONAL"


class OrderSideDB(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderTypeDB(str, enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    STOP_MARKET = "STOP_MARKET"
    TRAILING_STOP = "TRAILING_STOP"
    ICEBERG = "ICEBERG"


class OrderStatusDB(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class InstrumentTypeDB(str, enum.Enum):
    SPOT = "SPOT"
    PERPETUAL = "PERPETUAL"
    FUTURE = "FUTURE"
    OPTION = "OPTION"


# ── Models ────────────────────────────────────────────────────────────

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    account_type: Mapped[str] = mapped_column(
        SAEnum(AccountTypeDB), default=AccountTypeDB.INDIVIDUAL,
    )
    kyc_level: Mapped[str] = mapped_column(
        SAEnum(KycLevelDB), default=KycLevelDB.NONE,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    country_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(),
                                                  onupdate=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_users_created", "created_at"),
    )


class InstrumentModel(Base):
    __tablename__ = "instruments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    instrument_type: Mapped[str] = mapped_column(SAEnum(InstrumentTypeDB))
    base_asset: Mapped[str] = mapped_column(String(16), index=True)
    quote_asset: Mapped[str] = mapped_column(String(16), index=True)
    tick_size: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    lot_size: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    min_order_size: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    max_order_size: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    maker_fee_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("0.0005"))
    taker_fee_rate: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("0.001"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trading_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_order_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    instrument_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("instruments.id"), index=True,
    )
    side: Mapped[str] = mapped_column(SAEnum(OrderSideDB))
    order_type: Mapped[str] = mapped_column(SAEnum(OrderTypeDB))
    status: Mapped[str] = mapped_column(SAEnum(OrderStatusDB), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    filled_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 12), default=Decimal("0"))
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 12), nullable=True)
    stop_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 12), nullable=True)
    time_in_force: Mapped[str] = mapped_column(String(8), default="GTC")
    average_fill_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 12), nullable=True)
    total_fee: Mapped[Decimal] = mapped_column(Numeric(24, 12), default=Decimal("0"))
    reject_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(),
                                                  onupdate=func.now())
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expiry: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_orders_user_status", "user_id", "status"),
        Index("ix_orders_instrument_status", "instrument_id", "status"),
        Index("ix_orders_created", "created_at"),
    )


class TradeModel(Base):
    __tablename__ = "trades"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    instrument_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("instruments.id"), index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    maker_order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id"))
    taker_order_id: Mapped[str] = mapped_column(String(64), ForeignKey("orders.id"))
    maker_user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    taker_user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    maker_side: Mapped[str] = mapped_column(SAEnum(OrderSideDB))
    maker_fee: Mapped[Decimal] = mapped_column(Numeric(24, 12), default=Decimal("0"))
    taker_fee: Mapped[Decimal] = mapped_column(Numeric(24, 12), default=Decimal("0"))
    sequence_number: Mapped[int] = mapped_column(BigInteger, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_trades_instrument_time", "instrument_id", "timestamp"),
        Index("ix_trades_sequence", "sequence_number"),
    )


class LedgerEntryModel(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(64), index=True)
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    asset: Mapped[str] = mapped_column(String(16), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    direction: Mapped[str] = mapped_column(String(8))  # DEBIT or CREDIT
    entry_type: Mapped[str] = mapped_column(String(32))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    sequence_number: Mapped[int] = mapped_column(BigInteger, index=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_ledger_account_asset", "account_id", "asset"),
        Index("ix_ledger_transaction", "transaction_id"),
    )


class BalanceSnapshotModel(Base):
    __tablename__ = "balance_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    asset: Mapped[str] = mapped_column(String(16))
    available: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    reserved: Mapped[Decimal] = mapped_column(Numeric(24, 12), default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(24, 12))
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_balance_account_asset", "account_id", "asset"),
    )


class WalletModel(Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    asset: Mapped[str] = mapped_column(String(16))
    wallet_type: Mapped[str] = mapped_column(String(16), default="HOT")
    address: Mapped[str] = mapped_column(String(128), unique=True)
    label: Mapped[str] = mapped_column(String(128), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AuditLogModel(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(32))
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_audit_event_time", "event_type", "timestamp"),
    )


# ── Database setup ────────────────────────────────────────────────────

def create_database(url: str = "sqlite:///herald_exchange.db") -> sessionmaker:
    """Create database engine and tables."""
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def get_dev_session() -> Session:
    """Get a development database session (SQLite)."""
    session_factory = create_database()
    return session_factory()
