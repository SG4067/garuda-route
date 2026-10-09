"""Continuous Rainfall Tracker.

Tracks ongoing rainfall events and derives continuous rainfall duration
across sequential observations for individual locations/sensors.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from models.rainfall import RainfallObservation


class TrackerError(Exception):
    """Base exception for rainfall tracker errors."""
    pass


class OutOfOrderObservationError(TrackerError, ValueError):
    """Raised when an observation timestamp is older than the latest recorded observation."""
    pass


class DuplicateObservationError(TrackerError, ValueError):
    """Raised when an observation has the exact same timestamp as the latest recorded observation."""
    pass


class ObservationConflictError(DuplicateObservationError):
    """Raised when an observation arrives with the same timestamp but conflicting telemetry values."""
    pass


@dataclass
class LocationRainState:
    """Current tracked rainfall state for a specific location.
    
    Attributes:
        location_id: Identifier of the monitored location/sensor.
        is_raining: Whether it is currently raining at this location.
        rain_started_at: When the current continuous rainfall event began.
        last_rain_observed_at: Timestamp of the most recent rainy observation.
        last_observation_timestamp: Timestamp of the most recent observation received (rain or dry).
        continuous_duration_minutes: Total minutes of unbroken continuous rainfall.
        last_intensity_mm_hr: Most recently observed rain intensity.
        last_is_raining: Boolean flag of the most recent observation.
        has_observations: Whether at least one observation has been ingested.
    """
    location_id: str
    is_raining: bool = False
    rain_started_at: Optional[datetime] = None
    last_rain_observed_at: Optional[datetime] = None
    last_observation_timestamp: Optional[datetime] = None
    continuous_duration_minutes: float = 0.0
    last_intensity_mm_hr: float = 0.0
    last_is_raining: bool = False
    has_observations: bool = False

    def get_freshness(self, as_of: datetime, stale_threshold_minutes: float = 30.0) -> str:
        """Determine data freshness at a given evaluation time.
        
        CRITICAL: Staleness does NOT reset continuous duration or modify is_raining.
        
        Returns:
            'NO_DATA': No observation has ever been recorded for this location.
            'FRESH': (as_of - last_observation_timestamp) <= stale_threshold_minutes.
            'STALE': (as_of - last_observation_timestamp) > stale_threshold_minutes.
        """
        if not self.has_observations or self.last_observation_timestamp is None:
            return "NO_DATA"

        eval_time = as_of
        if eval_time.tzinfo is None:
            eval_time = eval_time.replace(tzinfo=self.last_observation_timestamp.tzinfo)

        elapsed_minutes = (eval_time - self.last_observation_timestamp).total_seconds() / 60.0
        if elapsed_minutes <= stale_threshold_minutes:
            return "FRESH"
        return "STALE"

    def to_dict(self) -> Dict:
        """Convert state to a dictionary."""
        return {
            "location_id": self.location_id,
            "is_raining": self.is_raining,
            "rain_started_at": self.rain_started_at.isoformat() if self.rain_started_at else None,
            "last_rain_observed_at": self.last_rain_observed_at.isoformat() if self.last_rain_observed_at else None,
            "last_observation_timestamp": self.last_observation_timestamp.isoformat() if self.last_observation_timestamp else None,
            "continuous_duration_minutes": round(self.continuous_duration_minutes, 1),
            "last_intensity_mm_hr": self.last_intensity_mm_hr,
            "has_observations": self.has_observations,
        }


class RainfallTracker:
    """Stateful tracker that processes point-in-time observations into continuous rainfall duration.
    
    Reset Policy:
    - Explicit Stop: An observation with intensity < min_intensity or is_raining=False
      immediately ends the rain event and resets continuous duration to 0.
    - Missing Observation Gap: If the time between two rainy observations exceeds
      max_observation_gap_minutes, the continuity is considered broken. The previous
      event has ended, and the new observation starts a fresh rainfall event.
    """

    def __init__(
        self,
        max_observation_gap_minutes: float = 30.0,
        min_rain_intensity_mm_hr: float = 0.1,
        allow_idempotent_duplicates: bool = True,
    ):
        """Initialize the tracker.
        
        Args:
            max_observation_gap_minutes: Maximum gap allowed between observations
                before considering the rain event interrupted.
            min_rain_intensity_mm_hr: Minimum intensity considered as actual rain.
            allow_idempotent_duplicates: Whether identical duplicate observations
                are ignored idempotently without raising an error.
        """
        if max_observation_gap_minutes <= 0:
            raise ValueError("max_observation_gap_minutes must be greater than 0.")
        if min_rain_intensity_mm_hr < 0:
            raise ValueError("min_rain_intensity_mm_hr cannot be negative.")

        self.max_gap_minutes = float(max_observation_gap_minutes)
        self.min_intensity = float(min_rain_intensity_mm_hr)
        self.allow_idempotent_duplicates = bool(allow_idempotent_duplicates)
        self._states: Dict[str, LocationRainState] = {}

    def get_state(self, location_id: str) -> LocationRainState:
        """Retrieve the current state for a location, initializing if absent."""
        if not location_id or not isinstance(location_id, str):
            raise ValueError("location_id must be a non-empty string.")
        
        if location_id not in self._states:
            self._states[location_id] = LocationRainState(location_id=location_id)
        return self._states[location_id]

    def record_observation(self, observation: RainfallObservation) -> LocationRainState:
        """Process a single rainfall observation and update continuous rain duration.
        
        Args:
            observation: A validated RainfallObservation instance.
            
        Returns:
            LocationRainState: The updated rainfall state for that location.
            
        Raises:
            TypeError: If observation is not a RainfallObservation.
            ObservationConflictError: If observation has the same timestamp but conflicting values.
            DuplicateObservationError: If duplicate timestamps are disallowed.
            OutOfOrderObservationError: If observation timestamp is older than last recorded timestamp.
        """
        if not isinstance(observation, RainfallObservation):
            raise TypeError(f"Expected RainfallObservation, got {type(observation).__name__}")

        state = self.get_state(observation.location_id)
        current_time = observation.timestamp

        # Check for duplicate, conflict, and out-of-order timestamps
        if state.last_observation_timestamp is not None:
            if current_time == state.last_observation_timestamp:
                is_conflict = (
                    observation.rainfall_intensity_mm_hr != state.last_intensity_mm_hr
                    or observation.is_raining != state.last_is_raining
                )
                if is_conflict:
                    raise ObservationConflictError(
                        f"Conflicting observation received for location '{observation.location_id}' at timestamp "
                        f"'{current_time.isoformat()}': existing (intensity={state.last_intensity_mm_hr}, "
                        f"is_raining={state.last_is_raining}) vs incoming (intensity={observation.rainfall_intensity_mm_hr}, "
                        f"is_raining={observation.is_raining})."
                    )
                if not self.allow_idempotent_duplicates:
                    raise DuplicateObservationError(
                        f"Duplicate observation timestamp '{current_time.isoformat()}' for location '{observation.location_id}'."
                    )
                # Idempotent exact duplicate: return existing state without altering duration or double-counting
                return state

            if current_time < state.last_observation_timestamp:
                raise OutOfOrderObservationError(
                    f"Out-of-order timestamp '{current_time.isoformat()}' is earlier than "
                    f"latest recorded observation '{state.last_observation_timestamp.isoformat()}'."
                )

        # Determine if currently raining in this observation
        is_currently_raining = (
            observation.is_raining and observation.rainfall_intensity_mm_hr >= self.min_intensity
        )

        if is_currently_raining:
            if not state.is_raining or state.last_rain_observed_at is None:
                # Rain has just started
                state.is_raining = True
                state.rain_started_at = current_time
                state.last_rain_observed_at = current_time
                state.continuous_duration_minutes = 0.0
            else:
                # Rain was already ongoing; check gap from last rain observation
                gap_minutes = (current_time - state.last_rain_observed_at).total_seconds() / 60.0
                if gap_minutes <= self.max_gap_minutes:
                    # Continuity maintained: calculate total elapsed continuous minutes
                    state.last_rain_observed_at = current_time
                    state.continuous_duration_minutes = (
                        state.last_rain_observed_at - state.rain_started_at
                    ).total_seconds() / 60.0
                else:
                    # Gap exceeded threshold: reset and start new event
                    state.is_raining = True
                    state.rain_started_at = current_time
                    state.last_rain_observed_at = current_time
                    state.continuous_duration_minutes = 0.0
        else:
            # Rain has stopped: reset continuous duration and state
            state.is_raining = False
            state.rain_started_at = None
            state.last_rain_observed_at = None
            state.continuous_duration_minutes = 0.0

        state.last_intensity_mm_hr = observation.rainfall_intensity_mm_hr
        state.last_is_raining = observation.is_raining
        state.last_observation_timestamp = current_time
        state.has_observations = True
        return state

    def reset(self, location_id: Optional[str] = None):
        """Reset state for a specific location or all locations."""
        if location_id:
            if location_id in self._states:
                self._states[location_id] = LocationRainState(location_id=location_id)
        else:
            self._states.clear()
