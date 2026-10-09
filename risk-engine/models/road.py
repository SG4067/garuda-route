"""Road vulnerability record data model and validation."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class RoadRecord:
    """Historical vulnerability record for a monitored road segment.
    
    Attributes:
        road_id: Unique road identifier (e.g., 'DEL-001').
        road_name: Human-readable road name (e.g., 'Outer Ring Road - Chirag Delhi').
        threshold_minutes: Historical continuous rainfall duration (in minutes) 
                           associated with onset of waterlogging, or None if unknown.
        severity: Historical severity rating (e.g., 'HIGH', 'MEDIUM', 'LOW').
    """
    road_id: str
    road_name: str
    threshold_minutes: Optional[float] = None
    severity: str = "MEDIUM"

    def __post_init__(self):
        if not self.road_id or not isinstance(self.road_id, str) or not self.road_id.strip():
            raise ValueError("road_id must be a non-empty string.")

        if not self.road_name or not isinstance(self.road_name, str) or not self.road_name.strip():
            raise ValueError("road_name must be a non-empty string.")

        if self.threshold_minutes is not None:
            if not isinstance(self.threshold_minutes, (int, float)):
                raise ValueError(f"threshold_minutes must be numeric or None, got {type(self.threshold_minutes)}.")

            if self.threshold_minutes <= 0:
                raise ValueError(f"threshold_minutes must be greater than 0, got {self.threshold_minutes}.")

        if not self.severity or not isinstance(self.severity, str):
            raise ValueError("severity must be a non-empty string.")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoadRecord":
        """Parse and validate road record from dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")

        required_fields = ["road_id", "road_name", "threshold_minutes"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required road field: '{field}'")

        raw_threshold = data["threshold_minutes"]
        if raw_threshold is not None:
            try:
                threshold = float(raw_threshold)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"threshold_minutes must be numeric or null, got '{raw_threshold}'") from exc
        else:
            threshold = None

        return cls(
            road_id=str(data["road_id"]).strip(),
            road_name=str(data["road_name"]).strip(),
            threshold_minutes=threshold,
            severity=str(data.get("severity", "MEDIUM")).strip().upper(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "road_id": self.road_id,
            "road_name": self.road_name,
            "threshold_minutes": self.threshold_minutes,
            "severity": self.severity,
        }
