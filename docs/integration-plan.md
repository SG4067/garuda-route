# Integration Plan — As-Built and Remaining Work

This replaces the original purely future-oriented phase list with the current baseline plus the remaining work required before live road-risk recommendations.

## Phase A — Historical data and dashboard (implemented baseline)

```text
Source workbook -> provenance/normalization -> processed CSV/JSON
                                  \
                                   -> curated dashboard JSON -> browser views/map
```

The research workbook contains 213 location rows across 19 event groups. The browser currently loads a separate curated feed of 10 event records across 7 locations. Ten priority claims were directly checked against cited articles; 203 workbook rows remain under review. No workbook row currently establishes a road-specific continuous-rain threshold.

## Phase B — Browser and map (implemented, provider-dependent)

The browser dashboard provides city selection, historical reference clock, location detail/history/alerts, map display, and route comparison when Google Maps services are configured. Google Maps has an OpenStreetMap fallback for map display. The fallback does not replace Google-specific routing/geocoding APIs.

## Phase C — Node backend (implemented baseline)

`backend/server.js` serves the app and data/config scripts, proxies IMD district endpoints, and proxies optional risk requests to FastAPI. It does not load `.env` automatically and does not start FastAPI.

## Phase D — M3 risk engine and FastAPI (implemented, unconfigured by default)

FastAPI -> `RiskServiceAdapter` -> `WaterloggingRiskService` -> tracker + threshold comparator.

Risk routes need an evidence-reviewed road file and explicit road-to-location mapping. Observation POST is an in-memory demo/testing endpoint and is not a live rainfall feed.

## Phase E — Work required for live road-level risk

1. Finish reviewing the historical evidence.
2. Identify road segments and verify geometry/identity.
3. Derive a candidate threshold only when supporting evidence justifies it; label threshold quality.
4. Select authorized observation data and implement a real adapter with timestamp/freshness/error behaviour.
5. Explicitly map eligible roads to observation locations; never infer mappings from names, IDs, or proximity.
6. Keep unknown/stale/unmapped states visible and out of “safe” recommendations.
7. Validate against an independent event set and instrument performance/coverage KPIs.
8. Add durable storage, monitoring, deployment and recovery procedures before production.

## Phase F — Production hardening (future)

- Durable telemetry storage and a clear retention policy.
- Authentication/authorization and API quotas as appropriate.
- Secret management, structured logs, metrics, alerting, and provider outage behaviour.
- Reproducible deployment and rollback processes.
- Accessibility, mobile layout, performance, and usability verification.

Do not describe phases E/F as delivered until code, tests, and evidence support that claim.
