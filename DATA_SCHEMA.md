# Data Schema and Semantics

This document summarizes the current data shapes and points to the machine-readable schemas. The central rule is: **preserve what the source says, preserve what is unknown, and distinguish observed facts from derived values and software examples.**

## 1. Current data layers

| File/layer | Shape and purpose | Important limitation |
|---|---|---|
| `data/raw/*.xlsx` | Original research workbook with 213 citywide incident/location rows, 24 rainfall-context rows, and 14 priority locations | Original source wording; not a verified road database |
| `data/processed/historical_waterlogging.csv` and `.json` | Normalized records derived from the citywide incident sheet | 213 rows across 19 event groups; ten priority claims directly checked, 203 remain under review |
| `frontend/data/road-waterlogging-records.json` | Small dashboard-facing format | `recordCount: 10`, `locationCount: 7`; values may be city/district/event context rather than road measurements |
| `data/roads.json` | Risk-engine road records | Synthetic `DEL-001` and `DEL-002` examples; not production evidence |
| M3 `RainfallObservation` | A timestamped observation supplied to the risk engine | API observation posting is demo/testing only and in-memory |
| M3 `RiskAssessment` | Derived engine status for a configured road | Depends on thresholds, explicit mapping, observation availability, and freshness |

The two historical data layers are not automatically joined. Do not assume the small dashboard JSON represents the entire 213-row workbook.

## 2. Dashboard JSON

Source: `frontend/data/road-waterlogging-records.json`.

Top-level fields:

| Field | Type | Meaning |
|---|---|---|
| `source` | string | Source workbook identifier recorded by the export |
| `recordCount` | integer | Total historical event records across all locations |
| `locationCount` | integer | Number of locations in the dashboard feed |
| `locations` | array | Location records |

Location fields:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Dashboard location ID (for example `KNP-01`) |
| `city` | string | City scope, currently `kanpur` or `gurugram` |
| `name` | string | Display label, which may identify an area rather than a precise road segment |
| `geo` | string | Geocoding/search label |
| `lat`, `lng` | number or null | Approximate or assigned coordinates; not proof of a surveyed road segment |
| `heading` | number | UI/map presentation metadata |
| `events` | array | Historical event/reference items for the location |

Dashboard event fields:

| Field | Type | Meaning |
|---|---|---|
| `date` | string | Event/report date as recorded |
| `mm` | number or null | Reported rainfall amount; interpret with `scope`, never assume it is road-level |
| `scope` | string | Explicit scale/period context for the amount |
| `dur` | string | Original duration context or `UNKNOWN`; does not imply a numeric continuous-rain duration |
| `sev` | string | Source-reported severity/depth context, not a standardized model probability |
| `impact` | string | Text description of reported impact |
| `src` | string | Source URL |

The current dashboard data shape is intentionally compact. It is not the canonical normalized research schema.

## 3. Normalized historical record

Machine-readable schema: `data/schemas/historical_waterlogging.schema.json`.

The normalized format includes source identifiers (`record_id`, `event_id`, `source_record_id`), location fields (`road_id`, `road_name`, `location_name`, `location_precision`, `city`, coordinates), event-date fields, rainfall values plus scope/period/road-specific flags, severity/context, source name/URL, review/confidence state, threshold suitability, review flags, source sheet/row, and raw source fields.

Important current rules:

- `road_id` and `road_name` are null where the workbook does not identify an actual road segment.
- Coordinates remain null in the normalized workbook export because the workbook does not support them; do not fill these from the dashboard's separately curated approximate coordinates without an explicit, reviewed join.
- `rainfall_amount_mm` must be interpreted with `rainfall_scope` and `rainfall_scope_period`; the current research workbook values are not road-specific.
- `rainfall_duration_minutes` is populated only for explicit wording that supports a numeric/qualified duration. An event time window is not automatically continuous rain.
- `rainfall_intensity_mm_hr` remains null unless reported or derivable from sufficient co-located measurements and a documented method.
- Ten priority claims were checked against their cited articles for the reported event/location claim; 203 other workbook records remain under review. This verification is not independent official corroboration and does not validate road thresholds.
- All normalized workbook rows currently have unknown threshold status / insufficient evidence for a road-specific threshold.

See [`data/README.md`](data/README.md), [`docs/historical-data-methodology.md`](docs/historical-data-methodology.md), and [`docs/source-verification-log.md`](docs/source-verification-log.md).

## 4. Rainfall observation

Machine-readable schema: `data/schemas/rainfall_observation.json`.

```json
{
  "location_id": "OBSERVATION_LOCATION_ID",
  "timestamp": "2026-10-09T10:30:00Z",
  "rainfall_intensity_mm_hr": 25.0,
  "is_raining": true,
  "latitude": null,
  "longitude": null,
  "accumulated_rainfall_mm": null,
  "source": "manual"
}
```

This is a structural example, not a real observation. Required fields are non-empty `location_id`, timezone-aware ISO-8601 `timestamp`, and non-negative `rainfall_intensity_mm_hr`. `is_raining`, coordinates, accumulated rainfall, and source may be optional. A single observation cannot establish continuous rainfall duration; the tracker derives duration from a sequence.

## 5. Road vulnerability configuration

`data/roads.json` currently contains two synthetic examples with numeric duration thresholds. These values are useful for software tests only and must not be interpreted as evidence-backed thresholds for actual roads. A production candidate should identify a stable road/segment, threshold basis, supporting historical record IDs, source provenance, review state, and threshold status such as `OBSERVED`, `DERIVED`, `ESTIMATED`, or `UNKNOWN`.

A road's ID is not a rainfall observation ID. M3 requires an explicit mapping:

```json
{"REVIEWED_ROAD_ID": "REVIEWED_OBSERVATION_LOCATION_ID"}
```

No mapping should be inferred from equal IDs, names, or proximity.

## 6. Risk assessment

A risk assessment preserves M3's output fields: `status`, `road_id`, `road_name`, `location_id`, `current_duration_minutes`, `historical_threshold_minutes`, `risk_level`, `severity`, `is_raining`, `data_freshness`, `last_observation_timestamp`, `reason`, and `evaluated_at`.

Risk enum values: `NORMAL`, `MONITOR`, `HIGH_RISK`, `UNKNOWN`.

Freshness/mapping values: `FRESH`, `STALE`, `NO_DATA`, `UNMAPPED`.

`MONITOR` defaults to 70% of a configured threshold; `HIGH_RISK` starts at 100%. This ratio is a provisional deterministic heuristic. It is not a validated probability. A null threshold produces an unknown/threshold-unavailable assessment; no-data and stale values must not be interpreted as safe.

## 7. Units, timestamps, and null semantics

- Rainfall amount/accumulation: millimetres (`mm`).
- Rainfall intensity: millimetres per hour (`mm/hr`).
- Continuous rainfall duration and thresholds: minutes.
- Coordinates: decimal degrees.
- Timestamps exchanged through the API: ISO-8601 with a timezone, preferably UTC (`Z`).
- Use JSON `null` for a missing numeric/string value. Do not substitute zero unless zero was actually observed.
- Keep the source's wording and qualifier when the normalized value is approximate or lower-bound.
- Do not derive rainfall intensity from a city rainfall amount and a rough event window if the measurements are not established as co-located and temporally compatible.
