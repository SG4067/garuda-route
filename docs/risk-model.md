# Risk Model

## Current Model

The current system uses deterministic rule-based comparison.

It is NOT a machine-learning model.

## Inputs

- continuous rainfall duration
- historical road threshold
- historical severity
- rainfall state
- data freshness

## Risk Levels

### NORMAL

Current rainfall conditions are sufficiently below the historical
waterlogging indicator.

### MONITOR

Current rainfall conditions are approaching the historical indicator.

### HIGH_RISK

Current rainfall conditions have reached or exceeded the historical
indicator.

## Important Scientific Limitation

The risk level is an empirical indicator.

It does not mean that flooding is guaranteed.

## Monitor Threshold

The current monitor ratio is configurable.

Default implementation currently uses a 70% early-warning ratio.

This is a provisional engineering heuristic and must not be presented
as scientifically validated.
