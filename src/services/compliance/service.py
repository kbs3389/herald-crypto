"""
Herald Crypto Exchange - Compliance & KYC Service (Agent 11)

KYC/KYB verification, AML screening, sanctions checks,
jurisdiction-based feature gating, and regulatory reporting.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID, uuid4


class KycStatus(Enum):
    NOT_STARTED = auto()
    PENDING = auto()
    BASIC_VERIFIED = auto()
    INTERMEDIATE_VERIFIED = auto()
    ADVANCED_VERIFIED = auto()
    INSTITUTIONAL_VERIFIED = auto()
    REJECTED = auto()
    SUSPENDED = auto()


class SanctionsResult(Enum):
    CLEAR = auto()
    MATCH = auto()
    POTENTIAL_MATCH = auto()
    REVIEW_REQUIRED = auto()


class JurisdictionTier(Enum):
    UNRESTRICTED = auto()
    RESTRICTED_DERIVATIVES = auto()
    RESTRICTED_ALL = auto()
    BLOCKED = auto()


@dataclass
class KycRecord:
    user_id: str
    status: KycStatus = KycStatus.NOT_STARTED
    level: int = 0
    country_code: str = ""
    jurisdiction_tier: JurisdictionTier = JurisdictionTier.UNRESTRICTED
    documents_submitted: list = field(default_factory=list)
    verification_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    risk_score: int = 0
    notes: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceAlert:
    alert_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    alert_type: str = ""
    severity: str = "medium"
    description: str = ""
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)


# Jurisdictions that restrict derivatives trading
RESTRICTED_DERIVATIVES_JURISDICTIONS = {"US", "CA", "UK", "JP", "AU", "SG", "HK"}
BLOCKED_JURISDICTIONS = {"CU", "IR", "KP", "SY", "RU"}

# KYC limits by level
KYC_LIMITS = {
    0: {"daily_withdraw": Decimal("0"), "features": ["VIEW_ONLY"]},
    1: {"daily_withdraw": Decimal("2000"), "features": ["SPOT", "DEPOSIT", "WITHDRAW"]},
    2: {"daily_withdraw": Decimal("100000"),
        "features": ["SPOT", "MARGIN", "DEPOSIT", "WITHDRAW", "P2P"]},
    3: {"daily_withdraw": Decimal("1000000"),
        "features": ["SPOT", "MARGIN", "FUTURES", "OPTIONS", "DEPOSIT", "WITHDRAW",
                      "P2P", "EARN", "COPY_TRADING"]},
    4: {"daily_withdraw": Decimal("10000000"),
        "features": ["ALL"]},
}


class ComplianceService:
    """Compliance engine for KYC, AML, sanctions, and jurisdiction gating."""

    def __init__(self):
        self._kyc_records: dict[str, KycRecord] = {}
        self._alerts: list[ComplianceAlert] = []
        self._sanctions_list: set[str] = set()
        self._transaction_monitor: list[dict] = []

    def create_kyc_record(self, user_id: str, country_code: str = "") -> KycRecord:
        jurisdiction = self._classify_jurisdiction(country_code)
        record = KycRecord(
            user_id=user_id,
            country_code=country_code,
            jurisdiction_tier=jurisdiction,
        )
        self._kyc_records[user_id] = record
        return record

    def submit_kyc_documents(self, user_id: str, documents: list[dict]) -> KycRecord:
        record = self._kyc_records.get(user_id)
        if record is None:
            record = self.create_kyc_record(user_id)
        record.documents_submitted.extend(documents)
        record.status = KycStatus.PENDING
        record.updated_at = datetime.utcnow()
        return record

    def approve_kyc(self, user_id: str, level: int, reviewer: str = "system") -> KycRecord:
        record = self._kyc_records.get(user_id)
        if record is None:
            raise ValueError(f"No KYC record for user {user_id}")
        status_map = {
            1: KycStatus.BASIC_VERIFIED,
            2: KycStatus.INTERMEDIATE_VERIFIED,
            3: KycStatus.ADVANCED_VERIFIED,
            4: KycStatus.INSTITUTIONAL_VERIFIED,
        }
        record.status = status_map.get(level, KycStatus.BASIC_VERIFIED)
        record.level = level
        record.verification_date = datetime.utcnow()
        record.updated_at = datetime.utcnow()
        record.notes.append(f"Approved to level {level} by {reviewer}")
        return record

    def check_feature_access(self, user_id: str, feature: str) -> dict:
        """Check if user has access to a specific feature based on KYC and jurisdiction."""
        record = self._kyc_records.get(user_id)
        if record is None:
            return {"allowed": False, "reason": "KYC not started",
                    "required_action": "COMPLETE_KYC"}
        if record.jurisdiction_tier == JurisdictionTier.BLOCKED:
            return {"allowed": False, "reason": "Jurisdiction blocked",
                    "required_action": "NONE"}
        if (feature in ("FUTURES", "OPTIONS", "PERPETUAL") and
                record.jurisdiction_tier == JurisdictionTier.RESTRICTED_DERIVATIVES):
            return {"allowed": False, "reason": "Derivatives restricted in your jurisdiction",
                    "required_action": "NONE"}
        limits = KYC_LIMITS.get(record.level, KYC_LIMITS[0])
        allowed_features = limits["features"]
        if "ALL" in allowed_features or feature in allowed_features:
            return {"allowed": True, "reason": "Access granted"}
        return {"allowed": False, "reason": f"KYC level {record.level} insufficient",
                "required_action": "UPGRADE_KYC",
                "required_level": self._min_level_for_feature(feature)}

    def screen_sanctions(self, name: str, country: str = "") -> SanctionsResult:
        if name.lower() in self._sanctions_list:
            return SanctionsResult.MATCH
        if country.upper() in BLOCKED_JURISDICTIONS:
            return SanctionsResult.MATCH
        return SanctionsResult.CLEAR

    def monitor_transaction(self, user_id: str, tx_type: str,
                            amount: Decimal, asset: str) -> Optional[ComplianceAlert]:
        """Monitor transaction for suspicious activity."""
        self._transaction_monitor.append({
            "user_id": user_id, "type": tx_type,
            "amount": str(amount), "asset": asset,
            "timestamp": datetime.utcnow().isoformat(),
        })
        # Simple rule: flag large withdrawals
        if tx_type == "WITHDRAWAL" and amount > Decimal("50000"):
            alert = ComplianceAlert(
                user_id=user_id,
                alert_type="LARGE_WITHDRAWAL",
                severity="high",
                description=f"Large withdrawal: {amount} {asset}",
            )
            self._alerts.append(alert)
            return alert
        return None

    def get_kyc_record(self, user_id: str) -> Optional[KycRecord]:
        return self._kyc_records.get(user_id)

    def get_withdrawal_limit(self, user_id: str) -> Decimal:
        record = self._kyc_records.get(user_id)
        if record is None:
            return Decimal("0")
        return KYC_LIMITS.get(record.level, KYC_LIMITS[0])["daily_withdraw"]

    def _classify_jurisdiction(self, country_code: str) -> JurisdictionTier:
        code = country_code.upper()
        if code in BLOCKED_JURISDICTIONS:
            return JurisdictionTier.BLOCKED
        if code in RESTRICTED_DERIVATIVES_JURISDICTIONS:
            return JurisdictionTier.RESTRICTED_DERIVATIVES
        return JurisdictionTier.UNRESTRICTED

    def _min_level_for_feature(self, feature: str) -> int:
        for level, limits in sorted(KYC_LIMITS.items()):
            if "ALL" in limits["features"] or feature in limits["features"]:
                return level
        return 4
