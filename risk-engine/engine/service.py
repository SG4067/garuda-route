"""Waterlogging Risk Service Facade.

Provides a unified, high-level public interface for backend and frontend integration.
Encapsulates RainfallTracker, ThresholdComparator, and RiskEngine.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from models.rainfall import RainfallObservation
from models.road import RoadRecord
from models.risk import RiskLevel
from tracker.rainfall_tracker import (
    RainfallTracker,
    LocationRainState,
    ObservationConflictError,
    DuplicateObservationError,
    OutOfOrderObservationError,
)
from engine.threshold_comparator import ThresholdComparator
from engine.risk_engine import RiskEngine, RoadNotFoundError, EmptyRoadDatasetError, RiskEngineError


class RoadMappingNotFoundError(RiskEngineError, KeyError):
    """Legacy exception retained for callers that import the old public name."""
    pass


class WaterloggingRiskService:
    """Unified service interface for waterlogging risk evaluation and weather ingestion.
    
    This facade coordinates:
    - Weather observation ingestion (with idempotent duplicate support)
    - Continuous rainfall tracking
    - Read-time data freshness evaluation (FRESH vs STALE)
    - Road vulnerability threshold comparison
    """

    def __init__(
        self,
        risk_engine: RiskEngine,
        tracker: Optional[RainfallTracker] = None,
        road_to_location: Optional[Dict[str, str]] = None,
        stale_threshold_minutes: float = 30.0,
    ):
        """Initialize service facade.
        
        Args:
            risk_engine: Instantiated RiskEngine managing roads and comparisons.
            tracker: Optional RainfallTracker instance (created if None).
            road_to_location: Explicit mapping of road_id -> location_id.
            stale_threshold_minutes: Max minutes before telemetry is marked STALE.
        """
        if not isinstance(risk_engine, RiskEngine):
            raise TypeError(f"Expected RiskEngine, got {type(risk_engine).__name__}")
        if stale_threshold_minutes <= 0:
            raise ValueError("stale_threshold_minutes must be greater than 0.")

        self._risk_engine = risk_engine
        self._tracker = tracker or RainfallTracker()
        self.stale_threshold_minutes = float(stale_threshold_minutes)
        self._road_to_location: Dict[str, str] = dict(road_to_location or {})

    @classmethod
    def from_roads_file(
        cls,
        roads_file_path: Union[str, Path] = "data/roads.json",
        road_to_location: Optional[Dict[str, str]] = None,
        stale_threshold_minutes: float = 30.0,
        max_observation_gap_minutes: float = 30.0,
        monitor_ratio: float = 0.70,
    ) -> "WaterloggingRiskService":
        """Factory method to construct service directly from a roads JSON file.
        
        Args:
            roads_file_path: Path to roads.json configuration file.
            road_to_location: Explicit mapping of road_id -> location_id.
            stale_threshold_minutes: Minutes after which observations become STALE.
            max_observation_gap_minutes: Gap after which continuous rainfall streak resets.
            monitor_ratio: Early warning threshold ratio (default: 0.70, or 70%).
        """
        comparator = ThresholdComparator(monitor_ratio=monitor_ratio)
        risk_engine = RiskEngine.from_roads_file(file_path=roads_file_path, comparator=comparator)
        tracker = RainfallTracker(
            max_observation_gap_minutes=max_observation_gap_minutes,
            allow_idempotent_duplicates=True,
        )

        return cls(
            risk_engine=risk_engine,
            tracker=tracker,
            road_to_location=road_to_location,
            stale_threshold_minutes=stale_threshold_minutes,
        )

    def register_road_mapping(self, road_id: str, location_id: str):
        """Register or update an explicit mapping from a road ID to a sensor location ID."""
        if not road_id or not isinstance(road_id, str):
            raise ValueError("road_id must be a non-empty string.")
        if not location_id or not isinstance(location_id, str):
            raise ValueError("location_id must be a non-empty string.")

        self._road_to_location[road_id.strip()] = location_id.strip()

    def get_road_mapping(self, road_id: str) -> Optional[str]:
        """Get the mapped location ID for a given road ID."""
        return self._road_to_location.get(road_id)

    @staticmethod
    def _threshold_value(threshold_minutes: Optional[float]) -> Optional[float]:
        """Round configured thresholds while preserving unavailable values as None."""
        return round(threshold_minutes, 1) if threshold_minutes is not None else None

    @staticmethod
    def _unmapped_assessment(road: RoadRecord, eval_time: datetime) -> Dict[str, Any]:
        """Build the common UNKNOWN / UNMAPPED response for single and batch reads."""
        return {
            "status": "error",
            "road_id": road.road_id,
            "road_name": road.road_name,
            "location_id": None,
            "current_duration_minutes": 0.0,
            "historical_threshold_minutes": WaterloggingRiskService._threshold_value(
                road.threshold_minutes
            ),
            "risk_level": RiskLevel.UNKNOWN.value,
            "severity": road.severity,
            "is_raining": False,
            "data_freshness": "UNMAPPED",
            "last_observation_timestamp": None,
            "reason": f"Road ID '{road.road_id}' has no configured rainfall observation location mapping.",
            "evaluated_at": eval_time.isoformat(),
        }

    def ingest_observation(
        self,
        observation: Union[Dict[str, Any], RainfallObservation],
    ) -> Dict[str, Any]:
        """Ingest a single rainfall observation into the stateful tracker.
        
        Handles:
        - Validating JSON dictionary or RainfallObservation model
        - Idempotent acknowledgment for exact duplicate observations (no double-count, no crash)
        - Raising ObservationConflictError if same timestamp has conflicting values
        
        Returns:
            Dict containing ingestion receipt.
        """
        if isinstance(observation, dict):
            obs = RainfallObservation.from_dict(observation)
        elif isinstance(observation, RainfallObservation):
            obs = observation
        else:
            raise TypeError(f"Expected dict or RainfallObservation, got {type(observation).__name__}")

        state_before = self._tracker.get_state(obs.location_id)
        current_time = obs.timestamp

        # Check for duplicate / conflict before updating
        is_exact_duplicate = False
        if state_before.last_observation_timestamp is not None and current_time == state_before.last_observation_timestamp:
            is_conflict = (
                obs.rainfall_intensity_mm_hr != state_before.last_intensity_mm_hr
                or obs.is_raining != state_before.last_is_raining
            )
            if is_conflict:
                raise ObservationConflictError(
                    f"Conflicting observation received for location '{obs.location_id}' at timestamp "
                    f"'{current_time.isoformat()}': existing (intensity={state_before.last_intensity_mm_hr}, "
                    f"is_raining={state_before.last_is_raining}) vs incoming (intensity={obs.rainfall_intensity_mm_hr}, "
                    f"is_raining={obs.is_raining})."
                )
            is_exact_duplicate = True

        state = self._tracker.record_observation(obs)

        if is_exact_duplicate:
            return {
                "status": "duplicate_ignored",
                "location_id": obs.location_id,
                "timestamp": obs.timestamp.isoformat(),
                "rainfall_intensity_mm_hr": obs.rainfall_intensity_mm_hr,
                "is_raining": obs.is_raining,
                "continuous_duration_minutes": round(state.continuous_duration_minutes, 1),
                "message": "Exact duplicate observation received and ignored idempotently.",
            }

        return {
            "status": "ingested",
            "location_id": obs.location_id,
            "timestamp": obs.timestamp.isoformat(),
            "rainfall_intensity_mm_hr": obs.rainfall_intensity_mm_hr,
            "is_raining": obs.is_raining,
            "continuous_duration_minutes": round(state.continuous_duration_minutes, 1),
        }

    def get_road_risk(
        self,
        road_id: str,
        as_of: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Evaluate waterlogging risk for a single road.
        
        Args:
            road_id: Monitored road identifier.
            as_of: Deterministic evaluation timestamp (defaults to current UTC time).
            
        Returns:
            Dict matching standardized risk output schema.
            
        Raises:
            RoadNotFoundError: If road_id is unknown.
        """
        road = self._risk_engine.get_road(road_id)

        eval_time = as_of or datetime.now(timezone.utc)
        if eval_time.tzinfo is None:
            eval_time = eval_time.replace(tzinfo=timezone.utc)

        location_id = self._road_to_location.get(road_id)
        if not location_id:
            return self._unmapped_assessment(road, eval_time)

        state = self._tracker.get_state(location_id)

        # Handle case where no observations have ever arrived for this location
        if not state.has_observations or state.last_observation_timestamp is None:
            return {
                "status": "no_data",
                "road_id": road.road_id,
                "road_name": road.road_name,
                "location_id": location_id,
                "current_duration_minutes": 0.0,
                "historical_threshold_minutes": self._threshold_value(road.threshold_minutes),
                "risk_level": RiskLevel.UNKNOWN.value,
                "severity": road.severity,
                "is_raining": False,
                "data_freshness": "NO_DATA",
                "last_observation_timestamp": None,
                "reason": f"No rainfall observations have been recorded yet for location '{location_id}'.",
                "evaluated_at": eval_time.isoformat(),
            }

        # Calculate data freshness
        elapsed_minutes = (eval_time - state.last_observation_timestamp).total_seconds() / 60.0
        if elapsed_minutes <= self.stale_threshold_minutes:
            data_freshness = "FRESH"
        else:
            data_freshness = "STALE"

        # Evaluate risk using duration observed up to last observation (do not reset to zero!)
        assessment = self._risk_engine.evaluate_risk(
            road_id=road.road_id,
            current_duration_minutes=state.continuous_duration_minutes,
        )

        reason = assessment.reason
        if data_freshness == "STALE":
            reason = (
                f"[STALE DATA - Last observation was {elapsed_minutes:.1f}m ago "
                f"(freshness limit: {self.stale_threshold_minutes:.1f}m)] {reason}"
            )

        return {
            "status": assessment.status,
            "road_id": road.road_id,
            "road_name": road.road_name,
            "location_id": location_id,
            "current_duration_minutes": round(state.continuous_duration_minutes, 1),
            "historical_threshold_minutes": self._threshold_value(road.threshold_minutes),
            "risk_level": assessment.risk_level.value,
            "severity": road.severity,
            "is_raining": state.is_raining,
            "data_freshness": data_freshness,
            "last_observation_timestamp": state.last_observation_timestamp.isoformat(),
            "reason": reason,
            "evaluated_at": eval_time.isoformat(),
        }

    def get_all_roads_risk(
        self,
        as_of: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Evaluate waterlogging risk for all registered roads.
        
        Returns:
            List of standardized risk dictionaries for all configured roads.
        """
        eval_time = as_of or datetime.now(timezone.utc)
        if eval_time.tzinfo is None:
            eval_time = eval_time.replace(tzinfo=timezone.utc)

        results: List[Dict[str, Any]] = []
        for road_id, road in self._risk_engine._roads.items():
            if road_id not in self._road_to_location:
                results.append(self._unmapped_assessment(road, eval_time))
            else:
                road_risk = self.get_road_risk(road_id=road_id, as_of=eval_time)
                results.append(road_risk)

        return results
