# Team Board — Current Baseline

This board reflects the code and documentation in `main` at the pre-command-centre/pre-Google-Weather baseline. It is not a claim that every optional provider has been tested with live credentials.

## Current status at a glance

| Area | Status | Notes / next step |
|---|---|---|
| Browser historical dashboard | Implemented | Curated feed: 10 event records across 7 locations; source evidence remains limited |
| Map display | Implemented with fallback | Google Maps first when configured; OSM fallback if Google Maps cannot load |
| Google route comparison / geocoding | Conditional | Needs a valid, restricted browser key and necessary APIs; browser test required |
| Node frontend server | Implemented | Serves page/config/data/helper and proxies optional services |
| IMD district weather proxy | Implemented as adapter routes | End-to-end availability depends on authorized credentials and provider response |
| M3 risk engine | Implemented as a Python module | Deterministic service/tracker/comparator; data is in-memory |
| FastAPI risk API | Implemented, configurable | Returns 503 until a reviewed road file is configured |
| Historical data normalization | Implemented | 213 workbook rows / 19 event groups; ten claims checked, 203 remain under review |
| Evidence-backed road thresholds | Not ready | Current research does not support road-specific continuous-rain thresholds |
| Verified road-to-observation mapping | Not ready as a real-data default | Must be explicitly researched/configured; root fixtures are synthetic |
| Persistent telemetry / production deployment | Planned | Requires storage, operations, auth/monitoring, and deployment design |
| Google Weather API integration | Not in this baseline | Previously experimental branch feature was rolled back |
| Three-column command-centre UI redesign | Not in this baseline | Experimental redesign was rolled back; baseline layout remains |

## Completed baseline capabilities

- [x] Browser dashboard for curated historical events and locations.
- [x] City filter for Kanpur, Gurugram, and both.
- [x] User-controlled historical reference clock and risk-category visualization.
- [x] Location detail/history/alert views and source links.
- [x] Google Maps/OSM map selection logic and conditional route comparison.
- [x] Node.js static serving and same-origin IMD/risk proxies.
- [x] M3 `WaterloggingRiskService`, observation tracking, duplicate/conflict handling, freshness behaviour, null-threshold behaviour, and explicit road mappings.
- [x] FastAPI adapter and route tests; it delegates risk calculation to M3.
- [x] Data processing scripts, JSON Schema files, research methodology, source verification log, and data limitations.

## Priorities before live road-risk recommendations

1. **Evidence:** finish reviewing the remaining workbook sources and preserve the difference between source verification and official corroboration.
2. **Road identity:** identify stable road segments and verified geometry from an authoritative/reviewed source.
3. **Threshold research:** do not derive road thresholds from city totals or event windows; document method and evidence for any threshold candidate.
4. **Observation mapping:** explicitly map each eligible road to the observation source actually used; no ID or proximity inference.
5. **Live ingestion:** implement a source adapter with timestamps, update cadence, timeouts, invalid-data handling, and outage behaviour. Do not treat manual `/api/observations` posts as a live feed.
6. **Validation:** compare classifications to an independent reviewed event set and report measurable KPIs only after establishing methodology.
7. **Operations:** add persistence, service health/monitoring, credential management, and deployment/runbook before production use.

## Test commands

```bash
node --test tests/routing-logic.test.js
node --test tests/imd-proxy.test.js
python -m unittest discover -s risk-engine/tests -v
node --check backend/server.js
```

For FastAPI tests, install `backend/requirements.txt` and run `python -m pytest -q` from `backend/`. See [`docs/TESTING.md`](docs/TESTING.md).
