# Data Sources

## Purpose and source priorities

Garuda Route combines historical waterlogging evidence, map/routing services, and—once authorized—current weather observations. These inputs have different meanings and must not be presented as interchangeable.

For historical incidents and rainfall evidence, prefer sources in this order:

1. Official road, drainage, disaster-management and government incident records.
2. IMD station observations and documented academic datasets, subject to access and reuse conditions.
3. Reputable reporting as secondary evidence when official incident records are unavailable.

OSM road geometry, Google Maps routing, NASA GPM precipitation and SACHET alerts can provide useful context, but they are not automatically road-level waterlogging observations.

## Historical research workbook

The broader Kanpur/Gurugram research workbook contains 213 source-linked locality rows grouped into 19 city/date/source event groups. It also contains a separate rainfall-context sheet and a priority-location sheet. These are research records, not 213 verified road segments.

The incident rows cite 19 distinct URLs across these publisher domains:

| Publisher | Domain represented in the workbook | Use and current status |
|---|---|---|
| The Times of India | `timesofindia.indiatimes.com` | Kanpur incident/rainfall reports. Four priority claims are directly checked; remaining records need review. |
| Hindustan Times | `www.hindustantimes.com` | Gurugram incident and rainfall reports. URLs retained; individual claims remain `REQUIRES_REVIEW`. |
| The Indian Express | `indianexpress.com` | Gurugram incident/rainfall reports. Five priority claims are directly checked; remaining records need review. |
| India Today | `www.indiatoday.in` | Gurugram waterlogging report. One priority claim is directly checked; an unsupported duration was removed from normalized values. |
| The Daily Pioneer | `www.dailypioneer.com` | Gurugram report PDF. URL retained; a rainfall figure overlaps another report and needs review. |
| The Tribune | `www.tribuneindia.com` | Gurugram rain/waterlogging report. URLs retained; individual claims need review. |

The separate `Rainfall context` worksheet contains 24 reference rows with 22 distinct URLs across seven domains. It includes city-, district- and station-level measurements. It is not automatically joined to a road incident as if it were a measurement at that road.

## Verification status and limits

Ten priority-location records are `VERIFIED` for the reported event/location claim against their linked articles. The remaining 203 records are `REQUIRES_REVIEW`. These checks establish what the cited secondary report states; they are not independent confirmation from an official incident register or road sensor.

The current dataset does **not** support validated, road-specific rainfall-duration thresholds. A location name, city-level rainfall total, approximate event duration or report of standing water must not be converted into a verified road-level trigger. See [the source verification log](source-verification-log.md) and [the historical-data methodology](historical-data-methodology.md).

## Sources used or integrated by the application

| Source/service | Intended role | Current state |
|---|---|---|
| Historical reporting workbook | Historical waterlogging-event evidence and contextual rainfall notes | Research dataset; 10 priority claims checked, 203 still need review. |
| Dashboard historical export (`frontend/data/road-waterlogging-records.json`) | Powers the local historical-evidence interface | Bundled export currently contains 10 event records across 7 locations. It is a separate, smaller interface dataset, not the full 213-row workbook. |
| India Meteorological Department (IMD) | Official district warning/rainfall context for the local dashboard, and a candidate source for authorized weather observations | The Node backend has proxy routes for warning and rainfall endpoints. Live API use is gated on obtaining official IMD permission/access and configuring issued credentials. The presence of a public API reference does not by itself mean access has been authorized. Until access is approved and a successful request is verified, display IMD as unavailable/not connected—not as live. |
| Google Maps Platform | Map display, geocoding and alternative-route calculation | Integrated when a valid, appropriately restricted browser key is configured. Maps may fall back to OpenStreetMap if Google Maps cannot load. Routing/geocoding capabilities depend on key/API configuration and provider terms. |
| OpenStreetMap (OSM) | Fallback map tiles and geographic context | Fallback map source; not incident evidence and not a live waterlogging feed. |
| M3 `WaterloggingRiskService` / FastAPI API | Deterministic risk-engine service for explicitly configured road/location mappings | Separate local service. The FastAPI routes return 503 until configured with an evidence-backed road dataset. Do not treat synthetic example thresholds as live traveller alerts. |
| NASA GPM precipitation | Possible regional precipitation cross-check | Not currently joined to the historical records; a gridded product is not a road-level gauge. |
| SACHET alerts | Possible official alert context | Potential future integration; not currently connected. |
| Delhi PWD, Delhi Irrigation & Flood Control Department and DDMA | Historical road, drainage and flood-event evidence | Official sources identified for further research; structured, reusable records have not yet been confirmed for this dataset. |

## IMD access requirements

The project intends to use official IMD data; this is not a decision to make the weather feature optional. However, a live integration must not be represented as operational until the team has obtained the required official permission/access, received the appropriate credentials, configured the backend, and successfully verified the permitted endpoints and fields.

Keep credentials on the backend in environment variables. Do not commit issued secrets or place them in frontend source, screenshots, README files or public logs. Follow the access conditions and permitted-use terms supplied by IMD.

## Sources to investigate next

| Source | Intended use | Next step |
|---|---|---|
| Delhi PWD | Historical road waterlogging, road closures and maintenance records | Identify structured records and confirm permission to reuse. |
| Delhi Irrigation & Flood Control Department | Drainage and flood context | Review available maps, reports and spatial detail. |
| DDMA / government publications | Incident reports and disaster records | Check whether downloadable, location-specific records exist. |
| IMD | Authorized warnings and rainfall observations | Obtain official access/permission and credentials; verify fields, update interval, station/district scope and licence. |
| OSM | Road geometry | Use as geographic context where suitable; do not treat it as incident evidence. |
| Google Maps Platform | Geocoding and candidate routes | Configure a restricted key and validate API enablement, quotas and terms. |
| NASA GPM | Precipitation cross-check | Assess spatial/temporal resolution and reuse terms before integrating. |
| SACHET | Official alerts | Assess a documented interface and permitted use before integrating. |
