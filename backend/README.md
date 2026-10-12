# Garuda Route FastAPI Backend

The FastAPI service exposes health and risk APIs. Risk calculation and observation tracking are delegated through `RiskServiceAdapter` to the M3 `WaterloggingRiskService`; FastAPI does not implement a second risk formula. This service is separate from `backend/server.js`, which serves the browser app on port 3000 and proxies optional requests to the API.

## Requirements

- Python 3.10 or newer.
- Dependencies from `requirements.txt`.

## Install and run

From the repository root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env               # Windows PowerShell: Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The service listens on `http://127.0.0.1:8000` by default. Health is `GET /api/health`; interactive OpenAPI docs are at `/docs`.

## Configuration

Settings use the `GARUDAROUTE_` prefix and Pydantic Settings loads the optional `.env` from the current working directory. Start `uvicorn` from `backend/` so it reads `backend/.env`.

Example variables (replace paths/IDs with reviewed data; values below are placeholders):

```dotenv
GARUDAROUTE_RISK_ROADS_FILE=/absolute/path/to/reviewed-road-records.json
GARUDAROUTE_RISK_ROAD_TO_LOCATION_JSON={"REVIEWED_ROAD_ID":"REVIEWED_LOCATION_ID"}
```

If `GARUDAROUTE_RISK_ROADS_FILE` is not configured, the adapter is unconfigured and risk endpoints return HTTP 503. The root `data/roads.json` currently contains synthetic examples and must not be used for real traveller warnings. Road mappings must be explicit and evidenced.

## Endpoints

- `GET /api/health`
- `GET /api/roads/risk?as_of=<ISO-8601-with-timezone>`
- `GET /api/roads/{road_id}/risk?as_of=<ISO-8601-with-timezone>`
- `POST /api/observations` — demo/testing only, in-memory

The collection response has shape `{"roads": [...], "count": n}`. Individual assessments preserve M3's field names and values. Missing data, stale observations, unmapped roads, unknown risk, or unavailable thresholds must not be shown as safe.

The observation endpoint updates in-process state only. It is not an IMD integration, durable datastore, or production telemetry endpoint. Observations disappear when the process restarts.

See the root [`API_CONTRACT.md`](../API_CONTRACT.md), [`risk-engine/README.md`](../risk-engine/README.md), and [configuration guide](../docs/CONFIGURATION.md).

## Tests

With dependencies installed, run from `backend/`:

```bash
python -m pytest -q
```

The tests include route-contract behaviour and integration with the M3 facade. Passing them does not validate external weather credentials or evidence-backed road thresholds.
