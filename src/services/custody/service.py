"""
Herald Crypto Exchange - Custody & Wallet Service (Agent 10)

Wallet management, deposit/withdrawal flows, hot/cold wallet segregation,
address generation, and transaction tracking.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import uuid4


class WalletType(Enum):
    HOT = auto()
    WARM = auto()
    COLD = auto()


class WalletStatus(Enum):
    ACTIVE = auto()
    SUSPENDED = auto()
    ARCHIVED = auto()


class TransactionStatus(Enum):
    PENDING = auto()
    CONFIRMING = auto()
    CONFIRMED = auto()
    FAILED = auto()
    CANCELLED = auto()


class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    INTERNAL_TRANSFER = auto()
    SWEEP = auto()


@dataclass
class Wallet:
    wallet_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    asset: str = ""
    wallet_type: WalletType = WalletType.HOT
    status: WalletStatus = WalletStatus.ACTIVE
    address: str = ""
    balance: Decimal = Decimal("0")
    reserved: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    label: str = ""

    @property
    def available(self) -> Decimal:
        return self.balance - self.reserved


@dataclass
class CustodyTransaction:
    tx_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    asset: str = ""
    amount: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")
    tx_type: TransactionType = TransactionType.DEPOSIT
    status: TransactionStatus = TransactionStatus.PENDING
    from_address: str = ""
    to_address: str = ""
    chain_tx_hash: Optional[str] = None
    confirmations: int = 0
    required_confirmations: int = 6
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


# Required confirmations per chain
CHAIN_CONFIRMATIONS = {
    "BTC": 3, "ETH": 12, "SOL": 32, "XRP": 1,
    "USDT": 12, "USDC": 12,
}

# Withdrawal fees per asset
WITHDRAWAL_FEES = {
    "BTC": Decimal("0.0001"), "ETH": Decimal("0.001"),
    "SOL": Decimal("0.01"), "XRP": Decimal("0.1"),
    "USDT": Decimal("1"), "USDC": Decimal("1"),
}


class CustodyService:
    """Custody engine managing wallets, deposits, and withdrawals."""

    def __init__(self):
        self._wallets: dict[str, Wallet] = {}
        self._transactions: list[CustodyTransaction] = []
        self._user_wallets: dict[str, list[str]] = {}
        self._hot_wallet_limits: dict[str, Decimal] = {
            "BTC": Decimal("100"), "ETH": Decimal("1000"),
            "SOL": Decimal("50000"), "XRP": Decimal("5000000"),
            "USDT": Decimal("10000000"), "USDC": Decimal("10000000"),
        }

    def create_wallet(self, user_id: str, asset: str,
                      wallet_type: WalletType = WalletType.HOT,
                      label: str = "") -> Wallet:
        address = self._generate_address(user_id, asset)
        wallet = Wallet(
            user_id=user_id, asset=asset,
            wallet_type=wallet_type, address=address,
            label=label or f"{asset} {wallet_type.name} Wallet",
        )
        self._wallets[wallet.wallet_id] = wallet
        if user_id not in self._user_wallets:
            self._user_wallets[user_id] = []
        self._user_wallets[user_id].append(wallet.wallet_id)
        return wallet

    def get_user_wallets(self, user_id: str) -> list[Wallet]:
        wallet_ids = self._user_wallets.get(user_id, [])
        return [self._wallets[wid] for wid in wallet_ids if wid in self._wallets]

    def get_wallet(self, wallet_id: str) -> Optional[Wallet]:
        return self._wallets.get(wallet_id)

    def initiate_deposit(self, user_id: str, asset: str,
                         amount: Decimal, from_address: str = "") -> CustodyTransaction:
        wallets = [w for w in self.get_user_wallets(user_id) if w.asset == asset]
        if not wallets:
            wallet = self.create_wallet(user_id, asset)
        else:
            wallet = wallets[0]

        tx = CustodyTransaction(
            user_id=user_id, asset=asset, amount=amount,
            tx_type=TransactionType.DEPOSIT,
            from_address=from_address, to_address=wallet.address,
            required_confirmations=CHAIN_CONFIRMATIONS.get(asset, 6),
        )
        self._transactions.append(tx)
        return tx

    def confirm_deposit(self, tx_id: str, chain_tx_hash: str = "") -> Optional[CustodyTransaction]:
        for tx in self._transactions:
            if tx.tx_id == tx_id and tx.tx_type == TransactionType.DEPOSIT:
                tx.status = TransactionStatus.CONFIRMED
                tx.chain_tx_hash = chain_tx_hash or f"0x{uuid4().hex}"
                tx.confirmations = tx.required_confirmations
                tx.updated_at = datetime.utcnow()
                # Credit wallet balance
                for w in self.get_user_wallets(tx.user_id):
                    if w.asset == tx.asset:
                        w.balance += tx.amount
                        w.updated_at = datetime.utcnow()
                        break
                return tx
        return None

    def initiate_withdrawal(self, user_id: str, asset: str, amount: Decimal,
                            to_address: str) -> Optional[CustodyTransaction]:
        wallets = [w for w in self.get_user_wallets(user_id) if w.asset == asset]
        if not wallets:
            return None
        wallet = wallets[0]
        fee = WITHDRAWAL_FEES.get(asset, Decimal("0"))
        total = amount + fee
        if wallet.available < total:
            return None

        wallet.reserved += total
        wallet.updated_at = datetime.utcnow()

        tx = CustodyTransaction(
            user_id=user_id, asset=asset, amount=amount, fee=fee,
            tx_type=TransactionType.WITHDRAWAL,
            from_address=wallet.address, to_address=to_address,
            required_confirmations=1,
        )
        self._transactions.append(tx)
        return tx

    def approve_withdrawal(self, tx_id: str) -> Optional[CustodyTransaction]:
        for tx in self._transactions:
            if tx.tx_id == tx_id and tx.tx_type == TransactionType.WITHDRAWAL:
                tx.status = TransactionStatus.CONFIRMED
                tx.chain_tx_hash = f"0x{uuid4().hex}"
                tx.updated_at = datetime.utcnow()
                # Debit wallet
                for w in self.get_user_wallets(tx.user_id):
                    if w.asset == tx.asset:
                        total = tx.amount + tx.fee
                        w.balance -= total
                        w.reserved -= total
                        w.updated_at = datetime.utcnow()
                        break
                return tx
        return None

    def get_transactions(self, user_id: str, limit: int = 50) -> list[CustodyTransaction]:
        user_txs = [tx for tx in self._transactions if tx.user_id == user_id]
        return user_txs[-limit:]

    def get_deposit_address(self, user_id: str, asset: str) -> str:
        wallets = [w for w in self.get_user_wallets(user_id) if w.asset == asset]
        if not wallets:
            wallet = self.create_wallet(user_id, asset)
            return wallet.address
        return wallets[0].address

    def _generate_address(self, user_id: str, asset: str) -> str:
        """Generate a deterministic demo deposit address."""
        seed = f"{user_id}:{asset}:{uuid4().hex[:8]}"
        h = hashlib.sha256(seed.encode()).hexdigest()
        prefix = {"BTC": "bc1q", "ETH": "0x", "SOL": "", "XRP": "r"}.get(asset, "0x")
        return f"{prefix}{h[:40]}"

    def check_hot_wallet_health(self) -> dict:
        """Check if hot wallets are within limits."""
        results = {}
        for asset, limit in self._hot_wallet_limits.items():
            hot_balance = sum(
                w.balance for w in self._wallets.values()
                if w.asset == asset and w.wallet_type == WalletType.HOT
            )
            results[asset] = {
                "balance": str(hot_balance),
                "limit": str(limit),
                "utilization_pct": str(
                    (hot_balance / limit * 100) if limit > 0 else Decimal("0")
                ),
                "healthy": hot_balance <= limit,
            }
        return results
