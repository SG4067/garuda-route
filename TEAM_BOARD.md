# TEAM BOARD

## PHASE 1 — FOUNDATION

### M1 — Integration
- [x] Create project_spec.md
- [ ] Review M3 implementation
- [ ] Define API_CONTRACT.md
- [ ] Define ARCHITECTURE.md
- [ ] Create TEAM_BOARD.md

### M2 — Historical Data
- [x] Verify ten priority location records against the cited sources; document limitations
- [x] Build historical_waterlogging.csv from source-linked workbook rows
- [x] Build historical_waterlogging.json from the same normalized records
- [x] Document source domains, provenance and limitations
- [x] Identify threshold suitability: current records are insufficient for a road-specific threshold
- [x] Add initial FastAPI health-check scaffold

Current data status: 213 location rows across 19 source/date groups; 10 claims are source-verified and 203 remain under review. None supports road-specific threshold derivation.

### M3 — Risk Engine
- [x] Initial risk engine
- [ ] Review architecture
- [ ] Complete unit tests
- [ ] Complete rainfall tracker
- [ ] Document public interface
- [ ] Commit stable version

### M4 — Frontend
- [ ] Build dashboard shell
- [ ] Build mock risk map
- [ ] Build road detail panel
- [ ] Build alert component
- [ ] Define frontend data contract
- [ ] Demonstrate mock flow

---

## PHASE 2 — FIRST INTEGRATION

- [ ] Historical data → risk engine
- [ ] Risk engine → API/JSON
- [ ] API → frontend
- [ ] Real historical records visible on map

---

## PHASE 3 — LIVE RAINFALL

- [ ] Test IMD API
- [ ] Build IMD adapter
- [ ] Normalize rainfall observations
- [ ] Connect to rainfall tracker
- [ ] Live risk update

---

## PHASE 4 — ROUTING

- [ ] Google Maps integration
- [ ] Route calculation
- [ ] Risk-aware route evaluation
- [ ] Alternative route

---

## PHASE 5 — ALERTS

- [ ] Traveller warning
- [ ] Nearby risky-road detection
- [ ] Alert explanation
- [ ] Demo notification

---

## PHASE 6 — VALIDATION

- [ ] Historical replay
- [ ] Threshold validation
- [ ] False-positive analysis
- [ ] False-negative analysis
- [ ] Limitations

---

## PHASE 7 — FINAL

- [ ] AWS deployment
- [ ] UI polish
- [ ] Error states
- [ ] README
- [ ] Architecture diagram
- [ ] Demo dataset
- [ ] 3-minute demo
