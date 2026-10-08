# API Contract

## Purpose

This document defines the interface between the risk engine and future
backend/frontend components.

## 1. Rainfall Observation

### Input

```json
{
  "location_id": "IMD_DEL_LODHI",
  "timestamp": "2026-10-09T10:30:00Z",
  "rainfall_intensity_mm_hr": 25.5,
  "is_raining": true,
  "latitude": 28.5892,
  "longitude": 77.2215,
  "source": "IMD_API"
}
