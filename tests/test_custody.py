"""Tests for the custody service."""
import pytest
from decimal import Decimal

from src.services.custody.service import (
    CustodyService, WalletType, TransactionStatus, TransactionType,
)


class TestCustodyService:
    def test_create_wallet(self):
        svc = CustodyService()
        wallet = svc.create_wallet("user1", "BTC")
        assert wallet.asset == "BTC"
        assert wallet.user_id == "user1"
        assert wallet.address.startswith("bc1q")
        assert wallet.balance == Decimal("0")

    def test_eth_address_prefix(self):
        svc = CustodyService()
        wallet = svc.create_wallet("user1", "ETH")
        assert wallet.address.startswith("0x")

    def test_deposit_flow(self):
        svc = CustodyService()
        tx = svc.initiate_deposit("user1", "BTC", Decimal("1.5"))
        assert tx.status == TransactionStatus.PENDING
        assert tx.amount == Decimal("1.5")

        confirmed = svc.confirm_deposit(tx.tx_id)
        assert confirmed is not None
        assert confirmed.status == TransactionStatus.CONFIRMED

        wallets = svc.get_user_wallets("user1")
        assert len(wallets) == 1
        assert wallets[0].balance == Decimal("1.5")

    def test_withdrawal_flow(self):
        svc = CustodyService()
        # Deposit first
        dep = svc.initiate_deposit("user1", "ETH", Decimal("10"))
        svc.confirm_deposit(dep.tx_id)

        # Withdraw
        tx = svc.initiate_withdrawal("user1", "ETH", Decimal("5"), "0xabc123")
        assert tx is not None
        assert tx.amount == Decimal("5")

        approved = svc.approve_withdrawal(tx.tx_id)
        assert approved.status == TransactionStatus.CONFIRMED

    def test_insufficient_withdrawal(self):
        svc = CustodyService()
        dep = svc.initiate_deposit("user1", "BTC", Decimal("1"))
        svc.confirm_deposit(dep.tx_id)
        # Try to withdraw more than balance
        tx = svc.initiate_withdrawal("user1", "BTC", Decimal("100"), "bc1qxyz")
        assert tx is None

    def test_deposit_address_generation(self):
        svc = CustodyService()
        addr1 = svc.get_deposit_address("user1", "BTC")
        assert addr1.startswith("bc1q")
        # Same user/asset should return same wallet
        addr2 = svc.get_deposit_address("user1", "BTC")
        assert addr1 == addr2

    def test_hot_wallet_health(self):
        svc = CustodyService()
        health = svc.check_hot_wallet_health()
        assert "BTC" in health
        assert "ETH" in health
        for asset, data in health.items():
            assert data["healthy"] is True
