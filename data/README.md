# Waterlogging Dataset — README

## 1. Purpose

This folder stores the evidence used by the Real-Time Road Waterlogging Alert and Route Diversion System.

The project aims to compare current rainfall observations with historical evidence of waterlogging at particular roads or locations. The dataset is an initial research collection for the Kanpur and Gurugram pilot areas; it is **not a complete official inventory** of all waterlogging incidents.

## 2. Current source workbook

The canonical source workbook is:

`kanpur_gurugram_all_waterlogging_locations.xlsx`

It was copied into `data/raw/` without editing its cell data. An earlier same-value workbook named `kanpur_gurugram_all_waterlogging_locations (2).xlsx` was already present there and was left unchanged. The two files have the same values in all four worksheets; they differ in binary metadata. The original in the earlier project output folder was not changed.

The canonical workbook contains these sheets:

| Sheet | Contents | Records |
|---|---|---:|
| `Start here` | Scope, interpretation notes and limitations | Instructions |
| `Citywide incidents` | Source-named historical waterlogging and rain-related road incidents | 213 incident/location rows: 109 Kanpur and 104 Gurugram |
| `Rainfall context` | Published rainfall measurements and event context | 24 records |
| `Priority locations` | Team-selected priority locations and evidence coverage | 14 locations: 8 Kanpur and 6 Gurugram |

The first two rows of each sheet are title/subtitle rows, with column headers on row 5 for the three tabular sheets. The workbook uses 12, 218, 29 and 19 occupied rows respectively, counting titles and headers.

In the `Priority locations` sheet, 11 locations are marked `EVIDENCE FOUND`, two are marked `PARTIAL — AREA ONLY`, and one is marked `NO EXACT EVENT FOUND`. These labels describe the results of the current source review, not whether a place can ever flood.

## 3. Folder conventions

Use the folders as follows:

- `raw/` — Original workbooks, PDFs, reports and downloaded source files. Do not edit originals.
- `processed/` — Cleaned CSV/JSON exports created from raw sources, with transformations documented.
- `sample/` — Small, clearly labelled synthetic records used for software tests and demos.
- `schemas/` — Machine-readable definitions of expected data structures.

Do not put synthetic test records in the same file as verified historical observations unless they have an explicit field marking them as synthetic.

## 4. What the current dataset can support

The workbook can help the team:

1. Identify locations that public reports have named in connection with waterlogging or rain-related road incidents.
2. Preserve the event date and source link where recorded.
3. Review published rainfall information associated with some events.
4. Prioritize locations for additional research.
5. Build and test the data-import pipeline.

The workbook is useful as an initial evidence register. It should not automatically be treated as a ready-to-train machine-learning dataset or as a source of validated road-specific rainfall thresholds.

## 5. Important limitations

### City rainfall is not road rainfall

Some reported rainfall measurements refer to a city, district, weather station or event-wide interval. These values must not be presented as measurements taken at each listed road. Check the `Rainfall scope / period` or equivalent notes before using a rainfall value.

### Missing information is not zero

The workbook uses the text `UNKNOWN` where a source did not state a value. In the normalized CSV this becomes an empty field; in JSON it becomes `null`. Original text is retained in `source_*_raw` fields. Unknown rainfall, duration, coordinates or severity must not be replaced with zero or an invented estimate.

### A reported event does not establish a rainfall-duration threshold

A report that a road was waterlogged on a particular date does not by itself prove that continuous rainfall of a certain number of minutes caused it. The currently collected records do not establish a causal rainfall-duration threshold for predicting future waterlogging.

Do not assign a threshold such as 60 minutes unless there is evidence and a documented method supporting that value. When evidence is insufficient, set the threshold to unknown and make sure the risk engine handles that case explicitly.

### Location names may not identify precise road segments

A report may mention an area or locality rather than an exact road segment. Do not infer precise coordinates or claim that an area-level event happened on a specific road without supporting evidence. The workbook notes that the Panki records do not separate the requested paved and unpaved road segments.

### No result found is not proof of no flooding

Public reporting is incomplete and uneven. A location marked `NO EXACT EVENT FOUND` means the current review did not find an exact match; it does not mean the location has never experienced waterlogging.

### Severity may be contextual

The reported severity can describe a broader event or locality rather than a measured severity at the exact road. Preserve the source's wording and clarify when a severity label is a project classification rather than a source-reported fact.

## 6. Recommended record handling

For every processed record, retain as many of these fields as the evidence supports:

- `event_id`
- `city`
- `road_or_location_name`
- `event_date`
- `latitude` and `longitude`, if supported
- `rainfall_amount_mm`, if reported
- `rainfall_scope_period`
- `rainfall_duration_minutes`, if reported
- `rainfall_intensity_mm_hr`, if reported or derived with a documented method
- `severity_as_reported`
- `source_name`
- `source_url`
- `evidence_status`
- `notes_and_limitations`

Recommended evidence-status values:

- `UNVERIFIED` — Record has not been checked against the source.
- `REQUIRES_REVIEW` — A source has been identified, but the event details still need checking.
- `VERIFIED` — The record was checked against the cited source for the event/location claim. This does not imply official corroboration or evidence for a road-level rainfall threshold.
- `REJECTED` — The claim is unsupported, incorrectly transcribed or unsuitable for the dataset.

Keep source wording separate from any normalized or inferred values. For derived fields, record the derivation method and preserve the original values.

## 7. Sources and provenance

The `Citywide incidents`, `Rainfall context` and `Priority locations` sheets contain source links and evidence notes. Before using a record in a public demo or threshold calculation, open its cited source and confirm that it supports the claim being made.

When exporting the workbook into CSV or JSON, preserve the source URL and the associated evidence/limitation note. Do not export only road names and rainfall values while discarding provenance.

## 8. How this data will be used by the application

The intended pipeline is:

1. Historical records provide evidence about where waterlogging has been reported.
2. A documented method may derive a road-vulnerability indicator when the evidence is sufficient.
3. Live rainfall observations are normalized separately and tracked over time.
4. The risk engine compares the current conditions with an evidence-supported indicator.
5. The application returns an explainable risk result.

If no defensible threshold is available for a road, the application should mark its risk assessment as unavailable or insufficiently supported rather than silently treating it as safe.

## 9. Current status and next actions

- [x] Initial Kanpur and Gurugram research workbook collected.
- [x] Citywide incident, rainfall-context and priority-location sheets included.
- [x] Directly verify ten priority records against their cited articles; see `../docs/source-verification-log.md`.
- [ ] Verify the remaining source links and claims before using those records as evidence.
- [x] Export location records to `processed/` CSV and JSON files.
- [x] Align normalized event fields with `DATA_SCHEMA.md`; retain source fields and add explicit scope/uncertainty fields.
- [x] Preserve unknowns and document transformations.
- [x] Assess threshold suitability: no record currently supports a road-specific rainfall-duration threshold.

**Current status:** source-linked research evidence register. Ten of 213 records are `VERIFIED` for the reported event/location claim; 203 remain `REQUIRES_REVIEW`. This is not a verified road-level predictive dataset.

## 10. Workbook inspection and processing

The processing script reads only `Citywide incidents` for the event dataset. It does not convert the other sheets into incident records.

| Worksheet | Used rows | Data rows | Columns | Interpretation |
|---|---:|---:|---:|---|
| `Start here` | 12 | — | No table header; A1:F12 | Scope, highlighting, unknown-value and threshold cautions. |
| `Citywide incidents` | 218 | 213 | 10 | One source-named locality row per event/location; 109 Kanpur and 104 Gurugram rows, representing 19 source/date event groups. |
| `Rainfall context` | 29 | 24 | 7 | City, district or station rainfall context, including historical comparison rows. Kept in the raw workbook and not joined to roads as if it were a road observation. |
| `Priority locations` | 19 | 14 | 6 | Coverage index for team-selected locations, not incident observations. |

`Citywide incidents` columns: `City` is the reported municipality; `Reported location / road` preserves the source label; `Event date` preserves a day or date range; `Rainfall (mm)` is the reported number or `UNKNOWN`; `Rainfall scope / period` identifies the measurement area/window; `Rain / water duration` is source text that may refer to rain, water recession, or a reporting window; `Reported severity (event context)` is event-level impact text; `Evidence note` and `Source link` preserve provenance/limitations; `Priority location?` marks the team's focus list.

`Rainfall context` columns: `City`, `Date / period`, `Rainfall (mm)`, `Measurement scope`, `Duration / period`, `Source context and limitation`, `Source link`. `Priority locations` columns: `City`, `User priority location`, `Coverage status`, `What the cited sources support`, `Incident rows found`, `Road-level rainfall`.

### Missing values and duplicates found

- No empty cells were found in the data rows of the three tables; the source uses literal `UNKNOWN` text instead.
- In `Citywide incidents`, 17 location rows have unknown rainfall amount, 127 have duration text containing `UNKNOWN`, and 126 have severity context that explicitly says some depth/severity is unknown. One location string is `Kanpur South roads (specific route UNKNOWN)`, which is retained as an area-level location.
- In `Rainfall context`, 3 rows have unknown rainfall, 12 have unknown duration, and 1 source-context cell contains `UNKNOWN`.
- In `Priority locations`, all 14 road-level rainfall cells are `UNKNOWN`; one status reports no exact event found. This is not evidence that the place never floods.
- There are 0 exact duplicate incident rows. `Gurugram / 2023-07-04 / Mayfield Garden` appears twice from different source URLs. Both rows are retained and flagged because the reports give different rainfall contexts (65 mm city total and 230 mm district figure).
- All 213 incident rows have a source URL, representing 19 distinct URLs on 6 publisher domains. The rainfall tab has 24 URL cells and 22 distinct URLs on 7 domains. These are mostly news reports; ten priority location rows have been checked directly, while the remaining source links have not yet been checked.
- The workbook has no latitude, longitude, stable road IDs, or standardized road-level severity values.

### Normalized record rules

- One CSV/JSON record represents one row in `Citywide incidents`, not one unique flood event. The output therefore contains 213 location records and 19 grouped `event_id` values.
- `record_id` is a stable workbook-row locator. `event_id` is a deterministic hash of city, raw date text and source URL. Neither is an ID assigned by the publisher.
- `road_id` and `road_name` remain `null`; the source column mixes roads, junctions, underpasses and broad localities. `location_name` preserves the named place, while `source_location_raw` preserves the exact original text.
- `event_date` is populated only for a single ISO date. For date ranges, `event_date` is `null` and `event_date_start` / `event_date_end` preserve the endpoints. `event_date_raw` always preserves the source cell.
- `rainfall_amount_mm` carries the workbook's reported numeric event/city/district/station amount with `rainfall_scope` and `rainfall_scope_period`. `rainfall_is_road_specific` is `false` for every row. The event-level amount is repeated across location rows belonging to that report; do not treat it as an individual road gauge.
- `rainfall_duration_minutes` is populated only for explicit duration wording: approximate 2-hour or 2.5-hour statements and an “over 2 hours” lower bound. The qualifier and original text are retained. These durations are event-area context, not road-specific continuous-rain measurements. Unclear windows and water-recession times remain `null` in the numeric field.
- `rainfall_intensity_mm_hr`, coordinates, `road_id`, `road_name`, and numeric confidence remain `null`; none is established by the workbook. Severity text is preserved in `severity` with `severity_scope=EVENT_CONTEXT`; it is not converted to a standardized road-level class.
- `source_name` is the publisher name derived from the URL hostname. The original URL and all useful incident-sheet source columns are preserved. `source_record_id` identifies the worksheet row.
- Ten evidence records are `VERIFIED` against the cited articles for the reported event/location claim; the other 203 remain `REQUIRES_REVIEW`. `confidence` remains `null` because no confidence-scoring method exists. Verification details and limits are in `../docs/source-verification-log.md`.
- The direct check found that the 2022-05-23 India Today article does not report a rainfall duration. The workbook had supplied an approximate two-hour duration for 14 rows linked to this article. The processed numeric durations are now null for those rows; original wording is retained in `source_duration_raw`.
- All records have `threshold_status=UNKNOWN` and `threshold_assessment="INSUFFICIENT EVIDENCE FOR THRESHOLD"`. Area-level rainfall, approximate durations and locality reports do not establish a causal road-specific threshold.

### Validation and regeneration

Install the data-processing dependencies, then run:

```powershell
python -m pip install -r data/requirements.txt
python data/process_workbook.py
python data/validate_historical_data.py
```

`process_workbook.py` reads the canonical workbook, writes the same ordered records to CSV and JSON, and prints a worksheet/record summary. `validate_historical_data.py` checks JSON Schema Draft 2020-12 compliance, CSV/JSON equivalence, types and identifiers, coordinate ranges, non-negative measurements, source-field retention against the raw workbook, preservation of `UNKNOWN` as null, duplicate flags, and separation of sample records.

**Validation run (2026-10-09):** `python data/process_workbook.py` completed and wrote 213 records to each format across 19 event groups. `python data/validate_historical_data.py` passed: CSV and JSON each contain 213 equivalent records; all 213 pass Draft 2020-12 schema validation; 213 record IDs are unique; all 213 retain source provenance; no exact duplicates were found; the one overlapping location/date group is retained and flagged; numeric rainfall/duration/intensity fields are non-negative; zero coordinate pairs are present; sample roads remain separate and have no numeric threshold. Summary: 196 rows have contextual rainfall amounts, 38 rows across 3 event groups have explicit approximate/lower-bound duration values after correcting the unsupported India Today duration, all 213 have event-context severity text, 0 have standardized road-specific severity, and 0 have road-specific rainfall or intensity. Ten source claims are checked as summarized above.

`python -m pytest -q` from `backend/`: **1 passed**. The installed Starlette/AnyIO combination emitted one deprecation warning from its test client; the health endpoint test passed.

## 11. Threshold-analysis summary

There are 213 location records across 167 city/location pairs and 19 event groups. 196 location rows carry a numeric rainfall amount, but no rainfall amount is road-specific. 38 rows carry a normalized approximate or lower-bound event-duration value across 3 event groups; none is a verified continuous rainfall duration at a specific road. All 213 carry event-context severity text, but 0 have a standardized, verified road-specific severity value. **Zero records are currently suitable to derive a road-specific rainfall-duration threshold.**
