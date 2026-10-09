# Data Sources

## Source priorities

For future historical and rainfall data, prefer official records in this order:

1. Delhi PWD and Delhi Irrigation & Flood Control Department
2. DDMA and other government reports
3. IMD station observations and documented academic datasets
4. Reputable reporting as secondary evidence when official incident records are unavailable

OSM road geometry, Google Maps routing, NASA GPM precipitation and SACHET alerts are potential later inputs. They are not currently joined to the historical records.

## Sources represented in the current workbook

The first Kanpur/Gurugram workbook contains 213 source-linked locality rows grouped into 19 city/date/source event groups. The incident rows cite 19 distinct URLs across these publisher domains:

| Publisher | Domain represented in the workbook | Use and current status |
|---|---|---|
| The Times of India | `timesofindia.indiatimes.com` | Kanpur incident/rainfall reports. Four priority claims are directly checked; remaining records need review. |
| Hindustan Times | `www.hindustantimes.com` | Gurugram incident and rainfall reports. URL retained; individual claims remain `REQUIRES_REVIEW`. |
| The Indian Express | `indianexpress.com` | Gurugram incident and rainfall reports. Five priority claims are directly checked; remaining records need review. |
| India Today | `www.indiatoday.in` | Gurugram waterlogging report. One priority claim is directly checked; its workbook duration was unsupported and removed from normalized values. |
| The Daily Pioneer | `www.dailypioneer.com` | Gurugram report PDF. URL retained; rainfall figure overlaps a different report and needs review. |
| The Tribune | `www.tribuneindia.com` | Gurugram rain/waterlogging report. URL retained; individual claims remain `REQUIRES_REVIEW`. |

The separate `Rainfall context` worksheet contains 24 reference rows with 22 distinct URLs across seven domains. It includes city/district/station values and historical context. It is preserved in the raw workbook and is not automatically joined to a road incident unless the incident worksheet already records that contextual amount.

## Source verification status

Ten priority location records are now `VERIFIED` for the event/location claim against the linked article. The direct checks and per-record limitations are documented in [the source verification log](source-verification-log.md). The remaining 203 records stay `REQUIRES_REVIEW`; conflicting measurements still need reconciliation. These checks verify what a secondary news report states, not independent official corroboration. No government PWD, I&FC or DDMA event dataset is currently included in this workbook.

## Planned official sources

| Source | Intended use | Status |
|---|---|---|
| Delhi PWD | Historical road waterlogging and road closures | Research required |
| Delhi Irrigation & Flood Control Department | Drainage and flood context | Research required |
| DDMA / government publications | Incident reports and disaster records | Research required |
| IMD | Rainfall observations and historical station data | Access, spatial/temporal resolution and licensing to be checked |
| OSM | Road geometry | Future; not incident evidence |
| Google Maps | Routing | Future; API access/licence needed |
| NASA GPM | Precipitation cross-check | Optional; not a road-level gauge |
| SACHET | Official alerts | Optional |
