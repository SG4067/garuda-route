"""Simulation Script for Waterlogging Alert System.

Demonstrates end-to-end integration via the WaterloggingRiskService public facade:
- Service initialization and road-to-sensor mapping
- Live rainfall observation ingestion (including idempotent duplicate handling)
- Continuous tracking and risk level transitions (NORMAL -> MONITOR -> HIGH_RISK -> RESET)
- Read-time data freshness checks (FRESH vs STALE)
- Bulk road querying for frontend/map consumption
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from engine.service import WaterloggingRiskService


def print_step_header(step_num: int, title: str):
    print("\n" + "=" * 75)
    print(f"STEP {step_num}: {title}")
    print("=" * 75)


def print_json(data):
    print(json.dumps(data, indent=2))


def run_simulation():
    print("=" * 75)
    print("REAL-TIME ROAD WATERLOGGING RISK SIMULATION (M3 FACADE)")
    print("=" * 75)

    roads_file = CURRENT_DIR.parent / "data" / "roads.json"
    sensor_loc = "IMD_DEL_SENSOR_01"
    
    # 1. Initialize Service with explicit road-to-location mapping
    road_mapping = {
        "DEL-001": sensor_loc,
        "DEL-002": "IMD_DEL_SENSOR_02",
    }

    service = WaterloggingRiskService.from_roads_file(
        roads_file_path=roads_file,
        road_to_location=road_mapping,
        stale_threshold_minutes=30.0,
        max_observation_gap_minutes=30.0,
        monitor_ratio=0.70,
    )
    print(f"Loaded roads from: {roads_file}")
    print(f"Configured Road Mapping: {road_mapping}")

    # Sequence of test events
    events = [
        # Part 1: Rain begins and continues up to 40 minutes -> NORMAL
        ("2026-10-09T10:00:00Z", 15.0, True, "Rain starts at 10:00 (15 mm/hr)"),
        ("2026-10-09T10:10:00Z", 20.0, True, "Rain continues at 10:10 (20 mm/hr)"),
        ("2026-10-09T10:20:00Z", 25.0, True, "Rain continues at 10:20 (25 mm/hr)"),
        ("2026-10-09T10:30:00Z", 18.0, True, "Rain continues at 10:30 (18 mm/hr)"),
        ("2026-10-09T10:40:00Z", 22.0, True, "Rain reaches 40 minutes duration"),

        # Part 2: Rain crosses 42m monitor threshold (70% of 60m) -> MONITOR
        ("2026-10-09T10:50:00Z", 30.0, True, "Rain reaches 50 minutes (crosses 70% threshold -> MONITOR)"),

        # Part 3: Rain reaches 60m historical threshold -> HIGH_RISK
        ("2026-10-09T11:00:00Z", 28.0, True, "Rain reaches 60 minutes historical threshold -> HIGH_RISK"),

        # Part 4: Rain stops -> RESET to NORMAL
        ("2026-10-09T11:20:00Z", 0.0, False, "Rain stops at 11:20 (0 mm/hr) -> Resets to NORMAL"),

        # Part 5: Rain resumes later -> NEW EVENT STARTS
        ("2026-10-09T12:00:00Z", 12.0, True, "New rain event begins at 12:00 -> Starts fresh at 0m"),
    ]

    for i, (ts, intensity, is_raining, label) in enumerate(events, 1):
        print_step_header(i, label)
        obs_payload = {
            "location_id": sensor_loc,
            "timestamp": ts,
            "rainfall_intensity_mm_hr": intensity,
            "is_raining": is_raining,
            "source": "SIMULATION",
        }
        receipt = service.ingest_observation(obs_payload)
        print("Ingestion Receipt:")
        print_json(receipt)

        # Query single road risk via facade
        eval_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        risk = service.get_road_risk("DEL-001", as_of=eval_time)
        print("\nRoad DEL-001 Risk Status:")
        print_json(risk)

    # Demonstrate Idempotent Duplicate Handling
    print_step_header(len(events) + 1, "Idempotent Ingestion of Exact Duplicate Observation")
    dup_payload = {
        "location_id": sensor_loc,
        "timestamp": "2026-10-09T12:00:00Z",
        "rainfall_intensity_mm_hr": 12.0,
        "is_raining": True,
        "source": "SIMULATION",
    }
    dup_receipt = service.ingest_observation(dup_payload)
    print("Duplicate Ingestion Receipt (Safe & Idempotent):")
    print_json(dup_receipt)

    # Demonstrate Stale Data Freshness Check
    print_step_header(len(events) + 2, "Read-Time Data Freshness Check (STALE Data Handling)")
    # Query at 13:00 UTC (60 minutes after 12:00 observation -> exceeds 30m stale threshold)
    stale_eval_time = datetime.fromisoformat("2026-10-09T13:00:00+00:00")
    stale_risk = service.get_road_risk("DEL-001", as_of=stale_eval_time)
    print("Risk Status Queried 60m After Last Telemetry (Notice data_freshness='STALE'):")
    print_json(stale_risk)

    # Demonstrate Bulk Query for All Configured Roads
    print_step_header(len(events) + 3, "Bulk Query for All Roads (GET /roads/risk Frontend Feed)")
    all_roads = service.get_all_roads_risk(as_of=datetime.fromisoformat("2026-10-09T12:05:00+00:00"))
    print_json(all_roads)


if __name__ == "__main__":
    run_simulation()
