# Historical Data Methodology

## Objective

Build a defensible relationship between historical rainfall conditions
and documented road waterlogging events.

## Historical Record

Each event should contain:

- location
- road
- date
- rainfall information
- waterlogging severity
- source
- confidence

## Missing Data

Unknown values must remain UNKNOWN.

They must not be fabricated.

## Threshold Derivation

A historical rainfall-duration threshold may only be derived when
sufficient evidence exists.

A threshold must be labeled:

OBSERVED
DERIVED
ESTIMATED
or UNKNOWN

## Evidence Requirements

Prefer government/official records and documented datasets.

## Limitations

Rainfall alone does not determine waterlogging.

Drainage, topography, road elevation, blockages, runoff and other
factors may affect actual waterlogging.

## Current workbook normalization

The current workbook has one `Citywide incidents` row per source-named location. It is normalized as one location record per source row, with a deterministic event group ID shared by rows with the same city, raw date and source URL. The source worksheet row is retained as `source_record_id`; these IDs are local import identifiers, not publisher IDs.

The source field `Reported location / road` mixes roads, crossings, underpasses and broad areas. Until a road segment is confirmed, `road_id` and `road_name` remain null and the source wording is retained in `location_name` and `source_location_raw`. Coordinates are not in the workbook and remain null.

City, district and station rainfall values are retained with their scope and period. They are explicitly marked as not road-specific. Unknown source values become empty CSV fields and JSON `null`; the original text remains in the `source_*_raw` fields.

Only explicit approximate or lower-bound duration statements are converted to minutes. The qualifier and original duration text are kept. A time window is not assumed to mean continuous rain, and water recession or clearing time is not treated as rainfall duration. No rainfall intensity is derived from event rainfall and duration because the observations are not established as co-located measurements.

The source event severity column is event context. It is preserved as text and is not converted into a standardized road severity class. Ten priority records were checked directly against their cited articles on 2026-10-09 and are marked `VERIFIED` for the event/location claim. The other 203 records remain `REQUIRES_REVIEW`. The checked sources are secondary reporting, not independent official corroboration; see [the source verification log](source-verification-log.md).

The direct check found that the cited 2022-05-23 India Today article does not state a rainfall duration. The workbook's approximately two-hour duration was therefore removed from the normalized duration field for all 14 location rows citing that article. The workbook wording remains preserved in the raw source field.

## Current threshold assessment

**INSUFFICIENT EVIDENCE FOR THRESHOLD.** The workbook contains 213 location rows, but it does not provide verified road-specific rainfall observations paired with continuous rainfall duration and waterlogging at that road. Event-level amounts and approximate durations can support source review and exploratory event timelines only. They do not support a causal road-specific threshold or a calibrated risk probability.
