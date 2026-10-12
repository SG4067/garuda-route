# Existing Systems and Problem Gap

## 1. Purpose

This document records weather, drainage, flood-management and navigation systems relevant to Garuda Route. It distinguishes existing services from the capabilities currently implemented in this project and from proposed work.

The project should not claim that no existing solution exists, or that its contribution is unique, without evidence.

## 2. Existing systems and potential data sources

### 2.1 India Meteorological Department (IMD)

**Website:** https://mausam.imd.gov.in/  
**API documentation:** https://api.imd.gov.in/public/api_reference.html

IMD publishes official weather observations, rainfall information, district/station products and weather warnings. These may provide authoritative inputs for a waterlogging-risk workflow, subject to the spatial and temporal scope of the returned data.

**Current Garuda Route status:** the local Node backend contains proxy endpoints for IMD district warnings and rainfall. The browser dashboard can request these endpoints, but the feature must not be described as live unless the team has obtained the required official IMD permission/access, configured the issued credentials on the backend, and verified successful responses. A public API reference is documentation, not proof that the project is authorized or currently connected.

Before live use, validate:
- the access/permission process and applicable use conditions;
- which product and fields are actually available to the project;
- update frequency, timestamp semantics, and district/station coverage;
- whether the measurement is district-, station- or road-specific;
- error handling for missing, stale, rejected or unavailable feeds.

A district warning or station observation is contextual weather information; it is not automatically a measurement at a particular road.

### 2.2 Delhi Irrigation and Flood Control Department

**Website:** https://ifc.delhi.gov.in/  
**Services:** https://ifc.delhi.gov.in/doit-content/our-services

Available material includes drainage maps, drainage plans and flood-control documents. These may help characterize vulnerable areas and drainage context.

**Status:** official documents are identified for research. Road-level coverage, downloadable formats, data quality and reuse conditions still require examination.

### 2.3 Delhi Disaster Management Authority (DDMA)

**Website:** https://ddma.delhi.gov.in/  
**Flood information:** https://ddma.delhi.gov.in/ddma/floods

DDMA information can help establish local flood/waterlogging context and disaster-management responsibilities.

**Status:** official information is identified, but structured historical incident data and a suitable real-time, traveller-facing interface have not been verified for this project.

### 2.4 Delhi Public Works Department (PWD)

**Website:** https://pwddelhi.gov.in/

Potentially relevant material includes road-related complaints, waterlogging records, monsoon-preparedness documents and maintenance information.

**Status:** a candidate source. Downloadable records, location precision, links to rainfall observations and reuse conditions remain to be confirmed.

### 2.5 Mapping and navigation services

Services such as Google Maps Platform provide map display, geocoding and candidate-route calculation, depending on enabled APIs, credentials and terms.

**Current Garuda Route status:** the browser app integrates Google Maps when a usable browser key is provided; the app can fall back to OpenStreetMap when Google Maps cannot load. Google-based geocoding and route calculation depend on the relevant APIs and key restrictions being configured correctly.

The route tab can compare candidate routes against the historical locations and the browser's current historical rainfall-clock heuristic. This is **not** proof of a fully validated road-segment flood-risk routing service. A map provider's route does not itself establish waterlogging risk unless the provider explicitly supplies a suitable hazard feed. Our own evidence and logic remain separate.

OpenStreetMap is a geographic/map fallback, not an official waterlogging incident feed. Its road geometry must not be used as evidence that a road has or has not flooded.

## 3. Current Garuda Route contribution

The current main-branch baseline includes:
- a browser dashboard for historical waterlogging evidence in Kanpur and Gurugram;
- a bundled interface dataset containing 10 event records across 7 locations, distinct from the larger 213-row research workbook;
- an interactive rainfall/value clock that compares entered or selected values with historical amounts/durations when available;
- alert, road/location, history and route panels;
- map display with Google Maps integration and an OpenStreetMap fallback;
- a route-comparison workflow whose risk interpretation is limited by the available historical data;
- a separate FastAPI/M3 risk-engine module with explicit road-to-observation mapping, freshness states and an in-memory observation endpoint for testing.

The historical dashboard's heuristic and M3's threshold comparator are separate mechanisms. The M3 service defaults to a 70% monitor ratio; the browser's historical comparison has its own configured ratio. Neither ratio is a scientifically calibrated flood probability.

The Node IMD proxy is an integration path, not proof of a live feed. IMD data remains unavailable until official access is authorized and configured.

## 4. Conceptual workflow

Authorized rainfall observations
        ↓
Observation validation and freshness checks
        ↓
Continuous-rainfall tracking
        ↓
Evidence-backed road vulnerability and explicit mapping
        ↓
Deterministic risk assessment
        ↓
Risk state with data-quality context
        ↓
Route evaluation and traveller-facing explanation

The browser's historical evidence dashboard provides a separate exploratory workflow. Do not imply the full live pipeline is active simply because a step exists in the architecture or an API route is present.

## 5. Remaining questions and work

- Obtain official IMD access/permission and issued API credentials, then verify the allowed endpoint fields and update behaviour.
- Find historical records that provide verified road-level geometry and co-located rainfall information.
- Establish whether evidence is sufficient for any defensible road-specific rainfall-duration threshold.
- Verify road-to-observation mappings before using M3 assessments for real traveller decisions.
- Communicate unavailable, stale, unknown and unmapped data as such—not as safe conditions.
- Evaluate Google Maps Platform and OpenStreetMap coverage, quotas, terms and attribution requirements.
- Compare existing navigation, municipal alert and disaster-management features without overstating novelty.
- Add validated coverage, freshness, route-result and risk-classification KPIs only when reliable measurements and evaluation methods are available.

## 6. Limitations

Rainfall alone does not determine waterlogging. Drainage, elevation, blockages, runoff, land use and other factors may affect conditions.

A historic report, event-area rainfall value, timer threshold or M3 status is not proof that a specific road is flooded. The historical dataset is mainly secondary reporting, and the current research assessment does not support validated road-specific thresholds or calibrated flood probabilities.

The FastAPI `/api/observations` endpoint is a testing/demo ingestion endpoint that updates process memory; it is not a live rainfall feed or persistent data store. Risk routes return service-unavailable until the M3 adapter is configured. Synthetic example thresholds must not be used as real traveller alerts.

## 7. Conclusion

Garuda Route's current value is an explainable prototype that organizes historical waterlogging evidence, presents it geographically, explores historical rainfall comparisons and demonstrates route comparison. The intended live, evidence-backed risk-routing workflow depends on stronger road-level data, verified mappings, authorized weather access, and further validation.

## 8. Sources

- IMD API Reference: https://api.imd.gov.in/public/api_reference.html
- Delhi Irrigation and Flood Control Department: https://ifc.delhi.gov.in/
- Delhi I&FC Services: https://ifc.delhi.gov.in/doit-content/our-services
- Delhi DDMA Flood Information: https://ddma.delhi.gov.in/ddma/floods
- Delhi PWD: https://pwddelhi.gov.in/
