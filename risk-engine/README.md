# M3 — Road Waterlogging Risk Engine

The M3 module provides a deterministic, rule-based **historical waterlogging risk indicator**. It tracks continuous rainfall observations by observation location and compares tracked duration against a configured road threshold. It is not an ML model, hydraulic simulator, or calibrated flood probability.

## Responsibilities

- Validate rainfall observations.
- Track the duration of continuous rain at each observation location.
- Handle time gaps, duplicate observations, conflicting timestamps, and out-of-order observations.
- Evaluate data freshness at read time.
- Compare duration to a configured threshold and produce a structured assessment.
- Require an explicit road-ID to observation-location-ID mapping.

## Module layout

```text
risk-engine/
├── engine/
│   ├── service.py               # Public WaterloggingRiskService facade
│   ├── threshold_comparator.py  # NORMAL / MONITOR / HIGH_RISK heuristic
│   └── risk_engine.py           # Road registry and assessment orchestration
├── models/
│   ├── rainfall.py              # RainfallObservation validation
│   ├── road.py                  # RoadRecord
│   └── risk.py                  # RiskLevel and assessment output
├── tracker/rainfall_tracker.py  # Per-location rainfall state and gap rules
├── tests/                       # M3 unit tests
├── simulation.py                # Synthetic lifecycle demonstration
└── README.md
```

## Public service interface

Located at `risk-engine/engine/service.py`:

- `WaterloggingRiskService.from_roads_file(...)`
- `register_road_mapping(road_id, location_id)`
- `get_road_mapping(road_id)`
- `ingest_observation(observation)`
- `get_road_risk(road_id, as_of=None)`
- `get_all_roads_risk(as_of=None)`

Because `risk-engine` contains a hyphen, the FastAPI adapter adds that folder to `sys.path` and imports `engine.service`. Prefer the existing adapter instead of creating another risk calculator.

## Initialise the service directly

From repository root:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "risk-engine"))
from engine.service import WaterloggingRiskService

service = WaterloggingRiskService.from_roads_file(
    roads_file_path="path/to/reviewed-road-records.json",
    road_to_location={"REVIEWED_ROAD_ID": "REVIEWED_LOCATION_ID"},
    stale_threshold_minutes=30.0,
    max_observation_gap_minutes=30.0,
    monitor_ratio=0.70,
)

receipt = service.ingest_observation({
    "location_id": "REVIEWED_LOCATION_ID",
    "timestamp": "2026-10-09T10:30:00Z",
    "rainfall_intensity_mm_hr": 25.0,
    "is_raining": True,
    "source": "manual",
})
assessment = service.get_road_risk("REVIEWED_ROAD_ID")
```

All identifiers and values above are examples. A single observation is not enough to establish a long continuous rain duration, and the mapping/threshold must be supported before using output for traveller decisions. Do not use the root `data/roads.json` fixture as evidence-backed road configuration.

## Risk levels and comparator

The monitor threshold is:

`monitor_threshold = historical_threshold_minutes × monitor_ratio`

The default ratio is `0.70` and must be in the open interval `(0, 1)`.

| Level | Condition | Interpretation |
|---|---|---|
| `NORMAL` | duration < monitor threshold | Below the configured early-warning comparison point |
| `MONITOR` | monitor threshold ≤ duration < historical threshold | Approaching the configured empirical indicator |
| `HIGH_RISK` | duration ≥ historical threshold | At or above the configured empirical indicator |
| `UNKNOWN` | insufficient threshold/data/mapping | Not enough information to assign one of the numeric classes |

These are deterministic categories relative to a configured indicator. They do not guarantee flooding, indicate a calibrated probability, or account for drainage, elevation, runoff, or all local factors.

## Freshness and mapping invariants

- Exact duplicate observations are ignored idempotently when accepted by the facade; duration must not be double-counted.
- Conflicting values for the same location/timestamp raise a conflict error.
- Out-of-order observations are rejected.
- A missing observation does **not** mean rain stopped.
- A stale assessment preserves last-known duration with a `STALE` freshness flag/reason instead of inventing a dry state.
- A road without an explicit mapping returns an `UNKNOWN` / `UNMAPPED` assessment with no location ID.
- A missing historical threshold stays null and yields an unknown/threshold-unavailable result; it is not filled with a default number.
- Observation state is held in memory in this implementation and is lost when the process restarts.

## Run simulation and tests

From the repository root:

```bash
python risk-engine/simulation.py
python -m unittest discover -s risk-engine/tests -v
```

The simulation creates synthetic observations to demonstrate state transitions. It is not a live weather integration. For the FastAPI interface and backend regression tests, see [`../backend/README.md`](../backend/README.md).
