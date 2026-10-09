# Road Waterlogging Risk Engine (M3 Module)

Part of the **Real-Time Road Waterlogging Alert and Route Diversion System**.

## 1. Purpose
The Risk Engine monitors continuous rainfall duration against historical empirical road vulnerability thresholds to determine whether a road segment is approaching or reaching conditions under which it has historically experienced waterlogging.

> **Empirical Indicator Notice**:  
> This system does *not* simulate physical flood hydraulics or claim that rain duration strictly causes flooding as a physical law. Instead, it computes a transparent **Historical Waterlogging Risk Level**: an empirical indicator that this specific road segment has historically experienced waterlogging under similar rainfall duration conditions.

---

## 2. Architecture & Facade Pattern

Backend (M2) and Frontend (M4) developers interact exclusively through the **`WaterloggingRiskService`** facade, without managing internal trackers or comparators:

```text
Backend Ingestion Worker (M2)          Frontend / Map Client (M4)
          │                                      │
          ▼ (Raw JSON / Dict)                    ▼ (GET /roads/risk)
┌────────────────────────────────────────────────────────────────────────┐
│                        WaterloggingRiskService                         │
│  ├── ingest_observation(dict | model) -> receipt                      │
│  ├── get_road_risk(road_id, as_of=None) -> assessment dict             │
│  └── get_all_roads_risk(as_of=None) -> list[assessment dict]           │
├────────────────────────────────────────────────────────────────────────┤
│                         INTERNAL DELEGATION                            │
│  [RainfallTracker]       [ThresholdComparator]        [RiskEngine]     │
│   (State & Gap Policy)    (70% & 100% Heuristic)       (Road Records)  │
└────────────────────────────────────────────────────────────────────────┘
```

### Module Structure
```text
risk-engine/
├── models/
│   ├── rainfall.py              # RainfallObservation model & validation
│   ├── road.py                  # RoadRecord model (historical threshold data)
│   └── risk.py                  # RiskLevel enum & RiskAssessment output
├── tracker/
│   └── rainfall_tracker.py      # Stateful continuous rainfall tracker & gap policy
├── engine/
│   ├── service.py               # WaterloggingRiskService public facade
│   ├── threshold_comparator.py  # Ratio-based threshold comparison logic
│   └── risk_engine.py           # Core orchestrator coordinating roads
├── tests/
│   ├── test_service.py          # 13 tests for public facade, staleness & conflicts
│   ├── test_rainfall_tracker.py # 10 tests for duration tracking
│   ├── test_threshold_comparator.py # 7 tests for threshold comparisons
│   └── test_risk_engine.py      # 8 tests for risk engine & error handling
├── simulation.py                # Standalone simulation demonstrating full lifecycle
└── README.md                    # Technical documentation
```

---

## 3. Public Service Quickstart

### Backend Import Note
Because `risk-engine` has a hyphen, Python cannot import it directly via `import risk-engine`. Backend developers should add the folder to `sys.path` or configure `PYTHONPATH`:

```python
import sys
from pathlib import Path

# Add risk-engine to path:
sys.path.insert(0, str(Path(__file__).resolve().parent / "risk-engine"))

from engine.service import WaterloggingRiskService
```

```python
# 1. Initialize service directly from roads dataset
service = WaterloggingRiskService.from_roads_file(
    roads_file_path="data/roads.json",
    road_to_location={"DEL-001": "IMD_DEL_SENSOR_01", "DEL-002": "IMD_DEL_SENSOR_02"},
    stale_threshold_minutes=30.0,
    max_observation_gap_minutes=30.0,
    monitor_ratio=0.70
)

# 2. Ingest live observation (idempotent, safe on retries)
receipt = service.ingest_observation({
    "location_id": "IMD_DEL_SENSOR_01",
    "timestamp": "2026-10-09T10:30:00Z",
    "rainfall_intensity_mm_hr": 25.0,
    "is_raining": True
})

# 3. Query single road risk
risk = service.get_road_risk("DEL-001")

# 4. Query all roads (for frontend map)
all_risks = service.get_all_roads_risk()
```

---

## 4. Key Engineering Policies

### 4.1 Idempotent Duplicate Handling & Conflicts
- **Exact Duplicate**: If an observation arrives with the same `location_id` and `timestamp` with matching values, the service returns `{"status": "duplicate_ignored"}`. It does **not** double-count duration and does **not** crash the ingestion worker.
- **Conflicting Observation**: If the same timestamp arrives with conflicting telemetry values (e.g., intensity 40.0 vs 20.0), `ObservationConflictError` is raised to prevent silent corruption.

### 4.2 Data Freshness vs Rainfall State (Stale Data Policy)
> **CRITICAL RULE**: Missing observations do *not* prove that rain has stopped.

- The system separates:
  1. `is_raining`: Observed rain status at the station.
  2. `current_duration_minutes`: Accumulated unbroken continuous rainfall.
  3. `last_observation_timestamp`: Time of the latest received observation.
  4. `data_freshness`: `"FRESH"`, `"STALE"`, or `"NO_DATA"`.
- If observations stop arriving for $> 30$ minutes, `data_freshness` is marked **`"STALE"`**.
- **The continuous duration is NOT reset to zero** merely because an API or sensor went silent. The last known continuous duration is evaluated and reported with an explicit `[STALE DATA]` advisory in the `reason` field.

### 4.3 Explicit Road-to-Location Mapping
Road segments must be explicitly mapped to weather stations (`road_to_location: {"DEL-001": "IMD_DEL_01"}`).
- The system does **not** assume `road_id == location_id`.
- If a road has no mapping, both `get_road_risk()` and `get_all_roads_risk()` return the same `risk_level: "UNKNOWN"`, `data_freshness: "UNMAPPED"` assessment. No proximity or ID-based mapping is inferred.
- If a road has no historical threshold, the threshold remains `None` in Python and serializes as JSON `null`; its risk remains `UNKNOWN`.

### 4.4 Risk Levels & Threshold Comparison
$$\text{monitor\_threshold} = \text{historical\_threshold} \times 0.70$$

| Level | Condition | Explanation |
|---|---|---|
| `NORMAL` | $\text{duration} < \text{monitor\_threshold}$ | Continuous rainfall comfortably below historical thresholds. |
| `MONITOR` | $\text{monitor\_threshold} \le \text{duration} < \text{historical\_threshold}$ | Early warning triggered. Continuous rain approaching historical waterlogging levels. |
| `HIGH_RISK` | $\text{duration} \ge \text{historical\_threshold}$ | Road has reached or exceeded historical waterlogging rainfall duration. |

---

## 5. Output Format Example

```json
{
  "status": "success",
  "road_id": "DEL-001",
  "road_name": "Road A",
  "location_id": "IMD_DEL_SENSOR_01",
  "current_duration_minutes": 50.0,
  "historical_threshold_minutes": 60.0,
  "risk_level": "MONITOR",
  "severity": "HIGH",
  "is_raining": true,
  "data_freshness": "FRESH",
  "last_observation_timestamp": "2026-10-09T10:50:00+00:00",
  "reason": "Continuous rainfall duration (50.0m) has exceeded early-warning monitor threshold (42.0m, 70% of 60.0m). Approaching historical waterlogging conditions.",
  "evaluated_at": "2026-10-09T10:50:00+00:00"
}
```

---

## 6. Running Tests & Simulation

```bash
# Run all 38 unit tests:
python -m unittest discover -s risk-engine/tests -v

# Run the interactive simulation:
python risk-engine/simulation.py
```
