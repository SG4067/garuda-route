# Risk Model and Interpretation

## 1. Two separate classifications

Garuda Route currently has two similar-looking but separate classification paths:

1. **Browser historical reference heuristic:** compares the user's rainfall/reference clock against values reported by the curated historical event dataset. The monitor level is currently 75% of the reference value and the high level is 100%. These amounts may describe a city or district and can be qualitative/incomplete.
2. **M3 engine:** tracks timestamped rainfall observations per observation location and compares continuous-rainfall duration against a configured historical threshold. Default monitor ratio is 70%; high risk begins at 100% of that threshold.

These systems must not be merged conceptually or presented with the same evidence basis. Neither is a physically based hydraulic model or calibrated probability of flooding.

## 2. M3 calculation

For a configured road with a non-null, evidence-supported duration threshold:

`monitor_threshold_minutes = historical_threshold_minutes × monitor_ratio`

With the default `monitor_ratio = 0.70`:

- `NORMAL`: current continuous rainfall duration is below the monitor threshold.
- `MONITOR`: duration is at or above the monitor threshold but below the historical threshold.
- `HIGH_RISK`: duration is at or above the historical threshold.
- `UNKNOWN`: there is insufficient mapping, data, or threshold information to assign a valid class.

These labels are engineering indicators relative to the configured threshold. They do not mean rain alone caused waterlogging, and they do not represent a calibrated flood probability.

## 3. Data freshness and state

The service distinguishes rainfall state from observation freshness:

- `FRESH`: last observation is within the configured freshness limit.
- `STALE`: last observation is too old to call current, but the last-known duration is preserved with a stale explanation.
- `NO_DATA`: no usable observation is available.
- `UNMAPPED`: the road has no explicit mapping to an observation location.

A missing observation is not proof that rain stopped. `is_raining: false` or duration `0` in a no-data output must not be used to claim normal/safe conditions. A null threshold must remain null; no arbitrary threshold may be substituted.

## 4. Required inputs and evidence

The M3 result depends on:

- a configured road record;
- an explicit `road_id -> location_id` mapping;
- timestamped observations at the mapped observation location;
- threshold value and evidence/derivation appropriate to the road;
- freshness and observation-gap policy.

The current normalized research workbook does not establish road-specific continuous-rainfall thresholds. Root `data/roads.json` is synthetic and should be used for development/tests only. The observation POST endpoint accepts manual/demo input in memory; it is not a live provider feed.

## 5. Model limitations

Neither classification accounts for all factors that determine waterlogging, such as drainage capacity and blockage, local elevation, surface condition, runoff, local rainfall variation, pump operation, and flood-control infrastructure. Historical reporting may be biased toward well-known roads and severe events. The dashboard's curated record count is small, and many rows in the research workbook remain under review.

## 6. Evaluation KPIs

Potential metrics: evidence coverage, explicit road-mapping coverage, observation freshness, risk API latency, route calculation success, and precision/recall against an independent and reviewed set of events. Do not publish a numeric model-accuracy score without a defined label policy, evaluation sample, split, and reproducible calculation.
