"""
Herald Crypto Exchange - Core Domain Entities

Primary domain entities representing the core business objects.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from .types import (
    AccountId,
    AccountType,
    AssetId,
    InstrumentId,
    InstrumentType,
    KycLevel,
    MarginType,
    Money,
    OptionType,
    OrderId,
    OrderStatus,
    OrderType,
    Price,
    Quantity,
    Side,
    TimeInForce,
    TradeId,
)


@dataclass
class Account:
    """User or system account in the exchange."""
    account_id: AccountId
    account_type: AccountType
    owner_id: UUID
    kyc_level: KycLevel = KycLevel.NONE
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    parent_account_id: Optional[AccountId] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Instrument:
    """Tradeable instrument definition."""
    instrument_id: InstrumentId
    instrument_type: InstrumentType
    base_asset: AssetId
    quote_asset: AssetId
    tick_size: Decimal
    lot_size: Decimal
    min_order_size: Decimal
    max_order_size: Decimal
    is_active: bool = True
    expiry: Optional[datetime] = None
    strike_price: Optional[Decimal] = None
    option_type: Optional[OptionType] = None
    underlying_instrument: Optional[InstrumentId] = None


@dataclass
class Order:
    """An order submitted to the matching engine."""
    order_id: OrderId
    account_id: AccountId
    instrument_id: InstrumentId
    side: Side
    order_type: OrderType
    quantity: Quantity
    filled_quantity: Quantity = field(default_factory=lambda: Quantity(Decimal("0")))
    price: Optional[Price] = None
    stop_price: Optional[Price] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    client_order_id: Optional[str] = None
    self_trade_prevention: bool = True

    @property
    def remaining_quantity(self) -> Quantity:
        return Quantity(self.quantity.value - self.filled_quantity.value)

    @property
    def is_complete(self) -> bool:
        return self.status in (
            OrderStatus.FILLED, OrderStatus.CANCELLED,
            OrderStatus.REJECTED, OrderStatus.EXPIRED,
        )


@dataclass
class Trade:
    """A matched trade between two orders."""
    trade_id: TradeId
    instrument_id: InstrumentId
    price: Price
    quantity: Quantity
    maker_order_id: OrderId
    taker_order_id: OrderId
    maker_account_id: AccountId
    taker_account_id: AccountId
    maker_side: Side
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence_number: int = 0
    maker_fee: Money = field(default_factory=lambda: Money(Decimal("0"), "USD"))
    taker_fee: Money = field(default_factory=lambda: Money(Decimal("0"), "USD"))


@dataclass
class Position:
    """A derivatives position held by an account."""
    account_id: AccountId
    instrument_id: InstrumentId
    side: Side
    quantity: Quantity
    entry_price: Price
    mark_price: Optional[Price] = None
    liquidation_price: Optional[Price] = None
    margin_type: MarginType = MarginType.ISOLATED
    initial_margin: Money = field(default_factory=lambda: Money(Decimal("0"), "USD"))
    maintenance_margin: Money = field(default_factory=lambda: Money(Decimal("0"), "USD"))
    unrealized_pnl: Money = field(default_factory=lambda: Money(Decimal("0"), "USD"))
    realized_pnl: Money = field(default_factory=lambda: Money(Decimal("0"), "USD"))
    updated_at: datetime = field(default_factory=datetime.utcnow)
