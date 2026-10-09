"""Risk assessment output data model and enums."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional


class RiskLevel(str, Enum):
    """Categorical waterlogging risk level based on empirical duration thresholds."""
    NORMAL = "NORMAL"
    MONITOR = "MONITOR"
    HIGH_RISK = "HIGH_RISK"
    UNKNOWN = "UNKNOWN"


@dataclass
class RiskAssessment:
    """Standardized output structure for waterlogging risk evaluation.
    
    Attributes:
        status: Operation status ('success', 'error', 'threshold_unavailable', etc.).
        road_id: Monitored road identifier.
        current_duration_minutes: Continuous rainfall duration tracked so far.
        historical_threshold_minutes: Road's historical rainfall duration threshold, or None if unknown.
        risk_level: Evaluated risk category (NORMAL, MONITOR, HIGH_RISK, UNKNOWN).
        severity: Historical severity rating for the road (e.g., HIGH, MEDIUM).
        reason: Plain-text engineering explanation for the assessment.
        evaluated_at: UTC timestamp when the evaluation was computed.
        road_name: Optional human-readable road name.
    """
    status: str
    road_id: str
    current_duration_minutes: float
    historical_threshold_minutes: Optional[float]
    risk_level: RiskLevel
    severity: str
    reason: str
    evaluated_at: Optional[datetime] = None
    road_name: Optional[str] = None

    def __post_init__(self):
        if self.evaluated_at is None:
            self.evaluated_at = datetime.now(timezone.utc)
        elif self.evaluated_at.tzinfo is None:
            self.evaluated_at = self.evaluated_at.replace(tzinfo=timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to JSON-serializable dictionary."""
        return {
            "status": self.status,
            "road_id": self.road_id,
            "road_name": self.road_name,
            "current_duration_minutes": round(self.current_duration_minutes, 1),
            "historical_threshold_minutes": (
                round(self.historical_threshold_minutes, 1)
                if self.historical_threshold_minutes is not None
                else None
            ),
            "risk_level": self.risk_level.value if isinstance(self.risk_level, RiskLevel) else str(self.risk_level),
            "severity": self.severity,
            "reason": self.reason,
            "evaluated_at": self.evaluated_at.isoformat() if self.evaluated_at else None,
        }
