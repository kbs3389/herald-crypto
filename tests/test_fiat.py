"""Tests for the fiat payment gateway."""
import pytest
from decimal import Decimal

from src.services.fiat.service import FiatService, PaymentMethod as FiatPaymentMethod
from src.services.fiat.gateway import (
    PaymentGateway, PaymentMethod, PaymentStatus, GatewayProvider,
)


class TestFiatService:
    def test_add_bank_account(self):
        svc = FiatService()
        acct = svc.add_bank_account("user1", "Chase", "1234", "021000021")
        assert acct.bank_name == "Chase"
        assert acct.is_primary is True

    def test_deposit(self):
        svc = FiatService()
        tx = svc.initiate_deposit("user1", "USD", Decimal("1000"))
        assert tx is not None
        assert tx.amount == Decimal("1000")
        assert tx.direction == "DEPOSIT"

    def test_deposit_exceeds_limit(self):
        svc = FiatService()
        # KYC level 1 limit is $5000
        tx = svc.initiate_deposit("user1", "USD", Decimal("10000"), kyc_level=1)
        assert tx is None

    def test_withdrawal(self):
        svc = FiatService()
        tx = svc.initiate_withdrawal("user1", "USD", Decimal("500"))
        assert tx is not None
        assert tx.direction == "WITHDRAWAL"

    def test_exchange_rate(self):
        svc = FiatService()
        rate = svc.get_exchange_rate("EUR", "USDT")
        assert rate == Decimal("1.08")

    def test_convert_to_usdt(self):
        svc = FiatService()
        usdt = svc.convert_to_usdt("GBP", Decimal("100"))
        assert usdt == Decimal("127.00")


class TestPaymentGateway:
    def test_create_intent(self):
        gw = PaymentGateway()
        intent = gw.create_payment_intent("user1", Decimal("100"))
        assert intent.amount == Decimal("100")
        assert intent.status == PaymentStatus.CREATED
        assert intent.intent_id.startswith("pi_")

    def test_sandbox_confirm(self):
        gw = PaymentGateway(provider=GatewayProvider.SANDBOX)
        intent = gw.create_payment_intent("user1", Decimal("500"))
        confirmed = gw.confirm_payment(intent.intent_id)
        assert confirmed is not None
        assert confirmed.status == PaymentStatus.SUCCEEDED

    def test_card_fee(self):
        gw = PaymentGateway()
        intent = gw.create_payment_intent(
            "user1", Decimal("100"), payment_method=PaymentMethod.CARD,
        )
        # 2.9% + $0.30
        expected_fee = Decimal("100") * Decimal("0.029") + Decimal("0.30")
        assert intent.fee == expected_fee

    def test_cancel(self):
        gw = PaymentGateway()
        intent = gw.create_payment_intent("user1", Decimal("100"))
        cancelled = gw.cancel_payment(intent.intent_id)
        assert cancelled.status == PaymentStatus.CANCELLED

    def test_refund(self):
        gw = PaymentGateway()
        intent = gw.create_payment_intent("user1", Decimal("100"))
        gw.confirm_payment(intent.intent_id)
        refunded = gw.refund_payment(intent.intent_id)
        assert refunded.status == PaymentStatus.REFUNDED

    def test_user_payments(self):
        gw = PaymentGateway()
        gw.create_payment_intent("user1", Decimal("100"))
        gw.create_payment_intent("user1", Decimal("200"))
        gw.create_payment_intent("user2", Decimal("300"))
        payments = gw.get_user_payments("user1")
        assert len(payments) == 2

    def test_daily_volume(self):
        gw = PaymentGateway()
        gw.create_payment_intent("user1", Decimal("1000"))
        gw.create_payment_intent("user1", Decimal("2000"))
        vol = gw.get_daily_volume("user1")
        assert vol == Decimal("3000")
