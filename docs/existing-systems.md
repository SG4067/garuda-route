# Existing Systems and Problem Gap

## 1. Purpose

This document records existing weather, drainage, flood-management and road-navigation systems relevant to our project.

The objective is to understand what already exists, identify useful data sources, and establish what our proposed system could add.

We must not claim that no existing solution exists without evidence.

## 2. Existing Systems

### 2.1 India Meteorological Department (IMD)

**Website:** https://mausam.imd.gov.in/

**API documentation:** https://api.imd.gov.in/public/api_reference.html

**What it provides:**
- Current weather observations
- District-wise and station-wise nowcasts
- Rainfall information
- District-level weather warnings
- Weather forecasts

**Relevance to our project:**

IMD may provide rainfall observations and warning information that can be used as inputs to our risk assessment system.

**Limitations to investigate:**
- Which API provides the most useful rainfall information for our selected area?
- How frequently are relevant observations updated?
- Does the returned data include a numerical rainfall intensity?
- How closely does the observation represent an individual road?

**Status:** Official source identified; specific endpoints and data quality still need testing.

### 2.2 Delhi Irrigation and Flood Control Department

**Website:** https://ifc.delhi.gov.in/

**Services:** https://ifc.delhi.gov.in/doit-content/our-services

**Available material includes:**
- Delhi Drainage Map
- Drainage Master Plan
- Flood-control documents

**Relevance to our project:**

These resources may help us understand drainage infrastructure, vulnerable areas and the physical context of documented waterlogging locations.

**Limitations to investigate:**
- Can we identify individual roads from the available documents?
- Are waterlogging locations explicitly listed?
- Are event dates, rainfall durations and severity recorded?
- Can the information be downloaded and reused under the applicable terms?

**Status:** Official documents identified; road-level coverage and usability require examination.

### 2.3 Delhi Disaster Management Authority (DDMA)

**Website:** https://ddma.delhi.gov.in/

**Flood information:** https://ddma.delhi.gov.in/ddma/floods

**What it provides:**

DDMA publishes information about flooding in Delhi, including river flooding, local flash flooding and waterlogging in low-lying areas.

**Relevance to our project:**

Its information can help establish the local problem, identify vulnerable-area characteristics and understand existing disaster-management responsibilities.

**Limitations to investigate:**
- Are downloadable historical incident records available?
- Do records identify individual road segments?
- Are rainfall observations linked to individual incidents?
- Are real-time, traveller-facing road alerts available through a documented interface?

**Status:** Official information identified; availability of structured data and relevant interfaces remains unverified.

### 2.4 Delhi Public Works Department (PWD)

**Website:** https://pwddelhi.gov.in/

**Potentially relevant material:**
- Waterlogging-related records and complaints
- Flood-control and monsoon-preparedness documents
- Road and drainage maintenance information

**Relevance to our project:**

PWD material is a potential source of historical waterlogging locations and road-related evidence.

**Limitations to investigate:**
- Whether records are downloadable or accessible through an API
- Whether location details are precise enough to map
- Whether rainfall conditions are linked to reported events
- Whether the source permits reuse

**Status:** Research required; usable records have not yet been confirmed.

### 2.5 Existing Mapping and Navigation Services

Examples include Google Maps and other navigation providers.

**What they generally help with:**
- Displaying maps
- Searching for places
- Calculating routes
- Providing travel-time estimates, with capabilities depending on the provider and API

**Relevance to our project:**

A navigation provider can supply candidate routes. Our system can then evaluate those routes against its own waterlogging-risk information.

**Important limitation:**

A normal navigation route calculation does not automatically establish whether a road is waterlogged according to our historical rainfall thresholds. That assessment must come from our own risk data and logic, unless a provider explicitly supplies a suitable hazard feature.

**Status:** Potential routing integration; provider, API access and terms to be confirmed.

## 3. What Is Our Proposed Contribution?

Our project proposes to connect four kinds of information:

1. Current rainfall observations
2. Historical road-waterlogging evidence
3. Road/location information
4. A transparent risk-assessment method

The system would compare current rainfall conditions with the historical vulnerability information available for a road or location.

It would then display a risk state, explain the evidence behind the warning, and help travellers consider an alternative route.

## 4. Proposed Workflow

Rainfall observations
        ↓
Rainfall-duration tracking
        ↓
Historical road vulnerability
        ↓
Risk assessment
        ↓
Road warning
        ↓
Route evaluation
        ↓
Traveller recommendation

## 5. Research Questions We Still Need to Answer

- Which live rainfall source works reliably for our pilot area?
- Which historical records contain usable road-level information?
- Do any records connect rainfall duration or intensity to waterlogging?
- How many records are sufficient to support a defensible threshold?
- How will a weather observation be associated with nearby roads?
- How will we communicate missing data and uncertainty?
- What existing road-alert or routing features could overlap with our proposal?
- Which datasets and APIs permit our intended use?

## 6. Important Limitations

We must not assume that a road will flood merely because a rainfall-duration threshold has been reached.

Waterlogging can also depend on drainage conditions, road elevation, runoff, blockages and other factors.

A historical threshold is an empirical indicator, not a guarantee of flooding.

We must not claim that our project replaces government flood-management infrastructure or that it is unique until the relevant comparisons have been completed.

## 7. Current Conclusion

The initial research establishes that relevant weather, drainage and disaster-management systems already exist.

The potential contribution of our project is to connect available rainfall observations with documented road-level waterlogging vulnerability, and to turn that relationship into an explainable warning and route-diversion workflow.

This contribution remains a hypothesis to validate through further research and testing.

## 8. Sources

- IMD API Reference: https://api.imd.gov.in/public/api_reference.html
- Delhi Irrigation and Flood Control Department: https://ifc.delhi.gov.in/
- Delhi I&FC Services: https://ifc.delhi.gov.in/doit-content/our-services
- Delhi DDMA Flood Information: https://ddma.delhi.gov.in/ddma/floods
- Delhi PWD: https://pwddelhi.gov.in/

