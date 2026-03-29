"""
Herald Crypto Exchange - Risk Engine

Pre-trade risk checks and margin calculations.
Portfolio margin bounded to well-defined risk groups (HC-014).
All risk parameter changes are auditable (HC-015).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple


class RiskCheckResult(Enum):
    PASSED = auto()
    REJECTED_INSUFFICIENT_BALANCE = auto()
    REJECTED_PRICE_PROTECTION = auto()
    REJECTED_POSITION_LIMIT = auto()
    REJECTED_RATE_LIMIT = auto()
    REJECTED_ACCOUNT_RESTRICTED = auto()
    REJECTED_INSTRUMENT_SUSPENDED = auto()


@dataclass(frozen=True)
class RiskParameters:
    """Risk parameters for an instrument. Changes are auditable (HC-015)."""
    instrument_id: str
    max_order_size: Decimal = Decimal("1000000")
    max_position_size: Decimal = Decimal("10000000")
    price_band_pct: Decimal = Decimal("0.10")
    initial_margin_rate: Decimal = Decimal("0.10")
    maintenance_margin_rate: Decimal = Decimal("0.05")
    max_leverage: Decimal = Decimal("20")
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: str = ""


@dataclass(frozen=True)
class MarginRequirement:
    initial_margin: Decimal = Decimal("0")
    maintenance_margin: Decimal = Decimal("0")
    margin_group: str = ""


@dataclass(frozen=True)
class RiskCheckRequest:
    account_id: str
    instrument_id: str
    side: str
    order_type: str
    quantity: Decimal
    price: Optional[Decimal] = None
    available_balance: Decimal = Decimal("0")
    current_position: Decimal = Decimal("0")
    reference_price: Optional[Decimal] = None


class RiskEngine:
    """
    Pre-trade risk engine for spot and derivatives.

    Hard Constraints:
    - HC-014: Portfolio margin bounded to well-defined risk groups
    - HC-015: All risk parameter changes auditable
    """

    def __init__(self):
        self._parameters: Dict[str, RiskParameters] = {}
        self._parameter_history: List[Tuple[datetime, str, RiskParameters]] = []

    def set_parameters(self, params: RiskParameters, changed_by: str) -> None:
        self._parameters[params.instrument_id] = params
        self._parameter_history.append((datetime.utcnow(), changed_by, params))

    def check_pre_trade(self, request: RiskCheckRequest) -> RiskCheckResult:
        params = self._parameters.get(request.instrument_id)
        if params is None:
            return RiskCheckResult.REJECTED_INSTRUMENT_SUSPENDED

        if request.quantity > params.max_order_size:
            return RiskCheckResult.REJECTED_POSITION_LIMIT

        new_position = abs(request.current_position + (
            request.quantity if request.side == "BUY" else -request.quantity
        ))
        if new_position > params.max_position_size:
            return RiskCheckResult.REJECTED_POSITION_LIMIT

        if request.price and request.reference_price:
            deviation = abs(request.price - request.reference_price) / request.reference_price
            if deviation > params.price_band_pct:
                return RiskCheckResult.REJECTED_PRICE_PROTECTION

        required = self.calculate_margin(request, params)
        if request.available_balance < required.initial_margin:
            return RiskCheckResult.REJECTED_INSUFFICIENT_BALANCE

        return RiskCheckResult.PASSED

    def calculate_margin(
        self, request: RiskCheckRequest, params: Optional[RiskParameters] = None
    ) -> MarginRequirement:
        if params is None:
            params = self._parameters.get(request.instrument_id, RiskParameters(
                instrument_id=request.instrument_id
            ))
        price = request.price or request.reference_price or Decimal("0")
        notional = request.quantity * price
        return MarginRequirement(
            initial_margin=notional * params.initial_margin_rate,
            maintenance_margin=notional * params.maintenance_margin_rate,
            margin_group=request.instrument_id.split("-")[0],
        )

    def check_liquidation(
        self, account_id: str, instrument_id: str, position_size: Decimal,
        entry_price: Decimal, mark_price: Decimal, margin_balance: Decimal,
    ) -> bool:
        params = self._parameters.get(instrument_id)
        if params is None:
            return False
        notional = position_size * mark_price
        maintenance_required = notional * params.maintenance_margin_rate
        return margin_balance < maintenance_required
