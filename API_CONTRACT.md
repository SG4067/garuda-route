# Garuda Route API Contract

This document distinguishes the **browser-facing Node routes** from the **upstream FastAPI risk routes**. The two prefixes are intentionally different. The Node layer does not calculate risk; FastAPI delegates to M3's `WaterloggingRiskService`.

## 1. Services and default addresses

| Service | Default address | Starts with |
|---|---|---|
| Browser frontend + proxy | `http://127.0.0.1:3000` | `node backend/server.js` |
| FastAPI risk service | `http://127.0.0.1:8000` | `cd backend && uvicorn app.main:app --reload` |

Node proxies risk requests to `GARUDAROUTE_RISK_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`. A working Node server does not mean the FastAPI service is running or configured.

## 2. Browser-facing Node endpoints

### Static/configuration endpoints

| Method and path | Purpose |
|---|---|
| `GET /` or `GET /index.html` | Serves `frontend/index.html` |
| `GET /config.js` | Exposes `GOOGLE_MAPS_BROWSER_KEY` as `window.GARUDA_CONFIG.googleMapsApiKey` |
| `GET /records.js` | Exposes the checked-in historical dashboard JSON as `window.GARUDA_DATA` |
| `GET /risk-utils.js` | Serves `frontend/risk-utils.js` |

The Google Maps key is intentionally browser-visible. It is not a secret and must be restricted by allowed HTTP referrers and required APIs.

### IMD district-context proxy

| Method and path | Upstream mapping |
|---|---|
| `GET /api/imd/warnings` | IMD `districtwarning` endpoint |
| `GET /api/imd/rainfall` | IMD `districtrainfall` endpoint |

The proxy reads `IMD_API_KEY`, `IMD_API_KEY_HEADER`, `IMD_API_KEY_PREFIX`, `IMD_API_KEY_MODE`, and `IMD_API_KEY_QUERY_PARAMETER` from the Node process environment. Missing credentials produce HTTP 503. IMD 401/403 responses indicate credential rejection; upstream and timeout failures return an error response. Exact authentication settings must match the issued credential.

These endpoints provide district context and must not be presented as measurements taken on each individual road.

### Risk proxy endpoints

| Method and path | Node proxy target |
|---|---|
| `GET /api/risk/roads` | `GET {GARUDAROUTE_RISK_API_BASE_URL}/api/roads/risk` |
| `GET /api/risk/roads/{road_id}/risk` | `GET {GARUDAROUTE_RISK_API_BASE_URL}/api/roads/{road_id}/risk` |

The `as_of` query parameter is forwarded when supplied. The Node proxy returns the upstream body/status, except that upstream 5xx responses are normalized to JSON error bodies. Connection failure returns HTTP 502.

## 3. FastAPI risk endpoints

Open `http://127.0.0.1:8000/docs` for the local OpenAPI page when the service is running.

### `GET /api/health`

Returns a small status object containing `status`, `service`, and `environment`.

### `GET /api/roads/risk?as_of=<ISO-8601 timestamp>`

Returns a collection envelope:

```json
{
  "roads": [],
  "count": 0
}
```

Each item in `roads` is the M3 assessment object. `as_of` is optional; if provided, it must be an ISO-8601 timestamp containing a timezone.

### `GET /api/roads/{road_id}/risk?as_of=<ISO-8601 timestamp>`

Returns one M3 assessment object. An unknown road ID returns HTTP 404. A known road without a location mapping returns an `UNKNOWN` / `UNMAPPED` assessment rather than a false normal/safe result.

### `POST /api/observations`

**Demo/testing endpoint only.** Validates and submits one observation to the in-memory M3 service. It does not connect to an IMD stream and does not persist to disk. State is lost when the FastAPI process restarts.

Request:

```json
{
  "location_id": "OBSERVATION_LOCATION_ID",
  "timestamp": "2026-10-09T10:30:00Z",
  "rainfall_intensity_mm_hr": 25.0,
  "is_raining": true,
  "source": "manual"
}
```

Required: non-empty `location_id`, timezone-aware `timestamp`, non-negative `rainfall_intensity_mm_hr`. Optional fields: `is_raining`, `latitude`, `longitude`, `accumulated_rainfall_mm`, `source`. Unknown fields are rejected. Example values are illustrative only.

## 4. Risk assessment object

The M3 service fields are passed through without renaming or recalculation:

| Field | Type | Meaning |
|---|---|---|
| `status` | string | Service outcome such as `success`, `error`, or `threshold_unavailable` |
| `road_id` | string | Configured road identifier |
| `road_name` | string | Road label |
| `location_id` | string or null | Explicit observation-location mapping |
| `current_duration_minutes` | number | Tracked continuous rainfall duration; zero in no-data output does not prove dry conditions |
| `historical_threshold_minutes` | number or null | Configured historical indicator; null stays null |
| `risk_level` | `NORMAL`, `MONITOR`, `HIGH_RISK`, or `UNKNOWN` | Deterministic engine classification |
| `severity` | string or null | Historical/configured severity, not current risk |
| `is_raining` | boolean | Last observed rain state; false without data does not prove dry conditions |
| `data_freshness` | `FRESH`, `STALE`, `NO_DATA`, or `UNMAPPED` | Quality/availability of the observation and mapping |
| `last_observation_timestamp` | ISO-8601 string or null | Latest observation time |
| `reason` | string | Human-readable explanation |
| `evaluated_at` | ISO-8601 string | Evaluation timestamp |

`UNKNOWN`, `NO_DATA`, `STALE`, `UNMAPPED`, and unavailable thresholds must not be converted to `NORMAL` or “safe”. Missing observations do not imply that rainfall stopped.

## 5. Status codes

| Condition | FastAPI status |
|---|---:|
| Risk service/roads not configured | 503 |
| Unknown road ID | 404 |
| Invalid/missing timezone in `as_of` | 422 |
| Invalid observation payload | 422 |
| Conflicting observation at same location/time | 409 |
| Successful query/ingest | 200 |

The exact error detail is explanatory; clients should use HTTP status and risk data-state fields rather than parse free-form text as risk state.

## 6. Configuration and data boundaries

The FastAPI configuration uses `GARUDAROUTE_RISK_ROADS_FILE` and `GARUDAROUTE_RISK_ROAD_TO_LOCATION_JSON`. If `GARUDAROUTE_RISK_ROADS_FILE` is unset, the service starts with the risk service unconfigured and the risk routes return 503. Mappings must be explicitly reviewed. The application must never infer road-to-location mapping from a matching ID, road name, or proximity.

The root `data/roads.json` contains synthetic `DEL-001` / `DEL-002` examples. Do not enable it for real traveller-facing risk decisions.
