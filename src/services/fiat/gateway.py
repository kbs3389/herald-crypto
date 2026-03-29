"""
Herald Crypto Exchange - Fiat Payment Gateway Integration

Stripe-style payment gateway with sandbox/mock mode.
Supports card payments, bank transfers, and webhooks.
Works in sandbox mode without real API keys.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class GatewayProvider(str, Enum):
    STRIPE = "stripe"
    SANDBOX = "sandbox"


class PaymentStatus(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WIRE = "wire"
    SEPA = "sepa"
    ACH = "ach"


@dataclass
class PaymentIntent:
    intent_id: str = field(default_factory=lambda: f"pi_{uuid4().hex[:24]}")
    user_id: str = ""
    amount: Decimal = Decimal("0")
    currency: str = "USD"
    crypto_amount: Decimal = Decimal("0")
    crypto_asset: str = "USDT"
    direction: str = "deposit"  # deposit or withdrawal
    payment_method: PaymentMethod = PaymentMethod.CARD
    status: PaymentStatus = PaymentStatus.CREATED
    provider: GatewayProvider = GatewayProvider.SANDBOX
    provider_ref: str = ""
    fee: Decimal = Decimal("0")
    exchange_rate: Decimal = Decimal("1.0")
    client_secret: str = field(default_factory=lambda: f"cs_{uuid4().hex[:24]}")
    webhook_url: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    error_message: str = ""


@dataclass
class WebhookEvent:
    event_id: str = field(default_factory=lambda: f"evt_{uuid4().hex[:24]}")
    event_type: str = ""
    intent_id: str = ""
    payload: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


# Fee schedule
CARD_FEE_PCT = Decimal("0.029")  # 2.9%
CARD_FEE_FIXED = Decimal("0.30")  # $0.30
BANK_FEE = Decimal("0")  # Free for bank transfers
WIRE_FEE = Decimal("25.00")

# Exchange rates (sandbox static rates)
SANDBOX_RATES = {
    "USD": Decimal("1.0"),
    "EUR": Decimal("1.08"),
    "GBP": Decimal("1.27"),
    "JPY": Decimal("0.0067"),
}


class PaymentGateway:
    """
    Payment gateway with sandbox mode for development.

    In sandbox mode, all payments auto-succeed after a simulated delay.
    In production, would integrate with Stripe/similar.
    """

    def __init__(
        self,
        provider: GatewayProvider = GatewayProvider.SANDBOX,
        api_key: str = "",
        webhook_secret: str = "",
    ):
        self.provider = provider
        self._api_key = api_key
        self._webhook_secret = webhook_secret or f"whsec_{uuid4().hex[:24]}"
        self._intents: dict[str, PaymentIntent] = {}
        self._events: list[WebhookEvent] = []
        self._daily_volume: dict[str, Decimal] = {}

    def create_payment_intent(
        self,
        user_id: str,
        amount: Decimal,
        currency: str = "USD",
        direction: str = "deposit",
        payment_method: PaymentMethod = PaymentMethod.CARD,
    ) -> PaymentIntent:
        """Create a payment intent (Stripe-style)."""
        # Calculate fee
        if payment_method == PaymentMethod.CARD:
            fee = amount * CARD_FEE_PCT + CARD_FEE_FIXED
        elif payment_method == PaymentMethod.WIRE:
            fee = WIRE_FEE
        else:
            fee = BANK_FEE

        # Calculate crypto equivalent
        rate = SANDBOX_RATES.get(currency, Decimal("1.0"))
        crypto_amount = (amount - fee) * rate

        intent = PaymentIntent(
            user_id=user_id,
            amount=amount,
            currency=currency,
            crypto_amount=crypto_amount,
            direction=direction,
            payment_method=payment_method,
            provider=self.provider,
            fee=fee,
            exchange_rate=rate,
            provider_ref=f"sandbox_{uuid4().hex[:16]}",
        )
        self._intents[intent.intent_id] = intent

        # Track daily volume
        date_key = f"{user_id}:{datetime.utcnow().date()}"
        self._daily_volume[date_key] = self._daily_volume.get(
            date_key, Decimal("0")
        ) + amount

        return intent

    def confirm_payment(self, intent_id: str) -> Optional[PaymentIntent]:
        """Confirm/process a payment intent."""
        intent = self._intents.get(intent_id)
        if intent is None:
            return None

        if self.provider == GatewayProvider.SANDBOX:
            # Sandbox: auto-succeed
            intent.status = PaymentStatus.SUCCEEDED
            intent.updated_at = datetime.utcnow()
            self._emit_event("payment.succeeded", intent)
            return intent

        # Production: would call Stripe API here
        intent.status = PaymentStatus.PROCESSING
        intent.updated_at = datetime.utcnow()
        return intent

    def cancel_payment(self, intent_id: str) -> Optional[PaymentIntent]:
        """Cancel a payment intent."""
        intent = self._intents.get(intent_id)
        if intent is None:
            return None
        if intent.status not in (PaymentStatus.CREATED, PaymentStatus.PENDING):
            return None
        intent.status = PaymentStatus.CANCELLED
        intent.updated_at = datetime.utcnow()
        self._emit_event("payment.cancelled", intent)
        return intent

    def refund_payment(self, intent_id: str) -> Optional[PaymentIntent]:
        """Refund a completed payment."""
        intent = self._intents.get(intent_id)
        if intent is None:
            return None
        if intent.status != PaymentStatus.SUCCEEDED:
            return None
        intent.status = PaymentStatus.REFUNDED
        intent.updated_at = datetime.utcnow()
        self._emit_event("payment.refunded", intent)
        return intent

    def get_intent(self, intent_id: str) -> Optional[PaymentIntent]:
        return self._intents.get(intent_id)

    def get_user_payments(self, user_id: str, limit: int = 50) -> list[PaymentIntent]:
        user_intents = [
            i for i in self._intents.values() if i.user_id == user_id
        ]
        return sorted(user_intents, key=lambda x: x.created_at, reverse=True)[:limit]

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature (HMAC-SHA256)."""
        expected = hmac.new(
            self._webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def get_daily_volume(self, user_id: str) -> Decimal:
        date_key = f"{user_id}:{datetime.utcnow().date()}"
        return self._daily_volume.get(date_key, Decimal("0"))

    def _emit_event(self, event_type: str, intent: PaymentIntent) -> None:
        event = WebhookEvent(
            event_type=event_type,
            intent_id=intent.intent_id,
            payload={
                "intent_id": intent.intent_id,
                "user_id": intent.user_id,
                "amount": str(intent.amount),
                "currency": intent.currency,
                "crypto_amount": str(intent.crypto_amount),
                "status": intent.status.value,
                "fee": str(intent.fee),
            },
        )
        self._events.append(event)

    def get_events(self, limit: int = 50) -> list[dict]:
        return [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "intent_id": e.intent_id,
                "created_at": e.created_at.isoformat(),
            }
            for e in self._events[-limit:]
        ]
