# GarudaRoute API Contract

## Status

Initial backend contract decisions confirmed on 2026-10-09. The backend routes must
preserve M3's risk fields and statuses. Route implementation depends on the
nullable-threshold and consistent-unmapped behavior being fixed in M3's
WaterloggingRiskService and present in the integrated risk-engine package.

## Risk assessment object

The backend returns M3's assessment fields without renaming or recalculating:

| Field | Type | Meaning |
|---|---|---|
| status | string | M3 operation status, such as success, no_data, or error |
| road_id | string | Configured road identifier |
| road_name | string | Configured road label |
| location_id | string or null | Explicit rainfall observation location mapped to this road |
| current_duration_minutes | number | Current continuous rain duration from M3; zero in M3 no-data output is not evidence the road is dry |
| historical_threshold_minutes | number or null | Source-supported threshold if configured; null must remain null |
| risk_level | NORMAL, MONITOR, HIGH_RISK, or UNKNOWN | M3 risk classification |
| severity | string or null | Configured historical severity |
| is_raining | boolean | Last observation's rain state; false in no-data output is not evidence it is dry |
| data_freshness | FRESH, STALE, NO_DATA, or UNMAPPED | Observation/mapping state |
| last_observation_timestamp | ISO-8601 string or null | Timestamp of last observation |
| reason | string | M3 explanation |
| evaluated_at | ISO-8601 string | Evaluation time |

Clients must not display UNKNOWN, NO_DATA, STALE, UNMAPPED, or an unavailable
threshold as NORMAL or safe. For NO_DATA, status and data_freshness are
authoritative; clients must not infer safety from current_duration_minutes=0
or is_raining=false.

## Routes

Register the static /roads/risk route before the dynamic /roads/{road_id}/risk
route.

### GET /api/roads/risk

Optional query parameter: as_of, an ISO-8601 timestamp with timezone.

Response: HTTP 200 JSON object. Each item in roads is the corresponding M3
assessment object.

    {
      "roads": [],
      "count": 0
    }

No observations produce UNKNOWN / NO_DATA assessments. A known road without a
road-to-location mapping produces an UNKNOWN / UNMAPPED assessment. The same
assessment semantics apply to collection and single-road queries.

### GET /api/roads/{road_id}/risk

Optional query parameter: as_of, an ISO-8601 timestamp with timezone.

Response: HTTP 200 with one M3 assessment object. Unknown road IDs return HTTP
404. A known but unmapped road returns HTTP 200 with risk_level UNKNOWN and
data_freshness UNMAPPED, matching the collection result.

### POST /api/observations

Demo/testing endpoint only. Observations update the in-memory
WaterloggingRiskService and are lost when the API process restarts. This is
not a live rainfall feed and does not persist observations.

Request JSON fields:

| Field | Required | Type |
|---|---|---|
| location_id | yes | non-empty string |
| timestamp | yes | ISO-8601 timestamp with timezone |
| rainfall_intensity_mm_hr | yes | number, greater than or equal to zero |
| is_raining | no | boolean; defaults from intensity if omitted |
| latitude | no | number from -90 to 90, or null |
| longitude | no | number from -180 to 180, or null |
| accumulated_rainfall_mm | no | non-negative number, or null |
| source | no | string |

HTTP 200 returns M3's ingestion receipt, including ingested or
duplicate_ignored status. Conflicting observations at the same location and
timestamp return HTTP 409. Invalid payloads return HTTP 422.

## Errors

| Condition | HTTP status |
|---|---:|
| Unknown road ID | 404 |
| Invalid as_of timestamp | 422 |
| Invalid observation payload | 422 |
| Conflicting observation at an existing location/timestamp | 409 |
| Backend service not configured | 503 |

## Mapping and data boundaries

Road IDs must map explicitly to rainfall observation location IDs. The API
must never infer a mapping from the road ID, name, or proximity. Unmapped roads
remain visible with UNKNOWN / UNMAPPED.

Risk values come from M3's WaterloggingRiskService. The backend does not
implement a second risk calculator, a live IMD feed, or persistent observation
storage. Historical threshold values must not be supplied by a demo fixture as
if they were supported by validated road-specific evidence.
