"""
Herald Crypto Exchange - Event Definitions

Base event types for the event-sourced architecture.
All economic events produce immutable ledger entries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class EventType(Enum):
    ORDER_SUBMITTED = auto()
    ORDER_ACCEPTED = auto()
    ORDER_REJECTED = auto()
    ORDER_CANCELLED = auto()
    ORDER_EXPIRED = auto()
    ORDER_FILLED = auto()
    ORDER_PARTIALLY_FILLED = auto()
    TRADE_EXECUTED = auto()
    TRADE_CLEARED = auto()
    LEDGER_ENTRY_CREATED = auto()
    BALANCE_RESERVED = auto()
    BALANCE_RELEASED = auto()
    ACCOUNT_CREATED = auto()
    ACCOUNT_SUSPENDED = auto()
    ACCOUNT_CLOSED = auto()
    DEPOSIT_DETECTED = auto()
    DEPOSIT_CONFIRMED = auto()
    WITHDRAWAL_REQUESTED = auto()
    WITHDRAWAL_APPROVED = auto()
    WITHDRAWAL_EXECUTED = auto()
    WITHDRAWAL_REJECTED = auto()
    MARGIN_CALL = auto()
    LIQUIDATION_TRIGGERED = auto()
    LIQUIDATION_COMPLETED = auto()
    ADL_TRIGGERED = auto()
    MARK_PRICE_UPDATED = auto()
    INDEX_PRICE_UPDATED = auto()
    FUNDING_RATE_CALCULATED = auto()
    FUNDING_SETTLED = auto()
    KYC_COMPLETED = auto()
    SANCTIONS_ALERT = auto()
    AML_ALERT = auto()
    ACCOUNT_RESTRICTED = auto()
    RISK_PARAMETER_CHANGED = auto()
    INSTRUMENT_LISTED = auto()
    INSTRUMENT_SUSPENDED = auto()
    INSTRUMENT_DELISTED = auto()


@dataclass(frozen=True)
class DomainEvent:
    """Base domain event. All events are immutable and sequenced."""
    event_id: UUID = field(default_factory=uuid4)
    event_type: EventType = EventType.ORDER_SUBMITTED
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence_number: int = 0
    aggregate_id: str = ""
    aggregate_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    causation_id: Optional[UUID] = None
    correlation_id: Optional[UUID] = None
