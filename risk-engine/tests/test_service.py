"""Unit tests for WaterloggingRiskService facade."""

import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.road import RoadRecord
from models.rainfall import RainfallObservation
from tracker.rainfall_tracker import ObservationConflictError, DuplicateObservationError
from engine.risk_engine import RiskEngine, RoadNotFoundError
from engine.service import WaterloggingRiskService, RoadMappingNotFoundError


class TestWaterloggingRiskService(unittest.TestCase):
    """Test suite covering the WaterloggingRiskService facade."""

    def setUp(self):
        self.roads = [
            RoadRecord(road_id="DEL-001", road_name="Road A", threshold_minutes=60.0, severity="HIGH"),
            RoadRecord(road_id="DEL-002", road_name="Road B", threshold_minutes=90.0, severity="MEDIUM"),
        ]
        self.road_to_loc = {
            "DEL-001": "LOC-DEL-01",
            "DEL-002": "LOC-DEL-02",
        }
        self.roads_file = Path(__file__).resolve().parent.parent.parent / "data" / "roads.json"
        self.service = WaterloggingRiskService.from_roads_file(
            roads_file_path=self.roads_file,
            road_to_location=self.road_to_loc,
            stale_threshold_minutes=30.0,
            monitor_ratio=0.70,
        )

    def test_01_service_initialization(self):
        """1. Service initializes cleanly via factory with configured roads and mappings."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.get_road_mapping("DEL-001"), "LOC-DEL-01")
        self.assertEqual(self.service.get_road_mapping("DEL-002"), "LOC-DEL-02")
        self.assertEqual(self.service.stale_threshold_minutes, 30.0)

    def test_02_ingest_valid_observation_dict(self):
        """2. Ingesting a valid raw observation dictionary succeeds with an ingestion receipt."""
        payload = {
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:00:00Z",
            "rainfall_intensity_mm_hr": 20.0,
            "is_raining": True,
            "source": "IMD_TEST",
        }
        receipt = self.service.ingest_observation(payload)
        self.assertEqual(receipt["status"], "ingested")
        self.assertEqual(receipt["location_id"], "LOC-DEL-01")
        self.assertEqual(receipt["continuous_duration_minutes"], 0.0)

    def test_03_ingest_valid_observation_model(self):
        """3. Ingesting an already validated RainfallObservation model succeeds."""
        obs = RainfallObservation(
            location_id="LOC-DEL-01",
            timestamp=datetime.fromisoformat("2026-10-09T10:10:00+00:00"),
            rainfall_intensity_mm_hr=25.0,
            is_raining=True,
        )
        receipt = self.service.ingest_observation(obs)
        self.assertEqual(receipt["status"], "ingested")
        self.assertEqual(receipt["location_id"], "LOC-DEL-01")

    def test_04_exact_duplicate_observation_idempotent(self):
        """4. Ingesting the exact same observation twice is idempotent and does not crash or double-count."""
        payload = {
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:00:00Z",
            "rainfall_intensity_mm_hr": 15.0,
            "is_raining": True,
        }
        first_receipt = self.service.ingest_observation(payload)
        self.assertEqual(first_receipt["status"], "ingested")

        # Ingest identical payload a second time
        dup_receipt = self.service.ingest_observation(payload)
        self.assertEqual(dup_receipt["status"], "duplicate_ignored")
        self.assertIn("Exact duplicate observation", dup_receipt["message"])
        self.assertEqual(dup_receipt["continuous_duration_minutes"], 0.0)

    def test_05_conflicting_observation_raises_error(self):
        """5. Ingesting an observation with same timestamp and location but conflicting values raises ObservationConflictError."""
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:00:00Z",
            "rainfall_intensity_mm_hr": 15.0,
            "is_raining": True,
        })

        conflict_payload = {
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:00:00Z",
            "rainfall_intensity_mm_hr": 35.0,  # Conflicting intensity!
            "is_raining": True,
        }
        with self.assertRaises(ObservationConflictError):
            self.service.ingest_observation(conflict_payload)

    def test_06_query_individual_road_monitor_and_high_risk(self):
        """6. Querying an individual road reflects tracked rainfall transitions (NORMAL -> MONITOR -> HIGH_RISK)."""
        # 10:00 (0m)
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:00:00Z",
            "rainfall_intensity_mm_hr": 20.0,
            "is_raining": True,
        })
        # 10:20 (20m)
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:20:00Z",
            "rainfall_intensity_mm_hr": 22.0,
            "is_raining": True,
        })
        # 10:45 (45m continuous -> crosses 70% of 60m threshold = 42m -> MONITOR)
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:45:00Z",
            "rainfall_intensity_mm_hr": 25.0,
            "is_raining": True,
        })

        eval_time = datetime.fromisoformat("2026-10-09T10:50:00+00:00")
        risk = self.service.get_road_risk("DEL-001", as_of=eval_time)
        self.assertEqual(risk["status"], "success")
        self.assertEqual(risk["road_id"], "DEL-001")
        self.assertEqual(risk["risk_level"], "MONITOR")
        self.assertEqual(risk["data_freshness"], "FRESH")
        self.assertEqual(risk["current_duration_minutes"], 45.0)

        # 11:05 (65m continuous -> crosses 60m threshold -> HIGH_RISK)
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T11:05:00Z",
            "rainfall_intensity_mm_hr": 30.0,
            "is_raining": True,
        })
        risk_high = self.service.get_road_risk("DEL-001", as_of=datetime.fromisoformat("2026-10-09T11:10:00+00:00"))
        self.assertEqual(risk_high["risk_level"], "HIGH_RISK")
        self.assertEqual(risk_high["current_duration_minutes"], 65.0)

    def test_07_query_all_configured_roads(self):
        """7. get_all_roads_risk() returns risk entries for all configured roads."""
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:00:00Z",
            "rainfall_intensity_mm_hr": 10.0,
            "is_raining": True,
        })
        all_roads = self.service.get_all_roads_risk(as_of=datetime.fromisoformat("2026-10-09T10:15:00+00:00"))
        self.assertIsInstance(all_roads, list)
        self.assertGreaterEqual(len(all_roads), 2)
        road_ids = [r["road_id"] for r in all_roads]
        self.assertIn("DEL-001", road_ids)
        self.assertIn("DEL-002", road_ids)

    def test_08_unknown_road_raises_error(self):
        """8. Querying unknown road ID raises RoadNotFoundError."""
        with self.assertRaises(RoadNotFoundError):
            self.service.get_road_risk("UNKNOWN-ROAD-999")

    def test_09_missing_road_to_location_mapping(self):
        """9. A road without a location mapping raises RoadMappingNotFoundError on get_road_risk, and produces error item in get_all_roads_risk."""
        unmapped_service = WaterloggingRiskService.from_roads_file(
            roads_file_path=self.roads_file,
            road_to_location={},  # No mappings provided!
        )
        with self.assertRaises(RoadMappingNotFoundError):
            unmapped_service.get_road_risk("DEL-001")

        all_roads = unmapped_service.get_all_roads_risk()
        self.assertEqual(all_roads[0]["data_freshness"], "UNMAPPED")
        self.assertEqual(all_roads[0]["status"], "error")
        self.assertIn("no configured rainfall", all_roads[0]["reason"])

    def test_10_stale_data_handling(self):
        """10. Read-time data freshness marks telemetry STALE without resetting duration or rain state."""
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:00:00Z",
            "rainfall_intensity_mm_hr": 20.0,
            "is_raining": True,
        })
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:20:00Z",
            "rainfall_intensity_mm_hr": 22.0,
            "is_raining": True,
        })
        self.service.ingest_observation({
            "location_id": "LOC-DEL-01",
            "timestamp": "2026-10-09T10:45:00Z",
            "rainfall_intensity_mm_hr": 25.0,
            "is_raining": True,
        })

        # Query 50 minutes after last observation (exceeds 30 min stale threshold)
        eval_time_stale = datetime.fromisoformat("2026-10-09T11:35:00+00:00")
        risk = self.service.get_road_risk("DEL-001", as_of=eval_time_stale)

        self.assertEqual(risk["status"], "success")
        self.assertEqual(risk["data_freshness"], "STALE")
        # CRITICAL: duration is NOT reset to 0, is_raining is NOT set to False!
        self.assertEqual(risk["current_duration_minutes"], 45.0)
        self.assertTrue(risk["is_raining"])
        self.assertEqual(risk["risk_level"], "MONITOR")
        self.assertIn("STALE DATA", risk["reason"])

    def test_11_no_data_handling(self):
        """11. Road mapped to a location with zero recorded observations returns status 'no_data' and data_freshness 'NO_DATA'."""
        eval_time = datetime.fromisoformat("2026-10-09T10:00:00+00:00")
        risk = self.service.get_road_risk("DEL-002", as_of=eval_time)
        self.assertEqual(risk["status"], "no_data")
        self.assertEqual(risk["data_freshness"], "NO_DATA")
        self.assertEqual(risk["risk_level"], "UNKNOWN")
        self.assertEqual(risk["current_duration_minutes"], 0.0)

    def test_12_invalid_observation_rejected(self):
        """12. Malformed or invalid observation dictionaries raise ValueError."""
        with self.assertRaises(ValueError):
            self.service.ingest_observation({
                "location_id": "LOC-DEL-01",
                "timestamp": "2026-10-09T10:00:00Z",
                "rainfall_intensity_mm_hr": -10.0,  # Negative intensity!
            })

        with self.assertRaises(ValueError):
            self.service.ingest_observation({
                "location_id": "LOC-DEL-01",
                "timestamp": "invalid-time",
                "rainfall_intensity_mm_hr": 10.0,
            })

    def test_13_missing_historical_threshold_rejected(self):
        """13. Road records missing threshold or having threshold <= 0 raise ValueError."""
        with self.assertRaises(ValueError):
            RoadRecord.from_dict({
                "road_id": "DEL-999",
                "road_name": "Invalid Road",
                "threshold_minutes": 0,
            })

        with self.assertRaises(ValueError):
            RoadRecord.from_dict({
                "road_id": "DEL-999",
                "road_name": "Invalid Road",
            })


if __name__ == "__main__":
    unittest.main()
