"""Tests for the double-entry ledger."""
from decimal import Decimal
from uuid import uuid4

import pytest

from src.core.ledger.ledger import (
    DebitCredit,
    EntryType,
    Ledger,
    LedgerEntry,
    LedgerTransaction,
)


class TestLedger:
    def test_empty_balance(self):
        ledger = Ledger()
        assert ledger.get_balance("user1", "BTC") == Decimal("0")

    def test_deposit(self):
        ledger = Ledger()
        txn = LedgerTransaction(
            transaction_id=uuid4(),
            entries=(
                LedgerEntry(
                    account_id="user1", asset="BTC",
                    amount=Decimal("1.5"), direction=DebitCredit.DEBIT,
                    entry_type=EntryType.DEPOSIT,
                ),
                LedgerEntry(
                    account_id="exchange-reserve", asset="BTC",
                    amount=Decimal("1.5"), direction=DebitCredit.CREDIT,
                    entry_type=EntryType.DEPOSIT,
                ),
            ),
            entry_type=EntryType.DEPOSIT,
            idempotency_key="dep-1",
        )
        assert txn.validate()
        assert ledger.append_transaction(txn)
        assert ledger.get_balance("user1", "BTC") == Decimal("1.5")

    def test_idempotency(self):
        ledger = Ledger()
        txn = LedgerTransaction(
            entries=(
                LedgerEntry(account_id="u1", asset="ETH", amount=Decimal("10"),
                            direction=DebitCredit.DEBIT, entry_type=EntryType.DEPOSIT),
                LedgerEntry(account_id="reserve", asset="ETH", amount=Decimal("10"),
                            direction=DebitCredit.CREDIT, entry_type=EntryType.DEPOSIT),
            ),
            entry_type=EntryType.DEPOSIT,
            idempotency_key="idem-1",
        )
        assert ledger.append_transaction(txn)
        # Second append with same key should be no-op
        assert not ledger.append_transaction(txn)
        assert ledger.get_balance("u1", "ETH") == Decimal("10")

    def test_unbalanced_transaction_raises(self):
        ledger = Ledger()
        txn = LedgerTransaction(
            entries=(
                LedgerEntry(account_id="u1", asset="BTC", amount=Decimal("1"),
                            direction=DebitCredit.DEBIT, entry_type=EntryType.DEPOSIT),
            ),
            entry_type=EntryType.DEPOSIT,
            idempotency_key="bad-1",
        )
        assert not txn.validate()
        with pytest.raises(ValueError):
            ledger.append_transaction(txn)

    def test_trade_settlement(self):
        ledger = Ledger()
        # Seed balances
        ledger.append_transaction(LedgerTransaction(
            entries=(
                LedgerEntry(account_id="buyer", asset="USDT", amount=Decimal("100000"),
                            direction=DebitCredit.DEBIT, entry_type=EntryType.DEPOSIT),
                LedgerEntry(account_id="reserve", asset="USDT", amount=Decimal("100000"),
                            direction=DebitCredit.CREDIT, entry_type=EntryType.DEPOSIT),
            ),
            entry_type=EntryType.DEPOSIT, idempotency_key="seed-buyer",
        ))
        ledger.append_transaction(LedgerTransaction(
            entries=(
                LedgerEntry(account_id="seller", asset="BTC", amount=Decimal("1"),
                            direction=DebitCredit.DEBIT, entry_type=EntryType.DEPOSIT),
                LedgerEntry(account_id="reserve", asset="BTC", amount=Decimal("1"),
                            direction=DebitCredit.CREDIT, entry_type=EntryType.DEPOSIT),
            ),
            entry_type=EntryType.DEPOSIT, idempotency_key="seed-seller",
        ))

        # Trade: buyer gets 0.5 BTC, seller gets 25000 USDT
        trade_txn = LedgerTransaction(
            entries=(
                # BTC moves from seller to buyer
                LedgerEntry(account_id="buyer", asset="BTC", amount=Decimal("0.5"),
                            direction=DebitCredit.DEBIT, entry_type=EntryType.TRADE_SETTLEMENT),
                LedgerEntry(account_id="seller", asset="BTC", amount=Decimal("0.5"),
                            direction=DebitCredit.CREDIT, entry_type=EntryType.TRADE_SETTLEMENT),
                # USDT moves from buyer to seller
                LedgerEntry(account_id="seller", asset="USDT", amount=Decimal("25000"),
                            direction=DebitCredit.DEBIT, entry_type=EntryType.TRADE_SETTLEMENT),
                LedgerEntry(account_id="buyer", asset="USDT", amount=Decimal("25000"),
                            direction=DebitCredit.CREDIT, entry_type=EntryType.TRADE_SETTLEMENT),
            ),
            entry_type=EntryType.TRADE_SETTLEMENT, idempotency_key="trade-1",
        )
        assert trade_txn.validate()
        ledger.append_transaction(trade_txn)

        assert ledger.get_balance("buyer", "BTC") == Decimal("0.5")
        assert ledger.get_balance("buyer", "USDT") == Decimal("75000")
        assert ledger.get_balance("seller", "BTC") == Decimal("0.5")
        assert ledger.get_balance("seller", "USDT") == Decimal("25000")

    def test_entry_count(self):
        ledger = Ledger()
        txn = LedgerTransaction(
            entries=(
                LedgerEntry(account_id="u1", asset="SOL", amount=Decimal("100"),
                            direction=DebitCredit.DEBIT, entry_type=EntryType.DEPOSIT),
                LedgerEntry(account_id="reserve", asset="SOL", amount=Decimal("100"),
                            direction=DebitCredit.CREDIT, entry_type=EntryType.DEPOSIT),
            ),
            entry_type=EntryType.DEPOSIT, idempotency_key="count-1",
        )
        ledger.append_transaction(txn)
        assert ledger.entry_count == 2
        assert ledger.transaction_count == 1
