# Team Board

## M1 — Integration / Architecture

- [x] project_spec.md
- [ ] ARCHITECTURE.md
- [ ] API_CONTRACT.md
- [ ] DATA_SCHEMA.md
- [ ] TEAM_BOARD.md
- [ ] Review M3 facade
- [ ] Integrate M2 + M3

### M2 — Historical Data
- [x] Verify ten priority location records against the cited sources; document limitations
- [x] Build historical_waterlogging.csv from source-linked workbook rows
- [x] Build historical_waterlogging.json from the same normalized records
- [x] Document source domains, provenance and limitations
- [x] Identify threshold suitability: current records are insufficient for a road-specific threshold
- [x] Add initial FastAPI health-check scaffold

Current data status: 213 location rows across 19 source/date groups; 10 claims are source-verified and 203 remain under review. None supports road-specific threshold derivation.

- [ ] Identify official sources
- [ ] Collect first 5–10 records
- [ ] Build historical CSV
- [ ] Build historical JSON
- [ ] Document provenance
- [ ] Determine threshold candidates

## M3 — Risk Engine

- [x] Initial risk engine
- [x] Initial unit tests
- [ ] Remove dead code
- [ ] Implement facade
- [ ] Improve stale-data handling
- [ ] Improve duplicate handling
- [ ] Add facade tests
- [ ] Finalize API interface

## M4 — Frontend

ON HOLD

Do not start frontend integration until the API contract is stable.

## Upcoming

- [ ] Historical data → risk engine
- [ ] Real IMD data
- [ ] Backend
- [ ] Google Maps
- [ ] Alerts
- [ ] AWS deployment
