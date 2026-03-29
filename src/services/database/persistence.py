"""
Herald Crypto Exchange - Database Persistence Layer

Wires SQLAlchemy models to the gateway services.
Provides session management and CRUD operations.
"""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.services.database.models import (
    Base,
    InstrumentModel,
    LedgerEntryModel,
    OrderModel,
    TradeModel,
    UserModel,
)

logger = logging.getLogger(__name__)

# Use /data/herald.db for production (Fly.io volume), else local
DB_PATH = os.environ.get("HERALD_DB_PATH", "herald_exchange.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"


def get_engine(url: str = DATABASE_URL):
    return create_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


_engine = None
_SessionLocal = None


def init_db(url: str = DATABASE_URL):
    """Initialize database engine and create tables."""
    global _engine, _SessionLocal
    _engine = get_engine(url)
    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    logger.info(f"Database initialized: {url}")
    return _SessionLocal


def get_session() -> Session:
    """Get a new database session."""
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class UserRepository:
    """Database operations for users."""

    @staticmethod
    def create_user(
        user_id: str,
        username: str,
        email: str,
        password_hash: str,
    ) -> UserModel:
        with session_scope() as session:
            existing = session.query(UserModel).filter_by(username=username).first()
            if existing:
                return existing
            user = UserModel(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
            )
            session.add(user)
            session.flush()
            return user

    @staticmethod
    def get_by_username(username: str) -> Optional[UserModel]:
        with session_scope() as session:
            return session.query(UserModel).filter_by(username=username).first()

    @staticmethod
    def get_by_id(user_id: str) -> Optional[UserModel]:
        with session_scope() as session:
            return session.query(UserModel).filter_by(id=user_id).first()


class OrderRepository:
    """Database operations for orders."""

    @staticmethod
    def save_order(order_data: dict) -> OrderModel:
        with session_scope() as session:
            order = OrderModel(**order_data)
            session.merge(order)
            return order

    @staticmethod
    def update_status(order_id: str, status: str, **kwargs) -> Optional[OrderModel]:
        with session_scope() as session:
            order = session.query(OrderModel).filter_by(id=order_id).first()
            if order:
                order.status = status
                for k, v in kwargs.items():
                    setattr(order, k, v)
                order.updated_at = datetime.utcnow()
            return order

    @staticmethod
    def get_user_orders(user_id: str, limit: int = 100) -> list[OrderModel]:
        with session_scope() as session:
            return (
                session.query(OrderModel)
                .filter_by(user_id=user_id)
                .order_by(OrderModel.created_at.desc())
                .limit(limit)
                .all()
            )


class TradeRepository:
    """Database operations for trades."""

    @staticmethod
    def save_trade(trade_data: dict) -> TradeModel:
        with session_scope() as session:
            trade = TradeModel(**trade_data)
            session.merge(trade)
            return trade

    @staticmethod
    def get_instrument_trades(
        instrument_id: str, limit: int = 50
    ) -> list[TradeModel]:
        with session_scope() as session:
            return (
                session.query(TradeModel)
                .filter_by(instrument_id=instrument_id)
                .order_by(TradeModel.executed_at.desc())
                .limit(limit)
                .all()
            )


class LedgerRepository:
    """Database operations for ledger entries."""

    @staticmethod
    def save_entry(entry_data: dict) -> LedgerEntryModel:
        with session_scope() as session:
            entry = LedgerEntryModel(**entry_data)
            session.add(entry)
            return entry

    @staticmethod
    def get_balance(account_id: str, asset: str) -> Decimal:
        with session_scope() as session:
            entries = (
                session.query(LedgerEntryModel)
                .filter_by(account_id=account_id, asset=asset)
                .all()
            )
            balance = Decimal("0")
            for e in entries:
                if e.direction == "DEBIT":
                    balance += e.amount
                else:
                    balance -= e.amount
            return balance

    @staticmethod
    def get_account_entries(account_id: str) -> list[LedgerEntryModel]:
        with session_scope() as session:
            return (
                session.query(LedgerEntryModel)
                .filter_by(account_id=account_id)
                .order_by(LedgerEntryModel.created_at.desc())
                .all()
            )


class InstrumentRepository:
    """Database operations for instruments."""

    @staticmethod
    def save_instrument(data: dict) -> InstrumentModel:
        with session_scope() as session:
            inst = session.query(InstrumentModel).filter_by(id=data["id"]).first()
            if inst:
                return inst
            inst = InstrumentModel(**data)
            session.add(inst)
            return inst

    @staticmethod
    def get_all() -> list[InstrumentModel]:
        with session_scope() as session:
            return session.query(InstrumentModel).all()
