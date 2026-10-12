# Documentation Refresh Notes

## Scope

This documentation proposal is aligned to the pre-command-centre, pre-Google-Weather baseline on `main`. It does not change application code or assert that optional external integrations were live-tested.

## Files included for replacement/addition

- `README.md`
- `ARCHITECTURE.md`
- `PROJECT_SPEC.md`
- `API_CONTRACT.md`
- `DATA_SCHEMA.md`
- `CHANGELOG.md`
- `TEAM_BOARD.md`
- `backend/README.md`
- `risk-engine/README.md`
- `risk-engine/M3_PROGRESS.md`
- `docs/CURRENT_STATUS.md` (new)
- `docs/CONFIGURATION.md` (new)
- `docs/TESTING.md` (new)
- `docs/risk-model.md`
- `docs/integration-plan.md`
- `docs/backend-risk-api-proposal.md`

## Existing research documentation deliberately preserved

The following documents contain detailed provenance/evidence research and should remain intact unless a record-specific review justifies a change:

- `data/README.md`
- `docs/data-sources.md`
- `docs/existing-systems.md`
- `docs/historical-data-methodology.md`
- `docs/source-verification-log.md`

The normalized dataset/schema and source verification notes are complementary; this refresh avoids replacing detailed source records with a shorter summary.

## Key consistency corrections

- Frontend is no longer described as “on hold” or merely planned.
- FastAPI risk API routes are documented as implemented but unconfigured by default, not as a pending proposal.
- Node browser-facing paths (`/api/risk/roads...`) are distinguished from FastAPI paths (`/api/roads...`).
- The browser historical heuristic is separate from M3's 70%-threshold engine.
- The 10-record/7-location browser feed is distinguished from the 213-row/19-group research workbook.
- Old M3 branch/test-count statements are removed from the progress page.
- Google Weather API and the experimental three-column command-centre layout are explicitly not part of this baseline after rollback.
