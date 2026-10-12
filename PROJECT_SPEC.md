# Garuda Route — Project Specification

## 1. Problem

Rainfall and waterlogging reports are often broad, fragmented, or difficult for travellers to relate to individual locations. A traveller may know that a city has had heavy rain but lack enough context to understand where waterlogging has previously been reported or how a proposed route intersects those locations.

Garuda Route explores how source-linked historical incident records, rainfall context, and route comparison could support better awareness. The longer-term system may evaluate rainfall observations against evidence-backed road-specific indicators, but the current prototype does not claim complete real-time, road-level prediction.

## 2. Product goals

1. Make the provenance and limitations of historical waterlogging reports easy to inspect.
2. Let users explore reported rainfall context and its relationship to past events.
3. Show documented locations on a map and allow location/city filtering.
4. Compare route options against locations currently flagged by the browser's historical reference heuristic when mapping APIs are configured.
5. Maintain a separate, testable M3 engine and API contract for future road-level empirical risk assessments.
6. Make data gaps, stale inputs, unmapped roads, and uncertainty explicit.

## 3. Current prototype scope

### Implemented in the checked-in baseline

- Browser dashboard for the curated historical dataset (10 events across 7 locations).
- Kanpur, Gurugram, and combined city scopes.
- Location details, source links, historical table/summary, and filters.
- User-controlled rainfall/reference clock with non-live exploration modes.
- Map initialization using Google Maps when configured and OpenStreetMap fallback when it cannot be used.
- Google-based route comparison/geocoding when the browser key and required APIs are available.
- Node.js server for frontend assets, IMD district-weather proxy routes, and an optional proxy to FastAPI risk endpoints.
- Python M3 risk engine and a separate FastAPI adapter/API with health, risk-query, and in-memory observation-ingest endpoints.
- JavaScript, Python, and backend regression-test suites.

### Conditional integrations

- Google Maps requires a restricted `GOOGLE_MAPS_BROWSER_KEY` and the required Google APIs enabled for the key/project.
- IMD district context requires valid credentials and authentication settings supplied by the provider.
- The risk API needs the FastAPI process running and a reviewed road dataset plus explicit road-to-location mappings. The API is unconfigured by default.

## 4. Functional requirements

| ID | Requirement | Baseline status |
|---|---|---|
| FR-01 | Show source-linked historical waterlogging locations | Implemented for curated dashboard feed |
| FR-02 | Preserve source context, unknowns, and limitations | Implemented in dataset/documentation; source review remains incomplete |
| FR-03 | Filter by Kanpur, Gurugram, or both | Implemented |
| FR-04 | Compare reference rainfall values with a user-controlled clock | Implemented as historical exploration; not a sensor feed |
| FR-05 | Display locations on a map | Implemented with Google/OSM fallback |
| FR-06 | Compare candidate routes with currently flagged locations | Conditional on Google Maps route services; no safety guarantee |
| FR-07 | Retrieve district warnings/rainfall through the Node backend | Endpoint and UI implemented; live availability depends on IMD credentials/provider response |
| FR-08 | Track continuous rainfall duration by observation location | Implemented in M3 service when observations are supplied |
| FR-09 | Return risk for explicitly configured roads | Implemented in FastAPI/M3 path when configured; otherwise unavailable |
| FR-10 | Persist telemetry across process restarts | Not implemented |
| FR-11 | Derive validated thresholds from historical incidents | Not supported by the current evidence; future research task |
| FR-12 | Provide production-grade live ingestion, monitoring, and deployment | Future work |

## 5. Risk model requirements

The M3 engine is deterministic and rule-based. It compares current continuous rainfall duration with a configured historical threshold. Default monitor ratio is 0.70; `MONITOR` means the duration has reached that fraction of a threshold, and `HIGH_RISK` means the threshold has been reached or exceeded. This is a heuristic indicator, not a physically based flood model or calibrated flood probability.

The browser's historical comparison has a separate heuristic: it compares the rainfall clock with reported historical reference amounts and uses its own threshold ratios. The UI result must not be described as an M3 assessment.

## 6. Non-goals

- Certified flood forecasting or a claim that flooding is certain.
- Hydraulic modelling of drainage, topography, runoff, river levels, or flow propagation.
- Nationwide coverage or a complete official incident inventory.
- Treating city/district rainfall as a road-level measurement.
- Inferring road-to-station mappings from identifiers, names, or nearest-point matching without validation.
- Guaranteeing a safe route or replacing official emergency advice.
- Autonomous traffic control.

## 7. Acceptance criteria for future live risk routing

Before recommending a route based on live risk, require:

1. A reviewed historical record and defensible threshold for the particular road or segment.
2. Verified road geometry/identity and a reviewed explicit observation-source mapping.
3. Fresh timestamped observations from an authorized source, with a documented adapter and failure policy.
4. Consistent `UNKNOWN`, `NO_DATA`, `STALE`, `UNMAPPED`, and missing-threshold semantics.
5. Tests for missing/stale/conflicting observations and route/road geometry edge cases.
6. Browser verification and an independent evaluation method using reviewed event data.
7. Clear UI wording that distinguishes evidence, observations, computed status, and uncertainty.

## 8. Project success metrics

Potential KPIs include historical evidence coverage, reviewed road-mapping coverage, observation freshness, route calculation success, risk API p50/p95 latency, and classification quality against independently reviewed labels. Definitions and formulas are in [docs/PROJECT_KPIS.md](docs/PROJECT_KPIS.md). These are metrics to instrument and evaluate; no numerical performance or accuracy claim is made here.

## 9. Current status

See [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md) for the implementation inventory and priority next steps.
