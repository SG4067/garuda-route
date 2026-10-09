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

The routes and `RiskServiceAdapter` are implemented and dependency-injectable. By default the app returns HTTP 503 from risk routes until an M3 service instance is bound to `app.state.risk_service_adapter`. The frontend branch currently does not contain the M3 package, and no duplicate copy has been added. Bind the root `risk-engine/engine/service.py` implementation after it is integrated and its nullable-threshold fix is verified. The routes are contract-tested with a fake M3 facade; those tests exercise HTTP behavior, not M3 calculations.

`GET /api/roads/risk` returns `{"roads": [...], "count": n}`. Risk assessments are passed through with M3's field names and enum values. Missing data, stale data, unmapped roads, and unavailable thresholds must not be displayed as safe. Unknown road IDs return 404; malformed timestamps and observations return 422; conflicting observations return 409.

`POST /api/observations` is for demo/testing only. It updates the in-memory M3 service instance and is not a live rainfall feed or persistent storage. Observations are lost when the process restarts.

See the root [`API_CONTRACT.md`](../API_CONTRACT.md) for the full request and response contract. The known M3 nullable-threshold serialization issue must be fixed upstream before binding and end-to-end integration tests can pass.

## Tests

With the environment activated, run from `backend/`:

```powershell
python -m pytest -q
```

## Configuration

Settings load from `GARUDAROUTE_*` environment variables and, for local development, an optional `.env` file. `.env` is ignored by Git. Never put secrets in `.env.example`.

## Risk service boundary

`app/services/risk_service_adapter.py` delegates to the published M3 facade methods and translates M3 exceptions to backend errors. Inject a `WaterloggingRiskService` instance through `RiskServiceAdapter(instance)`; the adapter intentionally does not construct a second risk engine.
