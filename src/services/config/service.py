"""
Herald Crypto Exchange - Configuration Service (Agent 15)

Feature flags, instrument configuration, risk parameter management,
and dynamic system configuration with audit trail.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import uuid4


@dataclass
class FeatureFlag:
    name: str
    enabled: bool = False
    description: str = ""
    conditions: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: str = "system"


@dataclass
class InstrumentConfig:
    instrument_id: str
    is_active: bool = True
    trading_enabled: bool = True
    deposits_enabled: bool = True
    withdrawals_enabled: bool = True
    maker_fee_rate: Decimal = Decimal("0.0005")
    taker_fee_rate: Decimal = Decimal("0.001")
    min_order_size: Decimal = Decimal("0.00001")
    max_order_size: Decimal = Decimal("1000")
    tick_size: Decimal = Decimal("0.01")
    lot_size: Decimal = Decimal("0.00001")
    max_leverage: Decimal = Decimal("1")
    maintenance_margin_rate: Decimal = Decimal("1.0")
    circuit_breaker_pct: Decimal = Decimal("0.10")
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: str = "system"


@dataclass
class ConfigChange:
    change_id: str = field(default_factory=lambda: str(uuid4()))
    config_type: str = ""
    config_key: str = ""
    old_value: str = ""
    new_value: str = ""
    changed_by: str = ""
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ConfigService:
    """Dynamic configuration service with feature flags and audit trail."""

    def __init__(self):
        self._feature_flags: dict[str, FeatureFlag] = {}
        self._instrument_configs: dict[str, InstrumentConfig] = {}
        self._system_config: dict[str, Any] = {}
        self._audit_log: list[ConfigChange] = []
        self._init_defaults()

    def _init_defaults(self):
        """Initialize default feature flags and system config."""
        default_flags = [
            ("SPOT_TRADING", True, "Enable spot trading"),
            ("MARGIN_TRADING", True, "Enable margin trading"),
            ("FUTURES_TRADING", True, "Enable futures/perpetual trading"),
            ("OPTIONS_TRADING", False, "Enable options trading"),
            ("P2P_TRADING", False, "Enable peer-to-peer trading"),
            ("COPY_TRADING", False, "Enable copy trading"),
            ("EARN_STAKING", False, "Enable staking/earn products"),
            ("FIAT_ONRAMP", True, "Enable fiat deposit/withdrawal"),
            ("KYC_REQUIRED", True, "Require KYC for trading"),
            ("TWO_FACTOR_REQUIRED", False, "Require 2FA for all users"),
            ("MAINTENANCE_MODE", False, "Global maintenance mode"),
            ("NEW_REGISTRATIONS", True, "Allow new user registrations"),
            ("WEBSOCKET_ENABLED", True, "Enable WebSocket connections"),
            ("API_RATE_LIMITING", True, "Enable API rate limiting"),
            ("CIRCUIT_BREAKER", True, "Enable market circuit breakers"),
        ]
        for name, enabled, desc in default_flags:
            self._feature_flags[name] = FeatureFlag(
                name=name, enabled=enabled, description=desc,
            )

        self._system_config = {
            "max_websocket_connections": 10000,
            "api_rate_limit_per_minute": 1200,
            "api_rate_limit_per_second": 50,
            "order_rate_limit_per_second": 10,
            "max_open_orders_per_user": 200,
            "max_open_orders_per_instrument": 50,
            "session_timeout_minutes": 1440,
            "withdrawal_cooldown_minutes": 0,
            "min_password_length": 8,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
        }

    def is_feature_enabled(self, flag_name: str,
                           context: Optional[dict] = None) -> bool:
        flag = self._feature_flags.get(flag_name)
        if flag is None:
            return False
        if not flag.enabled:
            return False
        if flag.conditions and context:
            for key, value in flag.conditions.items():
                if context.get(key) != value:
                    return False
        return True

    def set_feature_flag(self, flag_name: str, enabled: bool,
                         changed_by: str, reason: str = "") -> FeatureFlag:
        flag = self._feature_flags.get(flag_name)
        old_value = str(flag.enabled) if flag else "N/A"
        if flag is None:
            flag = FeatureFlag(name=flag_name)
            self._feature_flags[flag_name] = flag
        flag.enabled = enabled
        flag.updated_at = datetime.utcnow()
        flag.updated_by = changed_by
        self._audit_log.append(ConfigChange(
            config_type="feature_flag", config_key=flag_name,
            old_value=old_value, new_value=str(enabled),
            changed_by=changed_by, reason=reason,
        ))
        return flag

    def get_all_feature_flags(self) -> dict[str, bool]:
        return {name: flag.enabled for name, flag in self._feature_flags.items()}

    def get_instrument_config(self, instrument_id: str) -> Optional[InstrumentConfig]:
        return self._instrument_configs.get(instrument_id)

    def set_instrument_config(self, config: InstrumentConfig,
                              changed_by: str) -> InstrumentConfig:
        old = self._instrument_configs.get(config.instrument_id)
        config.updated_at = datetime.utcnow()
        config.updated_by = changed_by
        self._instrument_configs[config.instrument_id] = config
        self._audit_log.append(ConfigChange(
            config_type="instrument", config_key=config.instrument_id,
            old_value=str(old) if old else "N/A",
            new_value=str(config),
            changed_by=changed_by,
        ))
        return config

    def get_system_config(self, key: str, default: Any = None) -> Any:
        return self._system_config.get(key, default)

    def set_system_config(self, key: str, value: Any,
                          changed_by: str, reason: str = "") -> None:
        old_value = str(self._system_config.get(key, "N/A"))
        self._system_config[key] = value
        self._audit_log.append(ConfigChange(
            config_type="system", config_key=key,
            old_value=old_value, new_value=str(value),
            changed_by=changed_by, reason=reason,
        ))

    def get_audit_log(self, limit: int = 100,
                      config_type: Optional[str] = None) -> list[ConfigChange]:
        log = self._audit_log
        if config_type:
            log = [c for c in log if c.config_type == config_type]
        return list(reversed(log[-limit:]))
