"""
Herald Crypto Exchange - Surveillance Service (Agent 12)

Market surveillance for wash trading, spoofing, layering,
front-running, and other market manipulation detection.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4


class AlertSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SurveillanceAlert:
    alert_id: str = field(default_factory=lambda: str(uuid4()))
    alert_type: str = ""
    severity: str = AlertSeverity.MEDIUM
    account_id: str = ""
    instrument_id: str = ""
    description: str = ""
    evidence: dict = field(default_factory=dict)
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None


class SurveillanceService:
    """Real-time market surveillance engine."""

    def __init__(self):
        self._alerts: list[SurveillanceAlert] = []
        self._order_history: dict[str, list[dict]] = defaultdict(list)
        self._trade_history: dict[str, list[dict]] = defaultdict(list)
        self._cancel_counts: dict[str, int] = defaultdict(int)
        self._thresholds = {
            "wash_trade_window_seconds": 10,
            "spoof_cancel_ratio": 0.9,
            "spoof_window_orders": 20,
            "layering_levels": 5,
            "large_order_threshold": Decimal("100000"),
        }

    def on_order(self, account_id: str, instrument_id: str, side: str,
                 price: Decimal, quantity: Decimal, order_id: str) -> list[SurveillanceAlert]:
        """Process a new order for surveillance checks."""
        now = datetime.utcnow()
        self._order_history[account_id].append({
            "order_id": order_id, "instrument_id": instrument_id,
            "side": side, "price": str(price), "quantity": str(quantity),
            "timestamp": now, "status": "active",
        })
        alerts = []
        # Check for layering (multiple orders at different price levels)
        layering = self._check_layering(account_id, instrument_id, side)
        if layering:
            alerts.append(layering)
        return alerts

    def on_cancel(self, account_id: str, order_id: str,
                  instrument_id: str) -> list[SurveillanceAlert]:
        """Process an order cancellation for surveillance checks."""
        key = f"{account_id}:{instrument_id}"
        self._cancel_counts[key] += 1
        # Mark order as cancelled
        for order in self._order_history.get(account_id, []):
            if order["order_id"] == order_id:
                order["status"] = "cancelled"
                break
        alerts = []
        spoof = self._check_spoofing(account_id, instrument_id)
        if spoof:
            alerts.append(spoof)
        return alerts

    def on_trade(self, maker_account: str, taker_account: str,
                 instrument_id: str, price: Decimal, quantity: Decimal,
                 fill_id: str) -> list[SurveillanceAlert]:
        """Process a trade fill for surveillance checks."""
        now = datetime.utcnow()
        trade = {
            "fill_id": fill_id, "instrument_id": instrument_id,
            "price": str(price), "quantity": str(quantity),
            "timestamp": now,
        }
        self._trade_history[maker_account].append(trade)
        self._trade_history[taker_account].append(trade)

        alerts = []
        # Check for wash trading (same account on both sides)
        if maker_account == taker_account:
            alert = SurveillanceAlert(
                alert_type="WASH_TRADE",
                severity=AlertSeverity.HIGH,
                account_id=maker_account,
                instrument_id=instrument_id,
                description=f"Self-trade detected: {quantity} @ {price}",
                evidence={"fill_id": fill_id, "price": str(price),
                          "quantity": str(quantity)},
            )
            alerts.append(alert)
            self._alerts.append(alert)

        # Check for large trades
        notional = price * quantity
        if notional > self._thresholds["large_order_threshold"]:
            alert = SurveillanceAlert(
                alert_type="LARGE_TRADE",
                severity=AlertSeverity.MEDIUM,
                account_id=taker_account,
                instrument_id=instrument_id,
                description=f"Large trade: notional {notional}",
                evidence={"fill_id": fill_id, "notional": str(notional)},
            )
            alerts.append(alert)
            self._alerts.append(alert)

        return alerts

    def _check_spoofing(self, account_id: str, instrument_id: str) -> Optional[SurveillanceAlert]:
        """Detect spoofing: high cancel-to-fill ratio."""
        orders = [o for o in self._order_history.get(account_id, [])
                  if o["instrument_id"] == instrument_id]
        recent = orders[-self._thresholds["spoof_window_orders"]:]
        if len(recent) < self._thresholds["spoof_window_orders"]:
            return None
        cancelled = sum(1 for o in recent if o["status"] == "cancelled")
        ratio = cancelled / len(recent) if recent else 0
        if ratio >= self._thresholds["spoof_cancel_ratio"]:
            alert = SurveillanceAlert(
                alert_type="SPOOFING",
                severity=AlertSeverity.HIGH,
                account_id=account_id,
                instrument_id=instrument_id,
                description=f"High cancel ratio: {ratio:.1%} in last {len(recent)} orders",
                evidence={"cancel_ratio": ratio, "window": len(recent)},
            )
            self._alerts.append(alert)
            return alert
        return None

    def _check_layering(self, account_id: str, instrument_id: str,
                        side: str) -> Optional[SurveillanceAlert]:
        """Detect layering: multiple resting orders at different price levels."""
        orders = [o for o in self._order_history.get(account_id, [])
                  if o["instrument_id"] == instrument_id
                  and o["side"] == side and o["status"] == "active"]
        unique_prices = set(o["price"] for o in orders)
        if len(unique_prices) >= self._thresholds["layering_levels"]:
            alert = SurveillanceAlert(
                alert_type="LAYERING",
                severity=AlertSeverity.MEDIUM,
                account_id=account_id,
                instrument_id=instrument_id,
                description=f"Layering detected: {len(unique_prices)} price levels on {side}",
                evidence={"price_levels": len(unique_prices), "side": side},
            )
            self._alerts.append(alert)
            return alert
        return None

    def get_alerts(self, status: str = "open", limit: int = 100) -> list[SurveillanceAlert]:
        filtered = [a for a in self._alerts if a.status == status]
        return filtered[-limit:]

    def review_alert(self, alert_id: str, reviewer: str,
                     action: str = "acknowledged") -> Optional[SurveillanceAlert]:
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.status = action
                alert.reviewed_by = reviewer
                alert.reviewed_at = datetime.utcnow()
                return alert
        return None
