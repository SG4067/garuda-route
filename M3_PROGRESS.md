# M3 Progress: Waterlogging Risk Module

**Branch:** `feature/m3-risk-service`  
**Module Owner:** Member 3 (Rainfall Tracker & Waterlogging Risk Engine)  
**Status:** Verification & Integration Ready (38/38 Tests Passing)

---

## 1. Executive Summary
The M3 risk module is fully implemented, verified, and encapsulated behind a single public service facade: `WaterloggingRiskService`. Backend (M2) and Frontend (M4) do not need to manage internal trackers, comparators, or road records.

---

## 2. Installation & Test Commands

### Prerequisites
- Python 3.10+ (Standard Library only; zero third-party dependencies required).

### Run Test Suite
```bash
# From workspace root:
python -m unittest discover -s risk-engine/tests -v

# Or from risk-engine directory:
cd risk-engine
python -m unittest discover tests -v
```

### Run Full Simulation
```bash
python risk-engine/simulation.py
```

---

## 3. Public Service Interface

### Class: `WaterloggingRiskService`
Located in `risk-engine/engine/service.py`.

```python
class WaterloggingRiskService:
    @classmethod
    def from_roads_file(
        cls,
        roads_file_path: Union[str, Path] = "data/roads.json",
        road_to_location: Optional[Dict[str, str]] = None,
        stale_threshold_minutes: float = 30.0,
        max_observation_gap_minutes: float = 30.0,
        monitor_ratio: float = 0.70,
    ) -> "WaterloggingRiskService": ...

    def register_road_mapping(self, road_id: str, location_id: str) -> None: ...

    def get_road_mapping(self, road_id: str) -> Optional[str]: ...

    def ingest_observation(
        self,
        observation: Union[Dict[str, Any], RainfallObservation]
    ) -> Dict[str, Any]: ...

    def get_road_risk(
        self,
        road_id: str,
        as_of: Optional[datetime] = None
    ) -> Dict[str, Any]: ...

    def get_all_roads_risk(
        self,
        as_of: Optional[datetime] = None
    ) -> List[Dict[str, Any]]: ...
```

---

## 4. How the Backend Should Import This Code

> **Crucial Import Note:**  
> In Python, `risk-engine` contains a hyphen (`-`) and cannot be directly imported as `import risk-engine` (this triggers a `SyntaxError`).

### Smallest Safe Solutions for Backend (M2):

#### Solution A (Recommended for Monorepo/Backend Integration):
Add `risk-engine` to `sys.path` dynamically or configure `PYTHONPATH`:
```python
import sys
from pathlib import Path

# Add risk-engine folder to sys.path
RISK_ENGINE_DIR = Path(__file__).resolve().parent / "risk-engine"
if str(RISK_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(RISK_ENGINE_DIR))

# Import cleanly from engine.service
from engine.service import WaterloggingRiskService
```

#### Solution B (Packaging / Editable install):
When merging into the team repository root, provide a standard `pyproject.toml` pointing to `risk-engine`, or rename the top-level directory to `risk_engine` (underscore) so `from risk_engine.engine.service import WaterloggingRiskService` works natively.

---

## 5. Working Python Example

```python
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add risk-engine to import path
sys.path.insert(0, str(Path(__file__).resolve().parent / "risk-engine"))
from engine.service import WaterloggingRiskService

# 1. Initialize Service
service = WaterloggingRiskService.from_roads_file(
    roads_file_path="data/roads.json",
    road_to_location={"DEL-001": "IMD_DEL_SENSOR_01", "DEL-002": "IMD_DEL_SENSOR_02"},
    stale_threshold_minutes=30.0,
    max_observation_gap_minutes=30.0,
    monitor_ratio=0.70,
)

# 2. Ingest Weather Observation (Dict or Model)
receipt = service.ingest_observation({
    "location_id": "IMD_DEL_SENSOR_01",
    "timestamp": "2026-10-09T10:00:00Z",
    "rainfall_intensity_mm_hr": 25.0,
    "is_raining": True,
})
print("Ingestion Receipt:", receipt)

# 3. Query Single Road Risk
risk = service.get_road_risk("DEL-001")
print("DEL-001 Risk Level:", risk["risk_level"])  # NORMAL, MONITOR, or HIGH_RISK

# 4. Query All Configured Roads (for Map Feed)
all_risks = service.get_all_roads_risk()
print(f"Total Roads Evaluated: {len(all_risks)}")
```

---

## 6. Exact Formats

### Ingestion Input Format (`service.ingest_observation`)
```json
{
  "location_id": "IMD_DEL_SENSOR_01",
  "timestamp": "2026-10-09T10:30:00Z",
  "rainfall_intensity_mm_hr": 25.0,
  "is_raining": true,
  "latitude": 28.5892,
  "longitude": 77.2215,
  "accumulated_rainfall_mm": 5.0,
  "source": "IMD_API"
}
```

### Risk Output Format (`service.get_road_risk`)
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
  "evaluated_at": "2026-10-09T10:55:00+00:00"
}
```

---

## 7. Road-to-Location Mapping
The system requires an explicit mapping between road IDs and rainfall sensor IDs (`road_to_location: Dict[str, str]`):
- Roads without a configured mapping raise `RoadMappingNotFoundError` on `get_road_risk()`.
- Unmapped roads in `get_all_roads_risk()` return `{"status": "error", "data_freshness": "UNMAPPED", "risk_level": "UNKNOWN"}`.
- M3 does not assume `road_id == location_id` or pick an arbitrary primary sensor.

---

## 8. Error & Stale Data Behavior
1. **Idempotent Duplicates**: Exact duplicate observations return `{"status": "duplicate_ignored"}` without crashing or double-counting duration.
2. **Conflicting Telemetry**: Same timestamp with conflicting values raises `ObservationConflictError`.
3. **Stale Telemetry**: If no observation arrives for $> 30$ minutes, `data_freshness` becomes `"STALE"`. Continuous duration is **not** reset to zero; the last recorded duration is evaluated and flagged with a stale warning.
4. **Unknown Roads**: Raises `RoadNotFoundError`.
5. **Invalid Payload**: Raises `ValueError` on negative intensity or malformed timestamps.

---

## 9. Current Limitations & Handoff to M2
1. **In-Memory State**: Tracker state is kept in memory. For multi-worker deployments, M2 can attach Redis/DynamoDB behind tracker state.
2. **Spatial Association**: M3 uses explicit ID mapping (`road_to_location`). Geospatial polygon matching belongs to M2 (Backend/GIS).
3. **Root Document Ownership**: M1 owns root `API_CONTRACT.md` and `DATA_SCHEMA.md`. Confirmed fields are reported to M1 for incorporation.
