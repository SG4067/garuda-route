# Historical Data Methodology

## 1. Objective

Build a defensible relationship between historical rainfall conditions and documented road waterlogging events without presenting incomplete or area-level evidence as a road-specific prediction.

## 2. Historical record requirements

Where the source supports them, retain:
- named location and road/segment identity;
- event date or date range;
- rainfall amount, scope and period;
- rainfall duration and its qualifier;
- reported waterlogging severity and whether it applies to the named location;
- source name and URL;
- evidence status and the limitations of the record.

A missing value must remain `UNKNOWN` in source text or `null` in normalized numeric/optional fields as specified by the schema. Unknown values must not be fabricated.

## 3. Threshold derivation

A historical rainfall-duration threshold may only be derived when sufficient, relevant evidence exists. Every threshold must be labelled `OBSERVED`, `DERIVED`, `ESTIMATED` or `UNKNOWN`, with its method and supporting event IDs recorded.

A citywide rainfall total is not a measurement at each road. A report's event window is not automatically continuous rainfall duration. Water-recession or road-clearing time is not rainfall duration. Rainfall intensity must not be derived from an event amount and duration unless they are known to describe a compatible, co-located measurement and period.

Rainfall alone does not determine waterlogging. Drainage, topography, road elevation, blockages, runoff and other factors may affect actual conditions.

## 4. Current workbook normalization

The research workbook's `Citywide incidents` sheet has one row per source-named location. It is normalized as one location record per source row, with a deterministic event group ID shared by rows with the same city, raw date and source URL. `source_record_id` identifies a worksheet row; these IDs are not assigned by a publisher.

The source field `Reported location / road` mixes roads, crossings, underpasses and broad areas. Until a road segment is confirmed, `road_id` and `road_name` remain `null`; source wording is retained in `location_name` and `source_location_raw`. Coordinates are not in the workbook and remain `null`.

City-, district- and station-level rainfall values retain their scope and period and are marked as not road-specific. Unknown source values become empty CSV fields and JSON `null`; the original text remains in `source_*_raw` fields. Only explicit approximate or lower-bound duration statements are normalized into minutes, with the qualifier and source text retained. Source-event severity remains context, not a standardized road-level severity class.

Ten priority records were checked directly against their cited articles on 2026-10-09 and are marked `VERIFIED` for the event/location claim. The remaining 203 rows remain `REQUIRES_REVIEW`. This checks what the secondary source reports; it is not independent official corroboration. Details are in the [source verification log](source-verification-log.md).

The cited 2022-05-23 India Today article does not state a rainfall duration. The workbook's approximately two-hour duration was removed from the normalized duration field for all 14 location rows citing that article. The original workbook wording remains preserved in the raw source field.

## 5. How the current application uses historical evidence

The bundled browser dataset, `frontend/data/road-waterlogging-records.json`, is a smaller interface export containing 10 historical event records across 7 locations. It is distinct from the broader workbook containing 213 locality rows.

In the browser dashboard, the historical rainfall clock compares a user-selected/interactive value against reported rainfall amount or duration where the record contains a numeric value. The interface has a configurable monitor ratio of 0.75 and high-risk ratio of 1.0. These are **prototype heuristics for exploring historical reports**, not validated road-specific thresholds, live measurements or probabilities of flooding. Records without a usable numeric comparison remain unrated.

The separate M3 `WaterloggingRiskService` tracks continuous rainfall from ingested observations, applies a default 0.70 monitor ratio against a configured road threshold, and reports data freshness and mapping state. That engine is a distinct subsystem: it does not turn the historical dashboard's city/event-context measurements into verified road thresholds. Its live use still requires suitable evidence-backed road records, explicit road-to-observation mappings and an authorized observation source. The M3 observation API currently supports in-memory testing; it is not itself a live IMD feed or persistent store.

## 6. Current threshold assessment

**INSUFFICIENT EVIDENCE FOR A VALIDATED ROAD-SPECIFIC THRESHOLD.** The workbook has 213 location rows, but does not provide verified road-specific rainfall observations paired with continuous rainfall duration and waterlogging at that same road. Event-level amounts and approximate durations can support source review and exploratory timelines only. They do not support a causal road-specific threshold or calibrated risk probability.

## 7. Next validation steps

1. Continue verifying the 203 records marked `REQUIRES_REVIEW`; record corrections with source references.
2. Seek official incident and rainfall sources with clear dates, locations, measurement scope and reuse conditions.
3. Resolve road/segment geometry and observation locations with traceable evidence.
4. Keep area-level reports separate from road-level observations in storage and UI.
5. Derive a threshold only after documenting the evidence set, derivation method, limitations and validation approach.
6. Evaluate thresholds against held-out, independently verified events before describing classification accuracy.
7. Track source coverage and freshness without treating an absent report or absent observation as proof of safety.
