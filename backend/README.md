# GarudaRoute backend foundation

FastAPI backend scaffold for local development. It exposes a health check and the initial M3 risk API routes. Risk calculations are delegated to M3's `WaterloggingRiskService`; this backend does not implement a separate risk calculator.

## Requirements

- Python 3.10 or newer

## Install and run

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The health endpoint is `GET http://127.0.0.1:8000/api/health`. Risk routes are `GET /api/roads/risk`, `GET /api/roads/{road_id}/risk`, and `POST /api/observations`. Open `/docs` for the local OpenAPI page.

## Risk API integration status

The routes are implemented and the adapter loads the root `risk-engine/engine/service.py` facade when configured. The M3 package was merged from `origin/main`; the nullable-threshold and unmapped-road fixes are covered by M3 regression tests. No second engine copy was created.

Risk routes return HTTP 503 by default until an evidence-backed roads file is configured with `GARUDAROUTE_RISK_ROADS_FILE`. Supply explicit mappings with `GARUDAROUTE_RISK_ROAD_TO_LOCATION_JSON`, for example `{"ROAD_ID":"LOCATION_ID"}`. Unmapped roads remain `UNKNOWN` / `UNMAPPED`. Do not use the current `data/roads.json` synthetic thresholds for real traveller alerts.

`GET /api/roads/risk` returns `{"roads": [...], "count": n}`. Risk assessments are passed through with M3's field names and enum values. Missing data, stale data, unmapped roads, and unavailable thresholds must not be displayed as safe. Unknown road IDs return 404; malformed timestamps and observations return 422; conflicting observations return 409.

`POST /api/observations` is for demo/testing only. It updates the in-memory M3 service instance and is not a live rainfall feed or persistent storage. Observations are lost when the process restarts.

See the root [`API_CONTRACT.md`](../API_CONTRACT.md) for the request and response contract. The backend test suite includes both route-contract tests with a fake facade and integration tests using M3's actual facade.

## Tests

With the environment activated, run from `backend/`:

```powershell
python -m pytest -q
```

## Configuration

Settings load from `GARUDAROUTE_*` environment variables and, for local development, an optional `.env` file. `.env` is ignored by Git. Never put secrets in `.env.example`.

## Risk service boundary

`app/services/risk_service_adapter.py` delegates to the published M3 facade methods and translates M3 exceptions to backend errors. `RiskServiceAdapter.from_roads_file(...)` loads the existing M3 service and requires an explicit road mapping; it does not construct a second risk engine or infer mappings.
