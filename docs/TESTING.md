# Testing and Verification Guide

Use unit tests to check logic, API tests to check local service contracts, and browser/provider checks to verify external integrations. One category does not replace another.

## 1. JavaScript geometry and route scoring

From repository root:

```bash
node --test tests/routing-logic.test.js
```

Covers route-risk scoring/selection and geometry helpers, including segment-distance edge cases.

## 2. Node server / IMD proxy tests

From repository root:

```bash
node --test tests/imd-proxy.test.js
node --check backend/server.js
```

These checks do not prove the real IMD service accepts the configured credentials.

## 3. M3 Python service tests

From repository root:

```bash
python -m unittest discover -s risk-engine/tests -v
```

Covers tracker, comparator, risk engine, and service-facade behaviour.

## 4. FastAPI route and adapter tests

Install the backend requirements first:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

The backend test suite includes route behaviour using a fake facade and integration with the M3 service. Test execution should use the test output from the current commit rather than a copied count in a report.

## 5. Git and documentation checks

From repository root:

```bash
git diff --check
```

Before committing a docs-only update, confirm the documentation does not claim that an optional provider was live-tested unless it actually was.

## 6. Manual browser smoke test

1. Start `node backend/server.js` and open `http://127.0.0.1:3000`.
2. Confirm the dashboard and bundled historical records load.
3. Switch between Kanpur, Gurugram, and Both; open a location and check source links/details.
4. Drag the rainfall/reference clock and confirm the historical classifications update. Remember: this is a reference/simulation view, not live rainfall.
5. Confirm the map displays. If Google Maps fails, inspect the console and network panel for key/referrer/API issues and check whether OpenStreetMap fallback is active.
6. If testing routes, submit a valid origin/destination and verify the actual route response. Do not infer routing success from map initialization alone.
7. If testing IMD, check credentials, proxy response status, timestamp, and district scope. An unavailable feed must remain unavailable.
8. If testing the risk panel, start FastAPI separately, configure a reviewed road file/mapping, and inspect `data_freshness`/`risk_level`. Without configuration the service should report unavailable rather than normal.
9. Check the browser console for errors.

## 7. External and end-to-end checks not implied by unit tests

Unit tests alone do not confirm:

- Google Maps tiles, geocoding, or route service availability;
- browser key restrictions and allowed referrers;
- browser geolocation permissions;
- real IMD credential acceptance and response freshness;
- any verified live rainfall feed into M3;
- valid road-segment geometry or evidence-backed thresholds;
- route safety in real flood conditions.

Document the date, environment, exact check, and result whenever an integration is manually verified.
