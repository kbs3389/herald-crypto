"""
Herald Crypto Exchange - Fiat Rails & Treasury Service (Agent 13)

Fiat on/off ramp, bank integrations, payment processing,
treasury management, and currency conversion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import uuid4


class FiatCurrency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    SGD = "SGD"
    HKD = "HKD"


class PaymentMethod(Enum):
    BANK_TRANSFER = auto()
    WIRE_TRANSFER = auto()
    SEPA = auto()
    FASTER_PAYMENTS = auto()
    ACH = auto()
    CREDIT_CARD = auto()
    DEBIT_CARD = auto()


class FiatTxStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    REFUNDED = auto()
    ON_HOLD = auto()


@dataclass
class FiatTransaction:
    tx_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    direction: str = "DEPOSIT"  # DEPOSIT or WITHDRAWAL
    currency: str = "USD"
    amount: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    status: FiatTxStatus = FiatTxStatus.PENDING
    bank_reference: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


@dataclass
class BankAccount:
    account_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    bank_name: str = ""
    account_number_last4: str = ""
    routing_number: str = ""
    currency: str = "USD"
    is_verified: bool = False
    is_primary: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


# Fee schedule by payment method
FEE_SCHEDULE = {
    PaymentMethod.BANK_TRANSFER: {"deposit": Decimal("0"), "withdrawal": Decimal("25")},
    PaymentMethod.WIRE_TRANSFER: {"deposit": Decimal("0"), "withdrawal": Decimal("35")},
    PaymentMethod.SEPA: {"deposit": Decimal("0"), "withdrawal": Decimal("1")},
    PaymentMethod.ACH: {"deposit": Decimal("0"), "withdrawal": Decimal("0")},
    PaymentMethod.CREDIT_CARD: {"deposit_pct": Decimal("0.035"), "withdrawal": None},
    PaymentMethod.DEBIT_CARD: {"deposit_pct": Decimal("0.02"), "withdrawal": None},
}

# Daily limits by KYC level
FIAT_LIMITS = {
    0: Decimal("0"),
    1: Decimal("5000"),
    2: Decimal("50000"),
    3: Decimal("500000"),
    4: Decimal("10000000"),
}

# Exchange rates (demo static rates)
EXCHANGE_RATES = {
    ("USD", "USDT"): Decimal("1.0"),
    ("EUR", "USDT"): Decimal("1.08"),
    ("GBP", "USDT"): Decimal("1.27"),
    ("JPY", "USDT"): Decimal("0.0067"),
    ("AUD", "USDT"): Decimal("0.65"),
    ("CAD", "USDT"): Decimal("0.74"),
    ("CHF", "USDT"): Decimal("1.13"),
    ("SGD", "USDT"): Decimal("0.75"),
    ("HKD", "USDT"): Decimal("0.13"),
}


class FiatService:
    """Fiat on/off ramp and treasury management service."""

    def __init__(self):
        self._transactions: list[FiatTransaction] = []
        self._bank_accounts: dict[str, list[BankAccount]] = {}
        self._daily_volumes: dict[str, Decimal] = {}

    def add_bank_account(self, user_id: str, bank_name: str,
                         account_last4: str, routing: str = "",
                         currency: str = "USD") -> BankAccount:
        account = BankAccount(
            user_id=user_id, bank_name=bank_name,
            account_number_last4=account_last4,
            routing_number=routing, currency=currency,
        )
        if user_id not in self._bank_accounts:
            self._bank_accounts[user_id] = []
            account.is_primary = True
        self._bank_accounts[user_id].append(account)
        return account

    def get_bank_accounts(self, user_id: str) -> list[BankAccount]:
        return self._bank_accounts.get(user_id, [])

    def initiate_deposit(self, user_id: str, currency: str, amount: Decimal,
                         payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER,
                         kyc_level: int = 1) -> Optional[FiatTransaction]:
        limit = FIAT_LIMITS.get(kyc_level, Decimal("0"))
        if amount > limit:
            return None

        fees = FEE_SCHEDULE.get(payment_method, {})
        if "deposit_pct" in fees:
            fee = amount * fees["deposit_pct"]
        else:
            fee = fees.get("deposit", Decimal("0"))

        tx = FiatTransaction(
            user_id=user_id, direction="DEPOSIT",
            currency=currency, amount=amount, fee=fee,
            net_amount=amount - fee,
            payment_method=payment_method,
            bank_reference=f"HD-{uuid4().hex[:8].upper()}",
        )
        self._transactions.append(tx)
        return tx

    def initiate_withdrawal(self, user_id: str, currency: str, amount: Decimal,
                            payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER,
                            kyc_level: int = 1) -> Optional[FiatTransaction]:
        limit = FIAT_LIMITS.get(kyc_level, Decimal("0"))
        if amount > limit:
            return None

        fees = FEE_SCHEDULE.get(payment_method, {})
        fee = fees.get("withdrawal", Decimal("0"))
        if fee is None:
            return None  # Method not supported for withdrawals

        tx = FiatTransaction(
            user_id=user_id, direction="WITHDRAWAL",
            currency=currency, amount=amount, fee=fee,
            net_amount=amount - fee,
            payment_method=payment_method,
            bank_reference=f"HD-{uuid4().hex[:8].upper()}",
        )
        self._transactions.append(tx)
        return tx

    def confirm_transaction(self, tx_id: str) -> Optional[FiatTransaction]:
        for tx in self._transactions:
            if tx.tx_id == tx_id:
                tx.status = FiatTxStatus.COMPLETED
                tx.updated_at = datetime.utcnow()
                return tx
        return None

    def get_transactions(self, user_id: str, limit: int = 50) -> list[FiatTransaction]:
        user_txs = [tx for tx in self._transactions if tx.user_id == user_id]
        return user_txs[-limit:]

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Decimal]:
        rate = EXCHANGE_RATES.get((from_currency, to_currency))
        if rate:
            return rate
        reverse = EXCHANGE_RATES.get((to_currency, from_currency))
        if reverse and reverse > 0:
            return Decimal("1") / reverse
        return None

    def convert_to_usdt(self, currency: str, amount: Decimal) -> Optional[Decimal]:
        rate = self.get_exchange_rate(currency, "USDT")
        if rate is None:
            return None
        return amount * rate
