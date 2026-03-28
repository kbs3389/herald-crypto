"""
Herald Crypto Exchange - Immutable Double-Entry Ledger

The ledger is the single source of truth for all balances.
All entries are immutable (append-only). Corrections are made via compensating entries.
Balances are derived from ledger state, never manually edited. (HC-003, HC-004)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional, Dict, Tuple
from uuid import UUID, uuid4


class EntryType(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRADE_SETTLEMENT = auto()
    FEE = auto()
    FUNDING_PAYMENT = auto()
    PREMIUM_PAYMENT = auto()
    LIQUIDATION = auto()
    INSURANCE_FUND = auto()
    TRANSFER = auto()
    RESERVATION = auto()
    RELEASE = auto()
    EXPIRY_SETTLEMENT = auto()
    CORRECTION = auto()


class DebitCredit(Enum):
    DEBIT = auto()
    CREDIT = auto()


@dataclass(frozen=True)
class LedgerEntry:
    """A single immutable ledger entry. Always part of a balanced transaction."""
    entry_id: UUID = field(default_factory=uuid4)
    transaction_id: UUID = field(default_factory=uuid4)
    account_id: str = ""
    asset: str = ""
    amount: Decimal = Decimal("0")
    direction: DebitCredit = DebitCredit.DEBIT
    entry_type: EntryType = EntryType.DEPOSIT
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence_number: int = 0
    idempotency_key: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class LedgerTransaction:
    """
    A balanced ledger transaction. Sum of debits must equal sum of credits.
    Invariant: For each asset in the transaction, total debits == total credits.
    """
    transaction_id: UUID = field(default_factory=uuid4)
    entries: Tuple[LedgerEntry, ...] = ()
    timestamp: datetime = field(default_factory=datetime.utcnow)
    entry_type: EntryType = EntryType.DEPOSIT
    reference_id: str = ""
    idempotency_key: str = ""

    def validate(self) -> bool:
        """Verify double-entry invariant: debits == credits per asset."""
        balances: Dict[str, Decimal] = {}
        for entry in self.entries:
            key = entry.asset
            if entry.direction == DebitCredit.DEBIT:
                balances[key] = balances.get(key, Decimal("0")) + entry.amount
            else:
                balances[key] = balances.get(key, Decimal("0")) - entry.amount
        return all(v == Decimal("0") for v in balances.values())


class Ledger:
    """
    Append-only immutable double-entry ledger.

    Hard Constraints Enforced:
    - HC-003: All economic events land in append-only immutable ledger
    - HC-004: Balances derived from ledger state, not manual edits
    """

    def __init__(self):
        self._entries: List[LedgerEntry] = []
        self._transactions: List[LedgerTransaction] = []
        self._idempotency_keys: set = set()
        self._sequence: int = 0

    def append_transaction(self, transaction: LedgerTransaction) -> bool:
        """
        Append a balanced transaction to the ledger.
        Returns True if successful, False if idempotency key already exists.
        Raises ValueError if transaction is not balanced.
        """
        if transaction.idempotency_key in self._idempotency_keys:
            return False

        if not transaction.validate():
            raise ValueError(
                f"Transaction {transaction.transaction_id} is not balanced"
            )

        self._idempotency_keys.add(transaction.idempotency_key)
        self._transactions.append(transaction)

        for entry in transaction.entries:
            self._sequence += 1
            sequenced = LedgerEntry(
                entry_id=entry.entry_id,
                transaction_id=transaction.transaction_id,
                account_id=entry.account_id,
                asset=entry.asset,
                amount=entry.amount,
                direction=entry.direction,
                entry_type=entry.entry_type,
                timestamp=entry.timestamp,
                sequence_number=self._sequence,
                idempotency_key=entry.idempotency_key,
                metadata=entry.metadata,
            )
            self._entries.append(sequenced)

        return True

    def get_balance(self, account_id: str, asset: str) -> Decimal:
        """Derive balance from ledger entries (HC-004)."""
        balance = Decimal("0")
        for entry in self._entries:
            if entry.account_id == account_id and entry.asset == asset:
                if entry.direction == DebitCredit.DEBIT:
                    balance += entry.amount
                else:
                    balance -= entry.amount
        return balance

    def get_entries_for_account(self, account_id: str) -> List[LedgerEntry]:
        """Get all ledger entries for a given account."""
        return [e for e in self._entries if e.account_id == account_id]

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    @property
    def transaction_count(self) -> int:
        return len(self._transactions)
