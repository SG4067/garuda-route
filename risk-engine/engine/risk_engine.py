"""Risk Engine.

Coordinates historical road vulnerability records, continuous rainfall duration,
and threshold comparison to produce standardized waterlogging risk assessments.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from models.road import RoadRecord
from models.risk import RiskAssessment, RiskLevel
from engine.threshold_comparator import ThresholdComparator
from tracker.rainfall_tracker import RainfallTracker


class RiskEngineError(Exception):
    """Base exception for Risk Engine errors."""
    pass


class RoadNotFoundError(RiskEngineError, KeyError):
    """Raised when an evaluation is requested for an unknown road ID."""
    pass


class EmptyRoadDatasetError(RiskEngineError, ValueError):
    """Raised when the road dataset is empty or cannot be loaded."""
    pass


class RiskEngine:
    """Core engine evaluating road waterlogging risk based on empirical duration thresholds.
    
    The engine produces a 'Historical Waterlogging Risk Level' comparing live
    continuous rainfall duration against empirical road vulnerability thresholds.
    """

    def __init__(
        self,
        roads: Optional[List[RoadRecord]] = None,
        comparator: Optional[ThresholdComparator] = None,
    ):
        """Initialize the Risk Engine.
        
        Args:
            roads: Optional initial list of RoadRecord instances.
            comparator: Optional custom ThresholdComparator instance.
        """
        self.comparator = comparator or ThresholdComparator()
        self._roads: Dict[str, RoadRecord] = {}

        if roads:
            for road in roads:
                self.register_road(road)

    @property
    def registered_roads_count(self) -> int:
        """Count of loaded road records."""
        return len(self._roads)

    def register_road(self, road: RoadRecord):
        """Add or update a road vulnerability record in the engine."""
        if not isinstance(road, RoadRecord):
            raise TypeError(f"Expected RoadRecord, got {type(road).__name__}")
        self._roads[road.road_id] = road

    @classmethod
    def from_roads_file(
        cls,
        file_path: Union[str, Path],
        comparator: Optional[ThresholdComparator] = None,
    ) -> "RiskEngine":
        """Instantiate RiskEngine directly by loading roads from a JSON file.
        
        Args:
            file_path: Path to roads.json file.
            comparator: Optional custom ThresholdComparator.
            
        Raises:
            FileNotFoundError: If file does not exist.
            EmptyRoadDatasetError: If file contains an empty list or invalid structure.
            ValueError: If file is malformed JSON or items are missing fields.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Roads file not found at: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON in roads file: {exc}") from exc

        if not isinstance(data, list):
            raise ValueError("Roads file must contain a JSON array of road records.")

        if len(data) == 0:
            raise EmptyRoadDatasetError("Road dataset is empty. At least one road record is required.")

        roads = [RoadRecord.from_dict(item) for item in data]
        return cls(roads=roads, comparator=comparator)

    def get_road(self, road_id: str) -> RoadRecord:
        """Retrieve a registered road record by ID."""
        if not self._roads:
            raise EmptyRoadDatasetError("No roads are registered in the Risk Engine.")
        if road_id not in self._roads:
            raise RoadNotFoundError(
                f"Road ID '{road_id}' not found in registered roads. Available: {list(self._roads.keys())}"
            )
        return self._roads[road_id]

    def evaluate_risk(
        self,
        road_id: str,
        current_duration_minutes: float,
    ) -> RiskAssessment:
        """Evaluate waterlogging risk for a road given current continuous rainfall duration.
        
        Args:
            road_id: Monitored road identifier.
            current_duration_minutes: Continuous rainfall duration tracked so far.
            
        Returns:
            RiskAssessment: Standardized assessment result.
            
        Raises:
            RoadNotFoundError: If road_id is not registered.
            EmptyRoadDatasetError: If engine has no registered roads.
            ValueError: If current_duration_minutes is invalid.
        """
        road = self.get_road(road_id)

        if current_duration_minutes is None or not isinstance(current_duration_minutes, (int, float)):
            raise ValueError(f"current_duration_minutes must be numeric, got {type(current_duration_minutes)}")

        if current_duration_minutes < 0:
            raise ValueError(f"current_duration_minutes cannot be negative, got {current_duration_minutes}")

        if road.threshold_minutes is None:
            return RiskAssessment(
                status="threshold_unavailable",
                road_id=road.road_id,
                road_name=road.road_name,
                current_duration_minutes=current_duration_minutes,
                historical_threshold_minutes=None,
                risk_level=RiskLevel.UNKNOWN,
                severity=road.severity,
                reason=(
                    f"Historical waterlogging threshold is not yet determined for road '{road.road_id}'. "
                    f"Risk level cannot be reliably evaluated without historical evidence."
                ),
            )

        risk_level, reason = self.comparator.evaluate(
            current_duration_minutes=current_duration_minutes,
            historical_threshold_minutes=road.threshold_minutes,
        )

        return RiskAssessment(
            status="success",
            road_id=road.road_id,
            road_name=road.road_name,
            current_duration_minutes=current_duration_minutes,
            historical_threshold_minutes=road.threshold_minutes,
            risk_level=risk_level,
            severity=road.severity,
            reason=reason,
        )

    def evaluate_with_tracker(
        self,
        road_id: str,
        location_id: str,
        tracker: RainfallTracker,
    ) -> RiskAssessment:
        """Convenience method to evaluate road risk directly from a RainfallTracker state.
        
        Args:
            road_id: Monitored road identifier.
            location_id: Weather station or location identifier in the tracker.
            tracker: The RainfallTracker instance managing observations.
        """
        if not isinstance(tracker, RainfallTracker):
            raise TypeError(f"Expected RainfallTracker instance, got {type(tracker).__name__}")

        state = tracker.get_state(location_id)
        return self.evaluate_risk(
            road_id=road_id,
            current_duration_minutes=state.continuous_duration_minutes,
        )
