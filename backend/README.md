# GarudaRoute backend foundation

Minimal FastAPI scaffold for local development. It currently exposes a health check only. Historical data processing is documented under `../data/`; the M3 risk service is not connected until its public interface is finalized.

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

The health endpoint is `GET http://127.0.0.1:8000/api/health`. Open `/docs` for the local OpenAPI page.

## Tests

With the environment activated, run from `backend/`:

```powershell
python -m pytest -q
```

## Configuration

Settings load from `GARUDAROUTE_*` environment variables and, for local development, an optional `.env` file. `.env` is ignored by Git. Never put secrets in `.env.example`.

## Risk service boundary

`app/services/risk_service_adapter.py` is intentionally an unbound integration point. It does not calculate risk or assume M3's constructor, method names or response fields. Wire it after M3 publishes a final tested interface.
