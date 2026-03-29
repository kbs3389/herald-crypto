"""
Herald Crypto Exchange - Blockchain Chain Adapters

Read-only blockchain adapters for ETH and BTC.
Uses public APIs (no private keys needed for read operations).
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class BlockchainTransaction:
    tx_hash: str = ""
    from_address: str = ""
    to_address: str = ""
    amount: Decimal = Decimal("0")
    asset: str = ""
    confirmations: int = 0
    block_number: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, confirmed, failed


@dataclass
class AddressBalance:
    address: str = ""
    asset: str = ""
    balance: Decimal = Decimal("0")
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ChainAdapter(ABC):
    """Abstract base class for blockchain chain adapters."""

    @abstractmethod
    async def get_balance(self, address: str) -> Optional[AddressBalance]:
        pass

    @abstractmethod
    async def get_transaction(self, tx_hash: str) -> Optional[BlockchainTransaction]:
        pass

    @abstractmethod
    async def get_block_height(self) -> Optional[int]:
        pass

    @abstractmethod
    async def monitor_address(self, address: str) -> list[BlockchainTransaction]:
        pass

    @abstractmethod
    async def estimate_fee(self) -> Optional[Decimal]:
        pass


class EthereumAdapter(ChainAdapter):
    """
    Ethereum chain adapter using public RPC endpoints.
    Uses Cloudflare ETH gateway (no API key needed).
    """

    def __init__(self, rpc_url: str = "https://cloudflare-eth.com"):
        self._rpc_url = rpc_url
        self._http = httpx.AsyncClient(timeout=15.0)
        self._etherscan_base = "https://api.etherscan.io/api"

    async def get_balance(self, address: str) -> Optional[AddressBalance]:
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1,
            }
            resp = await self._http.post(self._rpc_url, json=payload)
            resp.raise_for_status()
            result = resp.json().get("result", "0x0")
            wei = int(result, 16)
            eth_balance = Decimal(str(wei)) / Decimal("1000000000000000000")
            return AddressBalance(
                address=address,
                asset="ETH",
                balance=eth_balance,
            )
        except Exception as e:
            logger.warning(f"ETH balance fetch failed: {e}")
            return None

    async def get_transaction(self, tx_hash: str) -> Optional[BlockchainTransaction]:
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionByHash",
                "params": [tx_hash],
                "id": 1,
            }
            resp = await self._http.post(self._rpc_url, json=payload)
            resp.raise_for_status()
            tx = resp.json().get("result")
            if tx is None:
                return None

            value_wei = int(tx.get("value", "0x0"), 16)
            eth_value = Decimal(str(value_wei)) / Decimal("1000000000000000000")

            # Get receipt for confirmation status
            receipt_payload = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionReceipt",
                "params": [tx_hash],
                "id": 2,
            }
            receipt_resp = await self._http.post(self._rpc_url, json=receipt_payload)
            receipt = receipt_resp.json().get("result")
            confirmed = receipt is not None and receipt.get("status") == "0x1"

            block_num = int(tx.get("blockNumber", "0x0"), 16) if tx.get("blockNumber") else 0

            return BlockchainTransaction(
                tx_hash=tx_hash,
                from_address=tx.get("from", ""),
                to_address=tx.get("to", ""),
                amount=eth_value,
                asset="ETH",
                block_number=block_num,
                status="confirmed" if confirmed else "pending",
            )
        except Exception as e:
            logger.warning(f"ETH tx fetch failed: {e}")
            return None

    async def get_block_height(self) -> Optional[int]:
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1,
            }
            resp = await self._http.post(self._rpc_url, json=payload)
            resp.raise_for_status()
            result = resp.json().get("result", "0x0")
            return int(result, 16)
        except Exception as e:
            logger.warning(f"ETH block height fetch failed: {e}")
            return None

    async def monitor_address(self, address: str) -> list[BlockchainTransaction]:
        """Monitor address for recent transactions (limited without API key)."""
        return []

    async def estimate_fee(self) -> Optional[Decimal]:
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": 1,
            }
            resp = await self._http.post(self._rpc_url, json=payload)
            resp.raise_for_status()
            gas_price_wei = int(resp.json().get("result", "0x0"), 16)
            # Standard transfer = 21000 gas
            fee_wei = gas_price_wei * 21000
            fee_eth = Decimal(str(fee_wei)) / Decimal("1000000000000000000")
            return fee_eth
        except Exception as e:
            logger.warning(f"ETH fee estimate failed: {e}")
            return None

    async def close(self) -> None:
        await self._http.aclose()


class BitcoinAdapter(ChainAdapter):
    """
    Bitcoin chain adapter using Blockstream public API.
    No API key required.
    """

    def __init__(self, base_url: str = "https://blockstream.info/api"):
        self._base_url = base_url
        self._http = httpx.AsyncClient(timeout=15.0)

    async def get_balance(self, address: str) -> Optional[AddressBalance]:
        try:
            resp = await self._http.get(f"{self._base_url}/address/{address}")
            resp.raise_for_status()
            data = resp.json()
            funded = data.get("chain_stats", {}).get("funded_txo_sum", 0)
            spent = data.get("chain_stats", {}).get("spent_txo_sum", 0)
            balance_sats = funded - spent
            balance_btc = Decimal(str(balance_sats)) / Decimal("100000000")
            return AddressBalance(
                address=address,
                asset="BTC",
                balance=balance_btc,
            )
        except Exception as e:
            logger.warning(f"BTC balance fetch failed: {e}")
            return None

    async def get_transaction(self, tx_hash: str) -> Optional[BlockchainTransaction]:
        try:
            resp = await self._http.get(f"{self._base_url}/tx/{tx_hash}")
            resp.raise_for_status()
            data = resp.json()

            # Sum outputs for amount
            total_out = sum(
                out.get("value", 0) for out in data.get("vout", [])
            )
            amount_btc = Decimal(str(total_out)) / Decimal("100000000")

            confirmed = data.get("status", {}).get("confirmed", False)
            block_height = data.get("status", {}).get("block_height", 0)

            return BlockchainTransaction(
                tx_hash=tx_hash,
                from_address="",  # BTC uses UTXO model
                to_address="",
                amount=amount_btc,
                asset="BTC",
                block_number=block_height,
                status="confirmed" if confirmed else "pending",
            )
        except Exception as e:
            logger.warning(f"BTC tx fetch failed: {e}")
            return None

    async def get_block_height(self) -> Optional[int]:
        try:
            resp = await self._http.get(f"{self._base_url}/blocks/tip/height")
            resp.raise_for_status()
            return int(resp.text)
        except Exception as e:
            logger.warning(f"BTC block height fetch failed: {e}")
            return None

    async def monitor_address(self, address: str) -> list[BlockchainTransaction]:
        """Get recent transactions for an address."""
        try:
            resp = await self._http.get(f"{self._base_url}/address/{address}/txs")
            resp.raise_for_status()
            txs = resp.json()
            results = []
            for tx in txs[:10]:
                total_out = sum(out.get("value", 0) for out in tx.get("vout", []))
                amount_btc = Decimal(str(total_out)) / Decimal("100000000")
                confirmed = tx.get("status", {}).get("confirmed", False)
                results.append(BlockchainTransaction(
                    tx_hash=tx.get("txid", ""),
                    amount=amount_btc,
                    asset="BTC",
                    block_number=tx.get("status", {}).get("block_height", 0),
                    status="confirmed" if confirmed else "pending",
                ))
            return results
        except Exception as e:
            logger.warning(f"BTC monitor failed: {e}")
            return []

    async def estimate_fee(self) -> Optional[Decimal]:
        try:
            resp = await self._http.get(f"{self._base_url}/fee-estimates")
            resp.raise_for_status()
            fees = resp.json()
            # Use 6-block target, ~1 hour confirmation
            sat_per_vbyte = Decimal(str(fees.get("6", "20")))
            # Average tx size ~250 vbytes
            fee_sats = sat_per_vbyte * 250
            fee_btc = fee_sats / Decimal("100000000")
            return fee_btc
        except Exception as e:
            logger.warning(f"BTC fee estimate failed: {e}")
            return None

    async def close(self) -> None:
        await self._http.aclose()


class ChainAdapterManager:
    """Manages multiple chain adapters."""

    def __init__(self):
        self.eth = EthereumAdapter()
        self.btc = BitcoinAdapter()
        self._adapters: dict[str, ChainAdapter] = {
            "ETH": self.eth,
            "BTC": self.btc,
        }

    def get_adapter(self, asset: str) -> Optional[ChainAdapter]:
        return self._adapters.get(asset)

    async def get_all_block_heights(self) -> dict[str, Optional[int]]:
        results = {}
        for asset, adapter in self._adapters.items():
            results[asset] = await adapter.get_block_height()
        return results

    async def close(self) -> None:
        for adapter in self._adapters.values():
            if hasattr(adapter, "close"):
                await adapter.close()
