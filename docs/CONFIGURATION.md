# Configuration Guide

The project has two separate local servers. The Node server serves the browser app on port 3000; FastAPI exposes the optional M3 risk API on port 8000. They have different configuration sources.

## 1. Node frontend server

Start from repository root:

```bash
node backend/server.js
```

The listener defaults to `127.0.0.1:3000`; override with `HOST` and `PORT` environment variables if needed. The checked-in `backend/server.js` reads `process.env` and does not automatically load a `.env` file.

### Google Maps (optional)

```bash
export GOOGLE_MAPS_BROWSER_KEY="your-restricted-browser-key"
node backend/server.js
```

PowerShell:

```powershell
$env:GOOGLE_MAPS_BROWSER_KEY = "your-restricted-browser-key"
node backend/server.js
```

`/config.js` makes this key available to the browser. Therefore it is a **public browser key**, not a server-side secret. Restrict allowed HTTP referrers and enable only the required APIs for Maps, geocoding, and routes. A working map does not prove route/geocoding APIs are enabled.

### IMD district-context proxy (optional)

Configure the credentials issued for your IMD access. The defaults assume an `Authorization` header and `Bearer` prefix only if that matches your issued credential:

```bash
export IMD_API_KEY="your-issued-credential"
export IMD_API_KEY_HEADER="Authorization"
export IMD_API_KEY_PREFIX="Bearer"
export IMD_API_KEY_MODE="header"
node backend/server.js
```

PowerShell:

```powershell
$env:IMD_API_KEY = "your-issued-credential"
$env:IMD_API_KEY_HEADER = "Authorization"
$env:IMD_API_KEY_PREFIX = "Bearer"
$env:IMD_API_KEY_MODE = "header"
node backend/server.js
```

If the issued credential uses query-string authentication, set `IMD_API_KEY_MODE=query` and `IMD_API_KEY_QUERY_PARAMETER` to the provider's documented parameter. Never place this credential in frontend JavaScript or a committed file. Endpoints: `/api/imd/warnings` and `/api/imd/rainfall`.

## 2. FastAPI risk service

From repository root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env                 # PowerShell: Copy-Item .env.example .env
```

Edit `backend/.env` and provide an evidence-reviewed road file, e.g.:

```dotenv
GARUDAROUTE_RISK_ROADS_FILE=/absolute/path/to/reviewed-road-records.json
GARUDAROUTE_RISK_ROAD_TO_LOCATION_JSON={"REVIEWED_ROAD_ID":"REVIEWED_LOCATION_ID"}
```

Use real reviewed IDs and an appropriate path. Do **not** point this setting at `../data/roads.json` for real traveller risk; that file contains synthetic fixtures. `GARUDAROUTE_RISK_ROAD_TO_LOCATION_JSON` must explicitly map road IDs to observation location IDs; mappings are not inferred. If no road file is configured, risk routes return 503.

Start the API from the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The FastAPI settings load `backend/.env` because the current working directory is `backend/`. Default API base is `http://127.0.0.1:8000`; OpenAPI docs are at `/docs`.

## 3. Connect the Node risk proxy to FastAPI

The Node proxy defaults to `http://127.0.0.1:8000`. Change it only when the API is listening elsewhere:

```bash
export GARUDAROUTE_RISK_API_BASE_URL="http://127.0.0.1:8000"
node backend/server.js
```

Keep Node and FastAPI running in separate terminals. The Node process does not launch the FastAPI process on its own.

## 4. Secret hygiene

- Do not commit `.env`, real IMD credentials, or unrestricted Google keys.
- Rotate credentials if they were pasted into a public repository, issue, chat, or screenshot.
- Keep a Google browser key restricted because browsers must receive it.
- Do not treat provider credentials or successful HTTP responses as proof that the returned data is road-specific.
