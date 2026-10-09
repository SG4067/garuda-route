# Backend risk API proposal — pending M1 agreement

**Status:** proposal only. This is not the finalized API contract. M1 should
confirm the collection response shape, error behavior, and unmapped-road
semantics before backend risk routes are finalized.

## Scope

The backend will be an HTTP adapter around M3's WaterloggingRiskService. It
will not calculate risk independently. M3 currently provides in-memory
observation tracking; a live rainfall feed and persistent storage are outside
this API proposal.

M3 code was found on the configured remote's backend branch. The named
feature/m3-risk-service branch was not advertised by the remote when checked
on 2026-10-09. Confirm the intended integration ref before adding or vendoring
the package into this branch.

## Proposed routes

### GET /api/roads/risk?as_of=<ISO-8601>

Call get_all_roads_risk(as_of=...) and return its array of road assessments
unchanged. A plain array matches M3's current return type. M1 may instead
request an object envelope such as { "roads": [...], "count": 0 }; that
choice should be made once with the frontend consumer.

### GET /api/roads/{road_id}/risk?as_of=<ISO-8601>

Call get_road_risk(road_id, as_of=...) and return its assessment object
unchanged. Unknown road IDs should map to HTTP 404. A timestamp, when supplied,
must be ISO-8601 and include a timezone.

### POST /api/observations

Optional for the initial integration. If exposed, accept the M3 rainfall
observation fields (location_id, timestamp,
rainfall_intensity_mm_hr, optional is_raining, and optional provenance or
coordinates) and return the service ingestion receipt unchanged. This endpoint
would update process memory only; it would not imply a live data feed or
persistence.

## Per-road assessment shape

Keep M3 field names and enums rather than introducing a second risk model:

    {
      "status": "success",
      "road_id": "ROAD-001",
      "road_name": "Example Road",
      "location_id": "RAIN-GAUGE-01",
      "current_duration_minutes": 45.0,
      "historical_threshold_minutes": null,
      "risk_level": "UNKNOWN",
      "severity": "HIGH",
      "is_raining": true,
      "data_freshness": "FRESH",
      "last_observation_timestamp": "2026-10-09T10:30:00+00:00",
      "reason": "Historical waterlogging threshold is not yet determined.",
      "evaluated_at": "2026-10-09T10:30:00+00:00"
    }

The values above are illustrative only. In particular, no threshold is being
proposed for a real road.

## Semantics the API must preserve

| M3 condition | Required client interpretation |
|---|---|
| risk_level=UNKNOWN, data_freshness=NO_DATA | No observation is available. Never render as NORMAL or safe. |
| risk_level=UNKNOWN, data_freshness=UNMAPPED | No explicit road-to-location mapping exists. Never render as NORMAL or safe. |
| data_freshness=STALE | Assessment uses last known state and is stale; show the stale warning. |
| threshold_unavailable / risk_level=UNKNOWN | No supported road threshold exists; do not compare against a guessed value. |
| NORMAL, MONITOR, HIGH_RISK | Display only when the service returns that risk level. |

M3 currently emits current_duration_minutes=0.0 and is_raining=false for
NO_DATA; clients must treat status and data_freshness as authoritative,
not infer that the road is dry from these fallback values. Prefer nulls for
unobserved values if M3 chooses to adjust its output contract.

## M3 integration issue to resolve

RoadRecord.threshold_minutes permits null. In the current service on
origin/backend, the no-observation and unmapped response paths call
round(road.threshold_minutes, 1). The mapped-observation success path also
rounds assessment.historical_threshold_minutes. These raise TypeError when
the threshold is null, even though RiskEngine.evaluate_risk represents an
unavailable threshold as UNKNOWN. M3 should preserve null thresholds in all
service responses and add tests for these cases before backend integration.

The single-road unmapped path currently raises RoadMappingNotFoundError,
while the all-roads path returns an UNKNOWN/UNMAPPED assessment. Prefer
consistent facade behavior before the API is finalized, or M1 must explicitly
choose HTTP and body behavior for this discrepancy.

## Decisions for M1

1. Should the collection endpoint return M3's raw array or an object envelope?
2. Should POST /api/observations be included now, given it is in-memory only?
3. What HTTP status and error body should unknown roads, invalid as_of, and
   missing road mappings use?
4. Should single-road missing mappings return an UNKNOWN/UNMAPPED object,
   matching collection results?
5. Can M1 confirm the intended branch/ref for integrating M3's package?
