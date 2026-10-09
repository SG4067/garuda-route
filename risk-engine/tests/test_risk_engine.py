"""Unit tests for RiskEngine."""

import unittest
import json
import tempfile
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.road import RoadRecord
from models.risk import RiskLevel
from models.rainfall import RainfallObservation
from tracker.rainfall_tracker import RainfallTracker
from engine.risk_engine import (
    RiskEngine,
    RoadNotFoundError,
    EmptyRoadDatasetError,
)
from datetime import datetime, timezone


class TestRiskEngine(unittest.TestCase):
    """Test suite for RiskEngine functionality and error scenarios."""

    def setUp(self):
        self.roads = [
            RoadRecord(road_id="DEL-001", road_name="Road A", threshold_minutes=60.0, severity="HIGH"),
            RoadRecord(road_id="DEL-002", road_name="Road B", threshold_minutes=90.0, severity="MEDIUM"),
        ]
        self.engine = RiskEngine(roads=self.roads)

    def test_15_normal_road(self):
        """15. Normal road risk evaluation produces structured NORMAL assessment."""
        result = self.engine.evaluate_risk(road_id="DEL-001", current_duration_minutes=20.0)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.road_id, "DEL-001")
        self.assertEqual(result.road_name, "Road A")
        self.assertEqual(result.current_duration_minutes, 20.0)
        self.assertEqual(result.historical_threshold_minutes, 60.0)
        self.assertEqual(result.risk_level, RiskLevel.NORMAL)
        self.assertEqual(result.severity, "HIGH")

        # Verify JSON serialization format matching project requirement
        d = result.to_dict()
        self.assertEqual(d["status"], "success")
        self.assertEqual(d["road_id"], "DEL-001")
        self.assertEqual(d["risk_level"], "NORMAL")
        self.assertEqual(d["current_duration_minutes"], 20.0)

    def test_16_monitor_road(self):
        """16. Monitor road risk evaluation produces structured MONITOR assessment."""
        result = self.engine.evaluate_risk(road_id="DEL-001", current_duration_minutes=45.0)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.risk_level, RiskLevel.MONITOR)
        self.assertIn("Approaching historical waterlogging conditions", result.reason)

    def test_17_high_risk_road(self):
        """17. High-risk road evaluation produces structured HIGH_RISK assessment."""
        result = self.engine.evaluate_risk(road_id="DEL-001", current_duration_minutes=65.0)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.risk_level, RiskLevel.HIGH_RISK)
        self.assertIn("reached or exceeded", result.reason)

    def test_18_unknown_road(self):
        """18. Querying unknown road ID raises RoadNotFoundError."""
        with self.assertRaises(RoadNotFoundError) as ctx:
            self.engine.evaluate_risk(road_id="DEL-999", current_duration_minutes=30.0)
        self.assertIn("DEL-999", str(ctx.exception))

    def test_19_invalid_input(self):
        """19. Invalid continuous duration (negative or non-numeric) raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.evaluate_risk(road_id="DEL-001", current_duration_minutes=-10.0)

        with self.assertRaises(ValueError):
            self.engine.evaluate_risk(road_id="DEL-001", current_duration_minutes="invalid")

    def test_20_empty_road_dataset(self):
        """20. An engine initialized with no roads raises EmptyRoadDatasetError on evaluation."""
        empty_engine = RiskEngine()
        with self.assertRaises(EmptyRoadDatasetError):
            empty_engine.evaluate_risk(road_id="DEL-001", current_duration_minutes=15.0)

    def test_load_from_roads_file(self):
        """Test loading directly from data/roads.json file."""
        root_roads_path = Path(__file__).resolve().parent.parent.parent / "data" / "roads.json"
        engine = RiskEngine.from_roads_file(root_roads_path)
        self.assertGreaterEqual(engine.registered_roads_count, 2)
        assessment = engine.evaluate_risk("DEL-001", 50.0)
        self.assertEqual(assessment.risk_level, RiskLevel.MONITOR)

    def test_evaluate_with_tracker_integration(self):
        """Test end-to-end evaluation using a live RainfallTracker instance."""
        tracker = RainfallTracker()
        loc = "DEL-001-SENSOR"
        
        # 10:00 to 10:45 with 15-20 min intervals (within 30 min max gap) = 45 minutes
        tracker.record_observation(RainfallObservation(
            location_id=loc,
            timestamp=datetime.fromisoformat("2026-10-09T10:00:00Z"),
            rainfall_intensity_mm_hr=12.0,
            is_raining=True
        ))
        tracker.record_observation(RainfallObservation(
            location_id=loc,
            timestamp=datetime.fromisoformat("2026-10-09T10:20:00Z"),
            rainfall_intensity_mm_hr=14.0,
            is_raining=True
        ))
        tracker.record_observation(RainfallObservation(
            location_id=loc,
            timestamp=datetime.fromisoformat("2026-10-09T10:45:00Z"),
            rainfall_intensity_mm_hr=15.0,
            is_raining=True
        ))

        assessment = self.engine.evaluate_with_tracker(
            road_id="DEL-001",
            location_id=loc,
            tracker=tracker
        )
        self.assertEqual(assessment.risk_level, RiskLevel.MONITOR)
        self.assertEqual(assessment.current_duration_minutes, 45.0)


if __name__ == "__main__":
    unittest.main()
