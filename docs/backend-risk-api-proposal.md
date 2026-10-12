# Backend Risk API — Implementation Notes

**Status:** Implemented in the checked-in baseline. This file describes the current integration rather than a pending proposal; the normative route/field contract is [`../API_CONTRACT.md`](../API_CONTRACT.md).

## Scope

The FastAPI application is a thin HTTP adapter around M3's `WaterloggingRiskService`. `backend/app/services/risk_service_adapter.py` configures/imports the existing facade and translates service exceptions. It does not implement a second risk calculator.

## Route summary

- `GET /api/health` — service health.
- `GET /api/roads/risk?as_of=<ISO-8601>` — returns `{ "roads": [...], "count": n }`.
- `GET /api/roads/{road_id}/risk?as_of=<ISO-8601>` — returns one assessment.
- `POST /api/observations` — ingests demo/testing observations into memory only.

Risk routes return HTTP 503 until a road file is configured. Unknown roads return 404, invalid timestamps/payloads 422, conflicting observations 409. Known unmapped roads remain `UNKNOWN` / `UNMAPPED`. Assessments preserve M3 field names and risk enum values.

## Node-to-FastAPI proxy

The browser talks to the Node server:

- `GET /api/risk/roads` -> FastAPI `GET /api/roads/risk`
- `GET /api/risk/roads/{road_id}/risk` -> FastAPI `GET /api/roads/{road_id}/risk`

Node's default upstream is `http://127.0.0.1:8000`, configurable through `GARUDAROUTE_RISK_API_BASE_URL`.

## Configuration requirements

Configure `GARUDAROUTE_RISK_ROADS_FILE` and `GARUDAROUTE_RISK_ROAD_TO_LOCATION_JSON` through FastAPI's environment or `backend/.env`. The root `data/roads.json` is a synthetic fixture and should not be used for real traveller safety decisions. Use only an evidence-reviewed road record and an explicit mapping.

Observation state is in memory and resets on restart. The API has no built-in live weather adapter or persistence layer. A successful manual observation POST is therefore not evidence of an operational live-rainfall integration.

## Tests

See `backend/tests/` for route and adapter tests. Run them after installing `backend/requirements.txt`:

```bash
cd backend
python -m pytest -q
```
