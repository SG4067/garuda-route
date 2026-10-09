"""Rainfall observation data model and validation."""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass
class RainfallObservation:
    """Represents a single point-in-time rainfall reading from any weather source.
    
    Attributes:
        location_id: Identifier for the weather station or road location.
        timestamp: Observation time as a timezone-aware datetime.
        rainfall_intensity_mm_hr: Rain rate in mm/hour (must be >= 0.0).
        is_raining: Boolean indicating active rain. Defaults to (intensity > 0.0).
        latitude: Optional geographic latitude (-90.0 to 90.0).
        longitude: Optional geographic longitude (-180.0 to 180.0).
        accumulated_rainfall_mm: Optional cumulative rainfall in mm.
        source: Provenance of data (e.g., 'IMD_API', 'SIMULATION').
    """
    location_id: str
    timestamp: datetime
    rainfall_intensity_mm_hr: float
    is_raining: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accumulated_rainfall_mm: Optional[float] = None
    source: str = "manual"

    def __post_init__(self):
        """Validate fields upon initialization."""
        if not self.location_id or not isinstance(self.location_id, str) or not self.location_id.strip():
            raise ValueError("location_id must be a non-empty string.")

        if not isinstance(self.timestamp, datetime):
            raise ValueError(f"timestamp must be a datetime instance, got {type(self.timestamp)}.")

        # Ensure timezone awareness (default to UTC if naive)
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)

        if not isinstance(self.rainfall_intensity_mm_hr, (int, float)):
            raise ValueError(f"rainfall_intensity_mm_hr must be numeric, got {type(self.rainfall_intensity_mm_hr)}.")

        if self.rainfall_intensity_mm_hr < 0.0:
            raise ValueError(f"rainfall_intensity_mm_hr cannot be negative, got {self.rainfall_intensity_mm_hr}.")

        if self.latitude is not None and not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"latitude must be between -90.0 and 90.0, got {self.latitude}.")

        if self.longitude is not None and not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"longitude must be between -180.0 and 180.0, got {self.longitude}.")

        if self.accumulated_rainfall_mm is not None and self.accumulated_rainfall_mm < 0.0:
            raise ValueError(f"accumulated_rainfall_mm cannot be negative, got {self.accumulated_rainfall_mm}.")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RainfallObservation":
        """Parse and validate observation dictionary from JSON payload or API."""
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")

        required_fields = ["location_id", "timestamp", "rainfall_intensity_mm_hr"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: '{field}'")

        raw_ts = data["timestamp"]
        if isinstance(raw_ts, str):
            try:
                # Support standard ISO format e.g. 2026-10-09T10:00:00Z or +00:00
                parsed_ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            except Exception as exc:
                raise ValueError(f"Invalid timestamp format '{raw_ts}': {exc}") from exc
        elif isinstance(raw_ts, datetime):
            parsed_ts = raw_ts
        else:
            raise ValueError(f"Timestamp must be ISO string or datetime, got {type(raw_ts)}")

        intensity = float(data["rainfall_intensity_mm_hr"])
        
        # If is_raining flag is explicitly provided, respect it; otherwise infer from intensity > 0
        is_raining = data.get("is_raining")
        if is_raining is None:
            is_raining = intensity > 0.0
        else:
            is_raining = bool(is_raining)

        return cls(
            location_id=str(data["location_id"]).strip(),
            timestamp=parsed_ts,
            rainfall_intensity_mm_hr=intensity,
            is_raining=is_raining,
            latitude=float(data["latitude"]) if data.get("latitude") is not None else None,
            longitude=float(data["longitude"]) if data.get("longitude") is not None else None,
            accumulated_rainfall_mm=float(data["accumulated_rainfall_mm"]) if data.get("accumulated_rainfall_mm") is not None else None,
            source=str(data.get("source", "manual")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "location_id": self.location_id,
            "timestamp": self.timestamp.isoformat(),
            "rainfall_intensity_mm_hr": self.rainfall_intensity_mm_hr,
            "is_raining": self.is_raining,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accumulated_rainfall_mm": self.accumulated_rainfall_mm,
            "source": self.source,
        }
