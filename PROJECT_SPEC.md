---------------------
# GarudaRoute
---------------------

# Real-Time Road Waterlogging Alert and Route Diversion System

## Problem

During continuous rainfall, certain roads are historically more prone to
waterlogging. Travellers may not receive sufficiently localized warnings
before reaching these areas.

## Core Idea

Compare current rainfall conditions with historical rainfall-waterlogging
relationships for individual roads/locations.

## MVP

1. Obtain current rainfall information.
2. Track continuous rainfall duration.
3. Store historical road vulnerability.
4. Compare current conditions with historical thresholds.
5. Mark roads as NORMAL, MONITOR, or HIGH RISK.
6. Display risky roads on a map.
7. Alert nearby travellers.
8. Suggest an alternative route.

## Non-Goals

- Nationwide flood prediction
- Physical drainage monitoring
- Satellite-based flood detection
- Fully autonomous traffic control
- Claiming scientifically calibrated flood probability

## Core Pipeline

Rainfall
→ Rain Duration
→ Historical Road Vulnerability
→ Risk Assessment
→ Road Alert
→ Route Diversion
