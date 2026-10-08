# Data Schema

## 1. Purpose

This document defines the data structures used by the Real-Time Road Waterlogging Alert and Route Diversion System.

It establishes common field names, types, units and meanings so that the historical-data module, rainfall tracker, risk engine and future backend can exchange data consistently.

## 2. General Rules

1. Use JSON for application data exchanged between modules.
2. Use ISO 8601 timestamps, preferably in UTC, for machine-to-machine communication.
3. Use latitude and longitude in decimal degrees.
4. Use rainfall intensity in millimetres per hour (mm/hr).
5. Use rainfall duration in minutes.
6. Use `null` for an unavailable value in JSON. Never invent a value to fill a gap.
7. Keep source information for historical claims.
8. Distinguish observed facts from derived values and assumptions.
9. Keep the historical severity separate from the current calculated risk level.
10. Fields in the examples are illustrative unless explicitly identified as verified data.

## 3. Rainfall Observation

### Purpose

Represents a rainfall-related observation reported by a weather source at a particular location and time.

### Proposed JSON Example

{
  "location_id": "IMD_DEL_LODHI",
  "timestamp": "2026-10-09T10:30:00Z",
  "rainfall_intensity_mm_hr": 25.5,
  "is_raining": true,
  "latitude": 28.5892,
  "longitude": 77.2215,
  "source": "IMD_API"
}

The example values are illustrative and must not be treated as an actual observation.

### Fields

| Field | Type | Meaning |
|---|---|---|
| `location_id` | String | Identifier for the observation location or station |
| `timestamp` | String | Time associated with the observation |
| `rainfall_intensity_mm_hr` | Number or null | Rainfall intensity, if actually provided or defensibly derived |
| `is_raining` | Boolean or null | Whether rain is reported for the observation interval |
| `latitude` | Number or null | Latitude of the observation location |
| `longitude` | Number or null | Longitude of the observation location |
| `source` | String | Source or adapter that supplied the observation |

### Important Notes

- Rainfall intensity and rainfall duration are different measurements.
- A single observation does not establish how long rainfall has continued.
- The rainfall tracker derives continuous duration from a sequence of observations.
- An observation may report rain status without providing numerical rainfall intensity.
- If a provider does not supply a field and it cannot be reliably derived, preserve it as unknown.
- A weather station's measurement must not be presented as an exact measurement for every nearby road.

## 4. Historical Waterlogging Event

### Purpose

Represents one documented past waterlogging incident.

### Proposed JSON Example

{
  "event_id": "EVENT-001",
  "road_id": "DEL-001",
  "road_name": "Example Road",
  "event_date": "2025-07-15",
  "latitude": null,
  "longitude": null,
  "rainfall_amount_mm": null,
  "rainfall_duration_minutes": null,
  "rainfall_intensity_mm_hr": null,
  "severity": "HIGH",
  "source_name": "Official report",
  "source_url": "https://example.gov.in/report",
  "evidence_status": "REQUIRES_REVIEW"
}

This is a structural example only. It is not a real event, and the URL must be replaced with a real source before any real record is added.

### Fields

| Field | Type | Meaning |
|---|---|---|
| `event_id` | String | Unique identifier for the documented incident |
| `road_id` | String or null | ID of the associated road, if identified reliably |
| `road_name` | String or null | Road or location name recorded by the source |
| `event_date` | String or null | Date of the documented event |
| `latitude` / `longitude` | Number or null | Coordinates, if supported by evidence |
| `rainfall_amount_mm` | Number or null | Documented rainfall accumulation over a known period |
| `rainfall_duration_minutes` | Number or null | Documented rainfall duration, when available |
| `rainfall_intensity_mm_hr` | Number or null | Documented or defensibly derived intensity |
| `severity` | String or null | Documented severity or a separately explained project classification |
| `source_name` | String | Name of the report, dataset or issuing body |
| `source_url` | String | Link to the underlying evidence |
| `evidence_status` | String | Review status for the record |

### Evidence Status

Use these values:

- `UNVERIFIED` — Source or record has not been checked.
- `REQUIRES_REVIEW` — Source exists but the record still needs validation.
- `VERIFIED` — Record checked against its cited evidence.
- `REJECTED` — Record is unsupported, inaccurate or unsuitable for use.

### Rules

- Do not infer rainfall duration from daily rainfall totals.
- Do not assume that two reports refer to different events without checking.
- Do not assign a precise road ID if the source only identifies a broad area.
- Record the original source for every event.
- Keep missing values unknown.

## 5. Road Vulnerability Record

### Purpose

Represents the historical waterlogging information associated with a road that the risk engine can use.

This record is derived from historical evidence; it is not a raw historical incident.

### Proposed JSON Example

{
  "road_id": "DEL-001",
  "road_name": "Example Road",
  "threshold_minutes": 60,
  "threshold_status": "ESTIMATED",
  "historical_event_count": 4,
  "severity": "HIGH",
  "evidence_event_ids": [
    "EVENT-001",
    "EVENT-002"
  ]
}

The threshold and event IDs here are illustrative. Do not use this record as real evidence.

### Fields

| Field | Type | Meaning |
|---|---|---|
| `road_id` | String | Stable identifier used by the application |
| `road_name` | String | Road name or documented location name |
| `threshold_minutes` | Number or null | Rainfall-duration indicator supported by the evidence |
| `threshold_status` | String | How the threshold was established |
| `historical_event_count` | Integer | Number of relevant events used or recorded |
| `severity` | String or null | Historical severity classification |
| `evidence_event_ids` | Array of strings | Historical events supporting the record |

### Threshold Status

Use these values:

- `OBSERVED` — The source explicitly records the relevant duration/condition.
- `DERIVED` — Calculated using a documented method from sufficient observations.
- `ESTIMATED` — Approximate value based on limited evidence and clearly documented assumptions.
- `UNKNOWN` — Evidence is insufficient to establish a threshold.

Do not promote an estimated or unknown threshold to a verified observation.

If the existing risk-engine implementation requires a numerical threshold, roads with `UNKNOWN` thresholds must be handled explicitly rather than given an invented number.

## 6. Risk Assessment Result

### Purpose

Represents the result produced by the risk engine for an identified road.

### Example

{
  "status": "success",
  "road_id": "DEL-001",
  "road_name": "Example Road",
  "current_duration_minutes": 50.0,
  "historical_threshold_minutes": 60.0,
  "risk_level": "MONITOR",
  "severity": "HIGH",
  "is_raining": true,
  "reason": "Rainfall duration is approaching the historical waterlogging indicator.",
  "evaluated_at": "2026-10-09T10:30:00Z"
}

This example illustrates a possible output shape. The final keys must match the actual public interface of M3's risk service.

### Fields

| Field | Type | Meaning |
|---|---|---|
| `status` | String | Whether the evaluation succeeded |
| `road_id` | String | Road being evaluated |
| `road_name` | String | Display name, if available |
| `current_duration_minutes` | Number or null | Current tracked continuous rainfall duration |
| `historical_threshold_minutes` | Number or null | Historical indicator used in the evaluation |
| `risk_level` | String | Calculated risk state |
| `severity` | String or null | Historical baseline severity, not the current risk state |
| `is_raining` | Boolean or null | Latest known rain state |
| `reason` | String | Human-readable explanation of the risk result |
| `evaluated_at` | String | Time of evaluation |

### Risk Level Values

Use the following agreed application values:

- `NORMAL`
- `MONITOR`
- `HIGH_RISK`

Do not use `HIGH` in one module and `HIGH_RISK` in another without an explicit conversion.

The meaning of each risk state must match the implemented threshold comparator.

## 7. Data Freshness

The system must eventually distinguish the state of rainfall from the freshness of its data.

Examples of possible data states:

- `FRESH` — Observation is within the configured freshness limit.
- `STALE` — Observation is older than the configured freshness limit.
- `INVALID` — The observation is malformed or fails validation.

These states describe data quality, not waterlogging risk.

Missing observations must not automatically be interpreted as proof that rain has stopped.

The exact fields and behaviour must match the implemented rainfall tracker.

## 8. Units and Time

- Rainfall intensity: mm/hr
- Rainfall amount: mm
- Rainfall duration: minutes
- Latitude: decimal degrees
- Longitude: decimal degrees
- Machine timestamps: ISO 8601, preferably UTC

Do not mix daily accumulation, hourly intensity and event duration.

## 9. Data Quality and Provenance

Every historical event should preserve its source.

Every derived road threshold should have a documented method and links to the evidence supporting it.

The risk engine must not describe a heuristic threshold result as a scientifically calibrated probability of flooding.

## 10. Current Status

- Rainfall observation structure: proposed; cross-check with M3's implemented model.
- Historical waterlogging event structure: to be finalized with M2.
- Road vulnerability structure: to be finalized once usable historical evidence is collected.
- Risk assessment structure: use M3's actual facade output as the authoritative implementation contract.
- Data freshness fields: finalize after M3's stale-data handling is implemented.
