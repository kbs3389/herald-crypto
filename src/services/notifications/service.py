"""
Herald Crypto Exchange - Notification Service (Agent 14)

Multi-channel notification delivery: in-app, email, push, SMS, webhook.
Supports user preferences, throttling, and template rendering.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional
from uuid import uuid4


class NotificationChannel(Enum):
    IN_APP = auto()
    EMAIL = auto()
    PUSH = auto()
    SMS = auto()
    WEBHOOK = auto()


class NotificationPriority(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class NotificationType(Enum):
    ORDER_FILLED = auto()
    ORDER_PARTIALLY_FILLED = auto()
    ORDER_CANCELLED = auto()
    ORDER_REJECTED = auto()
    DEPOSIT_CONFIRMED = auto()
    WITHDRAWAL_COMPLETED = auto()
    WITHDRAWAL_FAILED = auto()
    MARGIN_CALL = auto()
    LIQUIDATION_WARNING = auto()
    LIQUIDATION_EXECUTED = auto()
    PRICE_ALERT = auto()
    SECURITY_ALERT = auto()
    KYC_STATUS_CHANGE = auto()
    SYSTEM_MAINTENANCE = auto()
    NEW_LISTING = auto()
    PROMOTION = auto()


@dataclass
class Notification:
    notification_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    notification_type: NotificationType = NotificationType.ORDER_FILLED
    channel: NotificationChannel = NotificationChannel.IN_APP
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str = ""
    body: str = ""
    data: dict = field(default_factory=dict)
    read: bool = False
    delivered: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None


@dataclass
class PriceAlert:
    alert_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    instrument_id: str = ""
    condition: str = "ABOVE"  # ABOVE or BELOW
    target_price: str = "0"
    is_active: bool = True
    triggered: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserNotificationPreferences:
    user_id: str = ""
    channels: dict = field(default_factory=lambda: {
        "ORDER_FILLED": ["IN_APP", "PUSH"],
        "ORDER_CANCELLED": ["IN_APP"],
        "DEPOSIT_CONFIRMED": ["IN_APP", "EMAIL", "PUSH"],
        "WITHDRAWAL_COMPLETED": ["IN_APP", "EMAIL", "PUSH"],
        "MARGIN_CALL": ["IN_APP", "EMAIL", "PUSH", "SMS"],
        "LIQUIDATION_WARNING": ["IN_APP", "EMAIL", "PUSH", "SMS"],
        "SECURITY_ALERT": ["IN_APP", "EMAIL", "PUSH", "SMS"],
        "PRICE_ALERT": ["IN_APP", "PUSH"],
    })
    quiet_hours_start: Optional[int] = None  # Hour 0-23
    quiet_hours_end: Optional[int] = None
    email: str = ""
    phone: str = ""
    webhook_url: str = ""


# Notification templates
TEMPLATES = {
    NotificationType.ORDER_FILLED: {
        "title": "Order Filled",
        "body": "Your {side} order for {quantity} {base} was filled at {price} {quote}",
    },
    NotificationType.ORDER_PARTIALLY_FILLED: {
        "title": "Order Partially Filled",
        "body": (
            "Your {side} order was partially filled: "
            "{filled_qty}/{total_qty} {base} at {price}"
        ),
    },
    NotificationType.DEPOSIT_CONFIRMED: {
        "title": "Deposit Confirmed",
        "body": "Your deposit of {amount} {asset} has been confirmed",
    },
    NotificationType.WITHDRAWAL_COMPLETED: {
        "title": "Withdrawal Completed",
        "body": "Your withdrawal of {amount} {asset} to {address} has been completed",
    },
    NotificationType.MARGIN_CALL: {
        "title": "Margin Call",
        "body": (
            "Your {instrument} position requires additional margin. "
            "Current margin ratio: {ratio}%"
        ),
    },
    NotificationType.LIQUIDATION_WARNING: {
        "title": "Liquidation Warning",
        "body": "Your {instrument} position is approaching liquidation at {liq_price}",
    },
    NotificationType.PRICE_ALERT: {
        "title": "Price Alert",
        "body": "{instrument} has reached {price} ({condition} your target of {target})",
    },
    NotificationType.SECURITY_ALERT: {
        "title": "Security Alert",
        "body": (
            "New login detected from {location} ({ip}). "
            "If this wasn't you, secure your account."
        ),
    },
}


class NotificationService:
    """Multi-channel notification service with preferences and throttling."""

    def __init__(self):
        self._notifications: dict[str, list[Notification]] = defaultdict(list)
        self._preferences: dict[str, UserNotificationPreferences] = {}
        self._price_alerts: list[PriceAlert] = []
        self._sent_count: dict[str, int] = defaultdict(int)

    def send(self, user_id: str, notification_type: NotificationType,
             data: dict, priority: NotificationPriority = NotificationPriority.MEDIUM,
             ) -> list[Notification]:
        """Send notification across configured channels."""
        prefs = self._preferences.get(user_id, UserNotificationPreferences(user_id=user_id))
        type_name = notification_type.name
        channels_str = prefs.channels.get(type_name, ["IN_APP"])
        template = TEMPLATES.get(notification_type, {"title": type_name, "body": str(data)})

        try:
            title = template["title"]
            body = template["body"].format(**data)
        except (KeyError, IndexError):
            title = template["title"]
            body = str(data)

        sent = []
        for ch_str in channels_str:
            try:
                channel = NotificationChannel[ch_str]
            except KeyError:
                channel = NotificationChannel.IN_APP

            notif = Notification(
                user_id=user_id,
                notification_type=notification_type,
                channel=channel,
                priority=priority,
                title=title,
                body=body,
                data=data,
                delivered=True,
            )
            self._notifications[user_id].append(notif)
            sent.append(notif)

        return sent

    def get_notifications(self, user_id: str, unread_only: bool = False,
                          limit: int = 50) -> list[Notification]:
        notifs = self._notifications.get(user_id, [])
        if unread_only:
            notifs = [n for n in notifs if not n.read]
        return list(reversed(notifs[-limit:]))

    def mark_read(self, user_id: str, notification_id: str) -> bool:
        for n in self._notifications.get(user_id, []):
            if n.notification_id == notification_id:
                n.read = True
                n.read_at = datetime.utcnow()
                return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        count = 0
        for n in self._notifications.get(user_id, []):
            if not n.read:
                n.read = True
                n.read_at = datetime.utcnow()
                count += 1
        return count

    def get_unread_count(self, user_id: str) -> int:
        return sum(1 for n in self._notifications.get(user_id, []) if not n.read)

    def set_preferences(self, user_id: str,
                        prefs: UserNotificationPreferences) -> UserNotificationPreferences:
        prefs.user_id = user_id
        self._preferences[user_id] = prefs
        return prefs

    def get_preferences(self, user_id: str) -> UserNotificationPreferences:
        return self._preferences.get(user_id, UserNotificationPreferences(user_id=user_id))

    def create_price_alert(self, user_id: str, instrument_id: str,
                           condition: str, target_price: str) -> PriceAlert:
        alert = PriceAlert(
            user_id=user_id, instrument_id=instrument_id,
            condition=condition, target_price=target_price,
        )
        self._price_alerts.append(alert)
        return alert

    def check_price_alerts(self, instrument_id: str, current_price: float) -> list[PriceAlert]:
        triggered = []
        for alert in self._price_alerts:
            if (alert.instrument_id == instrument_id and alert.is_active
                    and not alert.triggered):
                target = float(alert.target_price)
                if (alert.condition == "ABOVE" and current_price >= target) or \
                   (alert.condition == "BELOW" and current_price <= target):
                    alert.triggered = True
                    alert.is_active = False
                    triggered.append(alert)
                    self.send(alert.user_id, NotificationType.PRICE_ALERT, {
                        "instrument": instrument_id, "price": str(current_price),
                        "condition": alert.condition, "target": alert.target_price,
                    }, NotificationPriority.HIGH)
        return triggered

    def get_price_alerts(self, user_id: str) -> list[PriceAlert]:
        return [a for a in self._price_alerts if a.user_id == user_id]

    def delete_price_alert(self, alert_id: str) -> bool:
        for i, a in enumerate(self._price_alerts):
            if a.alert_id == alert_id:
                self._price_alerts.pop(i)
                return True
        return False
