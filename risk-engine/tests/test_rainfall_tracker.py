"""Unit tests for RainfallTracker."""

import unittest
from datetime import datetime, timezone

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.rainfall import RainfallObservation
from tracker.rainfall_tracker import (
    RainfallTracker,
    DuplicateObservationError,
    OutOfOrderObservationError,
)


class TestRainfallTracker(unittest.TestCase):
    """Test suite covering all requirements for continuous rainfall tracking."""

    def setUp(self):
        self.tracker = RainfallTracker(max_observation_gap_minutes=30.0, min_rain_intensity_mm_hr=0.1)
        self.loc = "LOC-DEL-01"

    def _make_obs(self, time_str: str, intensity: float, is_raining: bool = True):
        return RainfallObservation(
            location_id=self.loc,
            timestamp=datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc),
            rainfall_intensity_mm_hr=intensity,
            is_raining=is_raining,
        )

    def test_01_first_rainfall_observation(self):
        """1. First rainfall observation initializes event at 0 minutes duration."""
        obs = self._make_obs("2026-10-09T10:00:00", 5.0)
        state = self.tracker.record_observation(obs)

        self.assertTrue(state.is_raining)
        self.assertEqual(state.continuous_duration_minutes, 0.0)
        self.assertIsNotNone(state.rain_started_at)
        self.assertEqual(state.rain_started_at, obs.timestamp)

    def test_02_continuous_rainfall(self):
        """2. Continuous rainfall accumulates correctly (10:00 to 10:30 -> 30 mins)."""
        self.tracker.record_observation(self._make_obs("2026-10-09T10:00:00", 5.0))
        self.tracker.record_observation(self._make_obs("2026-10-09T10:10:00", 6.0))
        self.tracker.record_observation(self._make_obs("2026-10-09T10:20:00", 7.0))
        state = self.tracker.record_observation(self._make_obs("2026-10-09T10:30:00", 8.0))

        self.assertTrue(state.is_raining)
        self.assertAlmostEqual(state.continuous_duration_minutes, 30.0)

    def test_03_rain_stops(self):
        """3. Rain stops resets continuous duration and is_raining flag."""
        self.tracker.record_observation(self._make_obs("2026-10-09T10:00:00", 5.0))
        self.tracker.record_observation(self._make_obs("2026-10-09T10:10:00", 5.0))
        self.tracker.record_observation(self._make_obs("2026-10-09T10:20:00", 5.0))

        # 10:40 rain stops (0 mm/hr)
        stop_obs = self._make_obs("2026-10-09T10:40:00", 0.0, is_raining=False)
        state = self.tracker.record_observation(stop_obs)

        self.assertFalse(state.is_raining)
        self.assertEqual(state.continuous_duration_minutes, 0.0)
        self.assertIsNone(state.rain_started_at)

    def test_04_rain_resumes(self):
        """4. Rain resumes starts a completely new event at 0 minutes."""
        self.tracker.record_observation(self._make_obs("2026-10-09T10:00:00", 5.0))
        self.tracker.record_observation(self._make_obs("2026-10-09T10:20:00", 5.0))
        self.tracker.record_observation(self._make_obs("2026-10-09T10:40:00", 0.0, is_raining=False))

        # 11:00 rain resumes
        resume_obs = self._make_obs("2026-10-09T11:00:00", 10.0)
        state = self.tracker.record_observation(resume_obs)

        self.assertTrue(state.is_raining)
        self.assertEqual(state.continuous_duration_minutes, 0.0)
        self.assertEqual(state.rain_started_at, resume_obs.timestamp)

    def test_05_missing_observation_tolerance(self):
        """5a. Missing observation within gap tolerance (20m <= 30m) keeps streak."""
        self.tracker.record_observation(self._make_obs("2026-10-09T10:00:00", 5.0))
        # 10:10 is missed; next is 10:20 (20 minute gap <= 30 minute tolerance)
        state = self.tracker.record_observation(self._make_obs("2026-10-09T10:20:00", 5.0))
        self.assertAlmostEqual(state.continuous_duration_minutes, 20.0)

    def test_05_missing_observation_gap_exceeded(self):
        """5b. Missing observation exceeding gap tolerance (> 30m) starts new event."""
        self.tracker.record_observation(self._make_obs("2026-10-09T10:00:00", 5.0))
        # 45 minute gap > 30 min max gap: reset and start new event
        state = self.tracker.record_observation(self._make_obs("2026-10-09T10:45:00", 5.0))
        self.assertEqual(state.continuous_duration_minutes, 0.0)
        self.assertEqual(state.rain_started_at, datetime.fromisoformat("2026-10-09T10:45:00").replace(tzinfo=timezone.utc))

    def test_06_duplicate_observation(self):
        """6. Duplicate timestamp raises DuplicateObservationError."""
        obs = self._make_obs("2026-10-09T10:00:00", 5.0)
        self.tracker.record_observation(obs)

        dup_obs = self._make_obs("2026-10-09T10:00:00", 7.0)
        with self.assertRaises(DuplicateObservationError):
            self.tracker.record_observation(dup_obs)

    def test_07_out_of_order_observation(self):
        """7. Out-of-order timestamp raises OutOfOrderObservationError."""
        self.tracker.record_observation(self._make_obs("2026-10-09T10:20:00", 5.0))
        older_obs = self._make_obs("2026-10-09T10:10:00", 5.0)

        with self.assertRaises(OutOfOrderObservationError):
            self.tracker.record_observation(older_obs)

    def test_08_invalid_timestamp(self):
        """8. Invalid timestamp format in dictionary parsing raises ValueError."""
        with self.assertRaises(ValueError):
            RainfallObservation.from_dict({
                "location_id": "LOC-01",
                "timestamp": "invalid-timestamp-format",
                "rainfall_intensity_mm_hr": 10.0,
            })

    def test_09_negative_rainfall_intensity(self):
        """9. Negative rainfall intensity raises ValueError."""
        with self.assertRaises(ValueError):
            RainfallObservation.from_dict({
                "location_id": "LOC-01",
                "timestamp": "2026-10-09T10:00:00Z",
                "rainfall_intensity_mm_hr": -4.5,
            })


if __name__ == "__main__":
    unittest.main()
