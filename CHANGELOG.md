# Changelog

This file records meaningful changes to the checked-in baseline. Documentation-only changes do not imply that application code or external integrations were deployed.

## Unreleased — documentation refresh

### Documentation
- Reconcile project status, architecture, API routes, data semantics, and setup instructions with the current `main` baseline.
- Separate the browser's historical reference heuristic from the M3 continuous-rainfall risk engine.
- Document Node proxy endpoints separately from upstream FastAPI endpoints.
- Add current status, configuration, and testing guides.
- Clarify that IMD district context is credential-dependent, API observations are demo/testing input, and M3 state is in-memory.

## 2026-10-09 — recorded baseline work

### Added / integrated in the baseline
- Project specification, architecture/API/data-schema documentation, and source provenance notes.
- Historical waterlogging research workbook plus processed CSV/JSON exports.
- Curated browser dataset with 10 historical event records across 7 locations.
- Browser dashboard with city filtering, rainfall/reference clock, location details, historical views, map fallback, and conditional route comparison.
- Node server routes for frontend config/data/helper scripts and IMD district-context proxying.
- M3 `WaterloggingRiskService`, continuous rainfall tracker, threshold comparator, and regression tests.
- FastAPI risk API adapter/routes delegating to the M3 service.

### Current limitations
- Ten priority historical claims have been checked against their cited articles; 203 of the 213 workbook rows remain under review.
- The research workbook does not establish road-specific rainfall-duration thresholds.
- The default root road-threshold JSON is illustrative and not suitable for real traveller risk warnings.
- Live provider credentials, Google APIs, and the separate risk API require local configuration.
