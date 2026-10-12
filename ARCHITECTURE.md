# System Architecture

## 1. Summary

The current `main` application is a local-development prototype made of a browser dashboard, a small Node.js HTTP server, a separate optional FastAPI service, and the M3 Python risk-engine module. Historical evidence, district weather, and M3 assessments are separate inputs. The default setup does not automatically turn a live weather feed into verified risk for every road.

## 2. Component diagram

```text
Historical research workbook
        │ reviewed / normalized export
        ├──> data/processed/historical_waterlogging.{csv,json}
        │
        └──> curated dashboard dataset
             frontend/data/road-waterlogging-records.json
                         │
                         ▼
Browser dashboard (frontend/index.html)
  ├── historical rainfall/reference clock and filters
  ├── Google Maps when configured; OpenStreetMap fallback
  ├── optional Google route comparison / geocoding
  ├── optional IMD district-weather cards
  └── optional M3 risk table
       │                    │
       │ same-origin IMD     │ same-origin risk proxy
       ▼                    ▼
Node.js server         FastAPI app (separate process)
backend/server.js      backend/app/main.py
                            │
                            ▼
                   RiskServiceAdapter
                            │ delegates
                            ▼
                   M3 WaterloggingRiskService
                   ├── observation validation/ingest
                   ├── continuous rainfall tracker
                   ├── data freshness and gap policy
                   └── empirical threshold comparator
```

## 3. Browser dashboard

`frontend/index.html` contains the dashboard structure and its browser-side behaviour. It loads:

- `/config.js` — serves the configured Google Maps browser key to the page;
- `/records.js` — serves the bundled historical event dataset;
- `/risk-utils.js` — serves shared route-geometry and scoring functions.

The map layer tries Google Maps when a key is configured and the required Google service loads. It falls back to OpenStreetMap if Google Maps cannot be used. The OSM fallback is a map display fallback; it does not provide Google-specific geocoding or route calculation.

The historical clock compares user-controlled values with reported historical reference values. The dashboard's reference levels use a 75% monitor threshold and 100% high-risk threshold relative to each available reference value. This UI logic is not the M3 risk engine and is not a calibrated flood model.

## 4. Node.js HTTP server

`backend/server.js` uses Node's built-in HTTP/HTTPS modules and serves the frontend plus proxy endpoints. The default listener is `127.0.0.1:3000`.

Responsibilities:

- serve the dashboard and its config/data/helper scripts;
- keep IMD credentials on the server while proxying district warning and rainfall requests;
- proxy optional dashboard risk requests to the separate FastAPI service (default upstream `http://127.0.0.1:8000`).

The Node server does not start the FastAPI process. It reads configuration from environment variables; the checked-in JavaScript server does not automatically load a `.env` file.

## 5. FastAPI risk API and M3 module

`backend/app/main.py` mounts the health and risk routers. `RiskServiceAdapter` is a thin adapter around `WaterloggingRiskService`, not a second risk calculator. The service must be configured with a road dataset and explicit `road_id -> location_id` mapping before assessments can be calculated.

The M3 engine tracks observations per location in process memory. It uses a maximum observation gap to manage continuous-rainfall duration and a freshness threshold to identify stale values. By default, the comparator enters `MONITOR` at 70% of the configured historical threshold and `HIGH_RISK` at 100% or above.

Risk observations posted through the current API are demo/testing inputs; there is no built-in live IMD ingestion worker or durable observation store in this baseline. Process restart clears in-memory observations.

## 6. Data layers and trust boundaries

| Data layer | Purpose | Trust boundary |
|---|---|---|
| Raw historical workbook | Original source-named incident and rainfall context | Preserve as evidence; do not edit originals |
| `data/processed/` exports | Normalized workbook rows with provenance and uncertainty fields | 213 rows across 19 event groups; most need source review |
| Browser historical JSON | Smaller interactive dashboard feed | 10 event records across 7 locations; reported rainfall may not be road-specific |
| `data/roads.json` | Risk-engine fixture | Synthetic identifiers/thresholds; not for live traveller safety claims |
| Explicit road-to-location mapping | Connects a road record to one observation location for M3 | Must be evidenced/configured; never infer from ID/name/proximity |
| IMD district response | Optional current district warning/rainfall context | District context, not precise per-road rainfall |
| M3 assessment | Deterministic status from supplied observations and configured threshold | UNKNOWN/stale/unmapped must not be shown as safe |

## 7. Security and reliability

- Google Maps key: intentionally sent to the browser by `/config.js`; it is a public browser key. Restrict HTTP referrers and enable only needed APIs.
- IMD credential: belongs in the Node server environment, never in browser code or committed documentation.
- FastAPI config: uses `GARUDAROUTE_*` variables and an optional `backend/.env` loaded by Pydantic Settings when started with `backend/` as the working directory.
- Missing provider/service responses must remain unavailable/error states, not be interpreted as normal conditions.
- M3 process memory is not durable or shared between workers.

## 8. Current architecture gaps

1. No verified end-to-end provider ingestion to validated road-specific risk exists by default.
2. Historical event records lack reliable road-segment geometry and rainfall duration adequate to derive road-level thresholds.
3. The 213-row research dataset and the 10-event browser feed are separate; there is no automatic, evidence-validating merge between them.
4. Production persistence, monitoring, deployment automation, and field validation remain future work.

See [Current Status](docs/CURRENT_STATUS.md), [API Contract](API_CONTRACT.md), [Data Schema](DATA_SCHEMA.md), and [Risk Model](docs/risk-model.md).
