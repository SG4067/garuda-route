# Real-Time Road Waterlogging Alert and Route Diversion System

> Early warning and route-diversion system based on current rainfall
> conditions and historical road waterlogging patterns.

## Status

🚧 Under Development

## Project Specification

See [project_spec.md](project_spec.md).

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md).

## Current Components

- Risk Engine
- Rainfall Tracker
- Threshold Comparator

## Planned Components

- Live rainfall integration
- Backend API
- Map
- Traveller alerts
- Route diversion
- AWS deployment

## Repository Structure

...

## Development

The dashboard loads its checked-in historical dataset from
`frontend/data/road-waterlogging-records.json`, exported from
`road_waterlogging_historical_records.xlsx`. The header reports the source,
event count, and location count. The Import spreadsheet control previews a
replacement in the current browser session; it does not overwrite the bundled
dataset.

### Run the local app

Requires Node.js 18 or newer. The frontend is served by a small same-origin
backend so IMD credentials stay on the server instead of being exposed in
browser code.

In PowerShell, set the credential format issued for your IMD access, then run:

```powershell
$env:IMD_API_KEY = "your-issued-key"
$env:IMD_API_KEY_HEADER = "Authorization"
$env:IMD_API_KEY_PREFIX = "Bearer"
node backend/server.js
```

Open `http://127.0.0.1:3000`. Adjust `IMD_API_KEY_HEADER` and
`IMD_API_KEY_PREFIX` to match the exact authentication instructions supplied
with your IMD credential. The API reference documents district warning codes
and rainfall fields, but not the credential format. `IMD_API_KEY_MODE=query`
and `IMD_API_KEY_QUERY_PARAMETER` are available if the credential is issued
for query-string authentication.

An optional restricted Google Maps browser key can be set as
`GOOGLE_MAPS_BROWSER_KEY`. Without it the app uses OpenStreetMap; Google route
comparison and geocoding are then unavailable.

## Disclaimer

The system provides empirical waterlogging risk indicators and does not
guarantee that flooding will occur.
