# Historical source verification log

Checked on **2026-10-09** by opening the source URLs already cited in the
workbook. This first audit covers ten priority-location records across Kanpur
and Gurugram. VERIFIED means the cited article supports the reported event
and named area/road. It does not mean the newspaper claim was independently
corroborated by a government incident register or a road sensor.

| Record ID | Event / location | What the cited source confirms | Rainfall / duration and limits |
|---|---|---|---|
| HIST-LOC-0036 | Kanpur, 2019-09-27, Chunniganj | The Times of India reports water accumulation near Chunniganj and traffic disruption on the Narhona Crossing–Mall Road to Chunniganj stretch. | 89.4 mm is reported from the CSA University city rain gauge at 3 pm. It is not a Chunniganj road measurement. No continuous rainfall duration or road-specific depth. [Article](https://timesofindia.indiatimes.com/city/kanpur/city-receives-heaviest-rainfall-of-season-more-showers-predicted/articleshow/71343589.cms) |
| HIST-LOC-0070 | Kanpur, 2025-07-12, Govind Nagar | The Times of India names Govind Nagar among the places affected by waterlogging. | 35 mm is the city total for the preceding 24 hours. Intermittent rain began Friday evening; heavier rain continued into Saturday morning, but the article does not establish a continuous duration at Govind Nagar. [Article](https://timesofindia.indiatimes.com/city/kanpur/kanpur-roads-flooded-after-heavy-downpour/articleshow/122409642.cms) |
| HIST-LOC-0073 | Kanpur, 2025-07-12, P Road | The same report names P Road among the places affected by waterlogging. | Same city-level 35 mm / 24-hour context as above; no road-specific rainfall, duration or depth. [Article](https://timesofindia.indiatimes.com/city/kanpur/kanpur-roads-flooded-after-heavy-downpour/articleshow/122409642.cms) |
| HIST-LOC-0077 | Kanpur, 2025-07-12, Gwaltoli | The same report names Gwaltoli among the places affected by waterlogging. | Same city-level 35 mm / 24-hour context as above; no road-specific rainfall, duration or depth. [Article](https://timesofindia.indiatimes.com/city/kanpur/kanpur-roads-flooded-after-heavy-downpour/articleshow/122409642.cms) |
| HIST-LOC-0116 | Gurugram, 2018-08-28, Hero Honda Chowk underpass | The Indian Express reports the underpass was closed after waterlogging and remained submerged through Wednesday, more than 24 hours later. | The report associates inundation with 128 mm of rainfall. It does not provide a continuous rainfall duration or a gauge measurement at the underpass. The >24 hours is submergence duration, not rainfall duration. [Article](https://indianexpress.com/article/cities/delhi/gurgaon-hero-honda-chowk-underpass-opened-still-submerged-delhi-rains-5331735/) |
| HIST-LOC-0123 | Gurugram, 2022-05-23, Rajiv Chowk | India Today names Rajeev Chowk among areas affected by waterlogging and describes traffic disruption. The workbook uses the spelling “Rajiv.” | The cited article states neither rainfall amount nor rainfall duration. The workbook's “about 2 hours” duration was not supported by this article; normalized duration is now null for all 14 location rows tied to this article. Original workbook wording remains in source_duration_raw. [Article](https://www.indiatoday.in/cities/gurugram/story/gurugram-news-traffic-jam-heavy-downpour-waterlogging-1953011-2022-05-23) |
| HIST-LOC-0131 | Gurugram, 2022-08-07, Golf Course Road | The Indian Express names waterlogging on Golf Course Road. A GMDA official says stormwater released from a society added to waterlogging on that stretch. | The article reports a rain spell of over two hours and 19 mm for Gurgaon by 5 pm. The 19 mm is city/event context. Knee-high water is reported for some low-lying points, not specifically this road. [Article](https://indianexpress.com/article/cities/delhi/gurgaon-rain-waterlogging-several-areas-8076161/) |
| HIST-LOC-0150 | Gurugram, 2022-08-07, Sheetla Mata Road | The Indian Express lists Sheetla Mata Road among locations with reported waterlogging. | Same over-two-hour rain-spell and city/event 19 mm context. No road-specific rainfall or depth. [Article](https://indianexpress.com/article/cities/delhi/gurgaon-rain-waterlogging-several-areas-8076161/) |
| HIST-LOC-0155 | Gurugram, 2023-07-04, Rajiv Chowk | The Indian Express names Rajeev Chowk among waterlogged stretches/areas. | The city received 65 mm by 4:30 pm. The article says heavy rain occurred in a short span but gives no exact duration; city total is not road-specific. Knee-deep water applied only to some unnamed places. [Article](https://indianexpress.com/article/cities/delhi/gurgaon-heavy-rain-waterlogging-gmda-8752362/) |
| HIST-LOC-0161 | Gurugram, 2023-07-04, Hero Honda Chowk | The same report, including a GMDA statement, names Hero Honda Chowk among the areas with waterlogging. | Same city-level 65 mm by 4:30 pm context. No exact rainfall duration or road-specific measurement. [Article](https://indianexpress.com/article/cities/delhi/gurgaon-heavy-rain-waterlogging-gmda-8752362/) |

## Correction and interpretation

The direct check of the 2022-05-23 India Today article found no rainfall
duration. The workbook had repeated “About 2 hours (area-wide report)” across
14 location rows for that article. Those numeric normalized durations are now
null, the qualifier is UNKNOWN, and the original supplied wording is
preserved in source_duration_raw. The records remain in the dataset.

These ten records verify reported historical waterlogging in the named
locations. They do not establish rainfall-duration thresholds. Rainfall values
are city/gauge context; except for the named underpass, most locations are
areas or roads without exact segment geometry. The three Kanpur 2025 place
names are reported affected areas, not precise road-segment observations.
Severity remains source/event context unless the source identifies a specific
depth at the specific location.

All other workbook rows remain REQUIRES_REVIEW. The sources above are
secondary journalism; further corroboration from official records is still
desirable. No record is suitable for threshold derivation.
