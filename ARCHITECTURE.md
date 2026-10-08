# System Architecture

## 1. Overview

The system detects when current rainfall conditions approach or exceed
historically observed waterlogging conditions for specific roads.

## 2. Core Pipeline

Rainfall Observation
        ↓
Continuous Rainfall Tracker
        ↓
Historical Road Vulnerability
        ↓
Threshold Comparison
        ↓
Waterlogging Risk
        ↓
Backend API
        ↓
Traveller Alert
        ↓
Route Diversion

## 3. Current Components

### Rainfall Input
Receives normalized rainfall observations.

### Rainfall Tracker
Determines continuous rainfall duration.

### Historical Vulnerability
Stores road-specific historical waterlogging information.

### Risk Engine
Compares current rainfall conditions against historical indicators.

### Backend
Will expose the risk system to clients.

### Frontend
Currently ON HOLD.

### Routing
Planned later using a mapping/routing provider.

## 4. Current Phase

Foundation / Data Collection / Risk Engine Stabilization

## 5. Future Components

- Live IMD integration
- Backend API
- Map
- Route calculation
- Traveller alerts
- AWS deployment
