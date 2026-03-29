"""
Herald Crypto Exchange - Core Domain Types

Foundational value objects and type definitions used across all bounded contexts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum, auto
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Money:
    """Immutable monetary amount with currency."""
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} from {other.currency}")
        return Money(self.amount - other.amount, self.currency)


@dataclass(frozen=True)
class Quantity:
    """Immutable quantity for orders and positions."""
    value: Decimal

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Quantity cannot be negative")


@dataclass(frozen=True)
class Price:
    """Immutable price value."""
    value: Decimal

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Price must be positive")


@dataclass(frozen=True)
class AssetId:
    """Unique identifier for an asset (e.g., BTC, ETH, USD)."""
    symbol: str


@dataclass(frozen=True)
class InstrumentId:
    """Unique identifier for a tradeable instrument (e.g., BTC-USD-SPOT)."""
    symbol: str


@dataclass(frozen=True)
class AccountId:
    """Unique identifier for a user/system account."""
    value: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class OrderId:
    """Unique identifier for an order."""
    value: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class TradeId:
    """Unique identifier for a trade/fill."""
    value: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class LedgerEntryId:
    """Unique identifier for a ledger entry."""
    value: UUID = field(default_factory=uuid4)


class Side(Enum):
    BUY = auto()
    SELL = auto()


class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()
    STOP_LIMIT = auto()
    STOP_MARKET = auto()
    ICEBERG = auto()


class TimeInForce(Enum):
    GTC = auto()
    IOC = auto()
    FOK = auto()
    GTD = auto()
    DAY = auto()


class OrderStatus(Enum):
    PENDING = auto()
    ACCEPTED = auto()
    PARTIALLY_FILLED = auto()
    FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()
    EXPIRED = auto()


class InstrumentType(Enum):
    SPOT = auto()
    DATED_FUTURE = auto()
    PERPETUAL = auto()
    EUROPEAN_OPTION = auto()


class OptionType(Enum):
    CALL = auto()
    PUT = auto()


class AccountType(Enum):
    RETAIL = auto()
    INSTITUTIONAL = auto()
    SUBACCOUNT = auto()
    OMNIBUS = auto()
    BROKER = auto()
    TREASURY = auto()
    HOUSE = auto()
    INSURANCE_FUND = auto()
    FEE_COLLECTION = auto()


class WalletTier(Enum):
    HOT = auto()
    WARM = auto()
    COLD = auto()


class KycLevel(Enum):
    NONE = auto()
    BASIC = auto()
    INTERMEDIATE = auto()
    ADVANCED = auto()
    INSTITUTIONAL = auto()


class MarginType(Enum):
    ISOLATED = auto()
    CROSS = auto()
    PORTFOLIO = auto()
