# Current Implementation Status

This page documents the checked-in pre-command-centre/pre-Google-Weather baseline. Use it as the cross-project status source; module-specific notes remain in each folder's README.

## Feature status

| Feature | Status | Notes |
|---|---|---|
| Historical dashboard | Implemented | Curated browser feed has 10 events across 7 locations |
| City selector | Implemented | Kanpur, Gurugram, both |
| Historical reference clock | Implemented | Interactive exploration, not a live sensor clock |
| Map | Implemented with fallback | Google Maps where configured; OpenStreetMap fallback if Google Maps cannot be used |
| Route option comparison | Conditional | Google routing service/key/API setup required; not a safety guarantee |
| IMD district warnings/rainfall | Conditional | Node proxy routes exist; authorized credentials and provider access needed |
| M3 rainfall tracker and risk engine | Implemented as a module | Deterministic, in-memory observation state |
| FastAPI risk endpoints | Implemented, unconfigured by default | Configure a reviewed road file and explicit mapping; otherwise returns 503 |
| Manual observation POST | Demo/testing only | In-memory; not live provider ingestion and not persistent |
| Google Weather API | Not in this baseline | Experimental work was rolled back |
| Three-column command-centre redesign | Not in this baseline | Experimental redesign was rolled back |
| Evidence-supported road thresholds | Not yet available from the current dataset | No normalized workbook row currently establishes a road-specific rainfall-duration threshold |
| Production persistence and deployment | Planned | Not part of the local prototype |

## Important counts and provenance

- Browser dataset: 10 historical event records across 7 locations.
- Research workbook: 213 source-named incident/location rows in 19 event groups.
- Source review: 10 priority claims were directly checked against cited articles; 203 rows remain under review.
- Threshold suitability: current workbook evidence is insufficient to derive validated road-specific rainfall-duration thresholds.
- `data/roads.json`: synthetic software fixture, not production configuration.

These counts describe different data layers; do not conflate them.

## Risks and constraints

1. A place name or approximate coordinate is not a verified road-segment geometry.
2. City/district rainfall is not a per-road observation.
3. A missing observation does not mean rain stopped.
4. `UNKNOWN`, `NO_DATA`, `STALE`, and `UNMAPPED` are not synonyms for `NORMAL` or safe.
5. The dashboard historical comparison uses a different heuristic from the M3 engine.
6. Google Map display success does not prove route comparison works; route service and API activation must be tested separately.
7. IMD proxy presence does not prove live feed availability; use explicit unavailable states when credentials/provider fail.

## Recommended next work

1. Finish source review and preserve provenance/uncertainty.
2. Establish validated road-segment identity and geometry.
3. Research thresholds using enough event-linked evidence; do not substitute city totals or event windows.
4. Define explicit observation mappings and a real ingest adapter with timeout/freshness policies.
5. Add persistent storage and operational monitoring before production use.
6. Instrument and measure coverage, observation freshness, route success, API latency, and classification quality before publishing KPI values.

## Reporting rule

Distinguish checks done in unit tests from browser/provider verification. Never claim live weather, Google route calculation, or map tile loading was verified unless that exact integration was exercised in the target environment.
