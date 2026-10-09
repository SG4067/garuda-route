# M3 Waterlogging Risk Engine — Audit Report

## A. Repository Status

- **Current branch:** `feature/m3-risk-service`
- **Commits:** None (repo initialized but no commits)
- **Modified/unstaged changes:** None
- **Staged changes:** None
- **Untracked files:** `.gitignore`, `API_CONTRACT.md`, `DATA_SCHEMA.md`, `M3_PROGRESS.md`, `data/`, `risk-engine/`
- **Git diff stat:** No diffs (nothing committed yet)

## B. Three-File Inspection

### 1. `risk-engine/engine/risk_engine.py`

- **What the file does:** Core engine that evaluates road waterlogging risk by comparing continuous rainfall duration against historical thresholds. Provides `evaluate_risk()`, `evaluate_with_tracker()`, and `from_roads_file()` classmethod.
- **What changed/appears partially implemented:** The file appears complete and consistent. The `evaluate_risk()` method already handles the case where `road.threshold_minutes is None` by returning a `RiskAssessment` with `risk_level=RiskLevel.UNKNOWN` and `status="threshold_unavailable"` (lines 141-154). This is correct per Issue B.
- **Syntax errors/inconsistent interfaces:** None observed.
- **What must be preserved:** The `threshold_unavailable` → `RiskLevel.UNKNOWN` path in `evaluate_risk()`. The `evaluate_with_tracker()` convenience method. The `RiskEngineError` hierarchy.
- **What remains incomplete:** The file is functionally functional once the `Optional` import bug in `road.py` is fixed. No obvious gaps.

### 2. `risk-engine/models/risk.py`

- **What the file does:** Defines `RiskLevel` enum (NORMAL, MONITOR, HIGH_RISK, UNKNOWN) and `RiskAssessment` dataclass with `to_dict()` serialization.
- **What changed/appears partially implemented:** The file appears complete. The `RiskLevel` enum has 4 values matching the required states. The `to_dict()` method serializes `risk_level.value` correctly.
- **Syntax errors/inconsistent interfaces:** None.
- **What must be preserved:** The four `RiskLevel` enum values (NORMAL, MONITOR, HIGH_RISK, UNKNOWN). The `evaluated_at` default to UTC now. The `to_dict()` format.
- **What remains incomplete:** None observed.

### 3. `risk-engine/models/road.py`

- **What the file does:** Defines `RoadRecord` dataclass with `road_id`, `road_name`, `threshold_minutes` (Optional[float]), and `severity`.
- **What changed/appears partially implemented:** **CRITICAL BUG**: Line 3 imports `from typing import Dict, Any` but uses `Optional[float]` on line 20 (`threshold_minutes: Optional[float] = None`). `Optional` is not imported, causing `NameError: name 'Optional' is not defined`. This blocks ALL imports from this module.
- **Syntax errors/inconsistent interfaces:** `Optional` used without import. The `from_dict()` method (line 46) lists `"threshold_minutes"` as required, but the dataclass field has `= None` default, creating a schema inconsistency.
- **What must be preserved:** The `threshold_minutes: Optional[float] = None` field definition (allows unknown thresholds per Issue B). The `from_dict()` validation that rejects `threshold_minutes <= 0` and non-numeric values. The `to_dict()` output format.
- **What remains incomplete:** The `Optional` import must be added. The `from_dict()` required-fields logic may need adjustment to handle `threshold_minutes` being optional.

## C. Test Results

- **Command executed:** `python -m unittest discover -s risk-engine/tests -v`
- **Actual result:** 4 tests registered, but **ALL FAILED with ImportError** due to `NameError: name 'Optional' is not defined` in `models/road.py`.
- **Test count:** 0 passing, 4 failed (all import errors).
- **Comparison to historical report:** The earlier report claimed 38 passing tests, but the actual baseline is 0 because:
  1. The repo has no commits (unlike the reported branch state).
  2. The `models/road.py` file has a missing import that prevents any test from running.
  3. The historical report cannot be verified until the import bug is fixed.

### Detailed error trace (reproduced below):

```
ImportError: Failed to import test module: test_rainfall_tracker
  ...
  File "C:\Users\Dell\Desktop\aws\risk-engine\models\road.py", line 8, in <module>
    class RoadRecord:
  File "C:\Users\Dell\Desktop\aws\risk-engine\models\road.py", line 20, in RoadRecord
    threshold_minutes: Optional[float] = None
                       ^^^^^^^^
    NameError: name 'Optional' is not defined
```

## D. Minimal Implementation Plan

### Fix 1: `models/road.py` — Add missing `Optional` import

**Change line 3 from:**
```python
from typing import Dict, Any
```
**To:**
```python
from typing import Dict, Any, Optional
```

**Rationale:** Fixes the `NameError` that blocks all imports. This is the single most critical fix.

### Fix 2: `models/road.py` — Fix `from_dict()` required-fields logic

**Change:** The `required_fields` list on line 46 includes `"threshold_minutes"`, but the dataclass field has `= None` default, making it technically optional. The `from_dict()` method should handle `threshold_minutes` being absent or null without raising ValueError for "missing required field", since `RoadRecord` itself makes it optional.

**Rationale:** Consistency between the dataclass field definition (`= None`) and the `from_dict()` validation. Currently, passing `{"road_id": "X", "road_name": "Y"}` (without `threshold_minutes`) to `from_dict()` raises ValueError for "Missing required road field: 'threshold_minutes'", even though `RoadRecord(road_id="X", road_name="Y")` would succeed (since `threshold_minutes` defaults to `None`).

### Fix 3: `risk-engine/engine/service.py` — `get_road_risk()` no-observations path (Issue A)

**Problem:** When a road has no rainfall observations (state.has_observations is False), the service returns `risk_level: RiskLevel.NORMAL` with `data_freshness: "NO_DATA"` (lines 205-220). Per Issue A, "absence of data is not evidence that a road is safe." The system must represent the distinction between `NORMAL` (sufficient information exists and rules assign normal risk) and `UNKNOWN` / `MONITOR` / `HIGH_RISK`.

**Proposed change:** When there are no observations, return `risk_level: RiskLevel.UNKNOWN` (or potentially `MONITOR` if we want to be conservative) instead of `NORMAL`, and ensure `data_freshness` is `"NO_DATA"`.

Actually, re-reading the requirements more carefully:
- `NORMAL`: sufficient usable information exists and the implemented rules assign normal risk.
- `MONITOR`: current conditions are approaching the historical indicator.
- `HIGH_RISK`: current conditions meet or exceed the historical indicator.
- `UNKNOWN`: insufficient information exists to determine a risk level.

When there are NO observations, we have insufficient information → should be `UNKNOWN`, not `NORMAL`.

But we must be careful: `test_11_no_data_handling` currently expects `risk_level: "NORMAL"`. If we change this, the test will need updating.

### Fix 4: `risk-engine/engine/service.py` — `get_road_risk()` unmapped road path (Issue A)

**Current behavior:** Unmapped roads in `get_all_roads_risk()` return `risk_level: "UNKNOWN"` with `data_freshness: "UNMAPPED"` (lines 275-289). This is correct per the requirements.

### Fix 5: `risk-engine/engine/threshold_comparator.py` — None threshold handling (Issue B)

**Problem:** The `ThresholdComparator.evaluate()` method (lines 52-53) raises `ValueError` if `historical_threshold_minutes is None`. However, `RiskEngine.evaluate_risk()` (lines 141-154) already handles `road.threshold_minutes is None` by returning `RiskLevel.UNKNOWN` before calling the comparator. So the comparator's ValueError for None is only reached if someone calls the comparator directly with a None threshold, which is a valid use case to reject.

**No change needed** — the separation of concerns is correct: `RiskEngine` handles the "threshold unknown" case gracefully, while `ThresholdComparator` asserts that it has valid data to compare.

## E. Risk Assessment

### Is the partially edited state safe to continue from?

**Partially safe, but currently broken.** The three files mentioned (`risk_engine.py`, `risk.py`, `road.py`) are functionally well-structured, but the missing `Optional` import in `road.py` prevents any code from importing the models, making the entire suite inoperable.

### Potentially destructive/incompatible changes to watch for:

1. **Changing `risk_level: NORMAL` → `UNKNOWN` when no observations exist** (Issue A). This is a behavior change that will break `test_11_no_data_handling` which expects `NORMAL`. However, it's the correct per the new correctness requirements. If we make this change, we must also update the test.

2. **Adding `Optional` import** is purely additive and safe.

3. **Modifying `from_dict()` in `road.py`** to not require `threshold_minutes` could affect validation, but since the dataclass already allows `None`, it should be safe.

4. **The `ThresholdComparator.evaluate()` raising ValueError for None threshold** is fine since `RiskEngine` already handles that case before calling the comparator.

### Overall recommendation:

The audit confirms the following immediate actions are needed (in order):

1. **Fix the `Optional` import in `models/road.py`** — this is the critical blocker.
2. **Consider whether `from_dict()` required-fields logic needs adjustment** — currently inconsistent with the dataclass field default.
3. **Decide on the `NORMAL` vs ` UNKNOWN` for no-observations case** (Issue A) — this is a correctness fix that may require test updates.
4. **Run the full test suite after each change** to verify no regressions.

The partially edited state is **safe to continue from** provided we fix the import bug first, then carefully address the correctness issues one at a time with appropriate test updates.