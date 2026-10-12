# Project KPIs — Definitions and Measurement Plan

This document separates **product KPIs** (how the tool performs) from **evidence-readiness KPIs** (whether the underlying data can support a road-level statement). These metrics are proposed measurement definitions. Do not display a live KPI unless its data source, sampling window, and calculation are implemented and verified.

## 1. Evidence and coverage KPIs

### 1.1 Historical record review coverage

**Formula**

`records directly checked against their cited source / total source-named incident-location rows × 100`

Current documented workbook state: 10 of 213 rows have been directly checked against their cited article, while 203 remain under review (about 4.7% row-review coverage). A direct source check confirms only the scoped event/location claim; it is not independent official corroboration or proof of a road-level rainfall threshold.

**Data needed:** record ID, evidence status, reviewer/check date, source URL, and review outcome.

### 1.2 Road geometry coverage

**Formula**

`eligible road records with reviewed, usable road-segment geometry / all eligible road records × 100`

Do not use a locality pin or geocoder result as verified road geometry. The current normalized workbook does not provide reliable road IDs or coordinates.

### 1.3 Explicit observation-mapping coverage

**Formula**

`eligible roads with reviewed road_id → observation_location_id mappings / eligible roads × 100`

A mapping must be explicit and evidence-backed. Never infer it from equal IDs, a matching road name, or nearest-neighbour distance. The project cannot claim real road-risk coverage until the set of eligible roads is defined.

### 1.4 Threshold evidence coverage

**Formula**

`roads with documented, reviewed threshold evidence / roads proposed for risk evaluation × 100`

Each threshold should retain its basis (`OBSERVED`, `DERIVED`, `ESTIMATED`, or `UNKNOWN`), supporting event IDs, period/scope, and review notes. The current research workbook does not establish a road-specific continuous-rainfall threshold.

## 2. Runtime and product KPIs

### 2.1 Observation freshness rate

**Formula**

`risk assessments whose last observation is within the configured freshness window / assessments with an observation × 100`

Measure over a declared period and report `NO_DATA` and `UNMAPPED` separately. Do not count them as fresh or safe.

### 2.2 Risk API availability and latency

Track:

- request success rate, separated by endpoint and HTTP status;
- p50 and p95 latency for collection and single-road queries;
- number of `503` unconfigured responses;
- counts of `NO_DATA`, `STALE`, `UNMAPPED`, and `UNKNOWN` assessments.

Availability should exclude intentional unconfigured/test states only if the published denominator and exclusion rule are documented.

### 2.3 Route calculation success

**Formula**

`successful route calculations / valid route requests × 100`

Record route provider, request outcome, failure reason, duration, and whether route alternatives were returned. A successful route response is not evidence that the road is not flooded or that the proposed route is safe.

### 2.4 Risk-classification quality

Evaluate precision, recall, and optionally F1 only when an independently reviewed ground-truth/event set, label policy, and evaluation protocol are available. Split records carefully by event/time/location to avoid leaking repeated reports about the same event across evaluation groups. Do not invent accuracy percentages from the current small and incomplete dataset.

## 3. User-facing dashboard KPIs vs engineering KPIs

A future command-centre UI may display current values such as “verified active high-risk assessments,” “route exposure,” “verified road coverage,” and “latest observation age.” These cards should be populated only from verified live assessment data and must show unavailable states for missing/stale/unmapped information.

Engineering KPIs above require logs, counters, and a measurement pipeline; they are not automatically available merely because a unit test passes.

## 4. Reporting template

For any published KPI, document:

- name and formula;
- numerator, denominator, and exclusions;
- source table/API/log;
- location and measurement period;
- timestamp and refresh policy;
- null/error handling;
- responsible maintainer;
- confidence and known limitations.
