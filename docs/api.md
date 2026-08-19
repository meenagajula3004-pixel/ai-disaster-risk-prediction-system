# REST API Reference Documentation

This document describes all API endpoints exposed by the **AI Multi-Disaster Risk Prediction System** backend.

Base URL: `http://localhost:8000`

---

## Endpoints Summary

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Deployment health check & diagnostic status |
| `GET` | `/api/v1/location/search?query=...` | Location search & geocoding autocomplete |
| `GET` | `/api/v1/weather/live?latitude=...&longitude=...` | Retrieve raw live environmental data |
| `POST` | `/api/v1/predict` | Main multi-disaster prediction + SHAP explainability |
| `POST` | `/api/v1/predict/what-if` | What-If climate simulation endpoint |
| `GET` | `/api/v1/history/location?location_name=...` | Fetch prediction trend history for a location |
| `GET` | `/api/v1/admin/stats` | System analytics and model metrics |

---

## Endpoint Details

### 1. `GET /health`
Returns system status.
```json
{
  "status": "healthy",
  "service": "AI Multi-Disaster Risk Prediction & Early Warning System",
  "timestamp": "2026-08-19T10:00:00.000Z",
  "database": "connected",
  "ml_models": "loaded"
}
```

### 2. `POST /api/v1/predict`
Main multi-hazard risk prediction request.

**Request Payload:**
```json
{
  "latitude": 16.5449,
  "longitude": 81.5212,
  "location_name": "Bhimavaram, Andhra Pradesh"
}
```

**Response Payload:**
```json
{
  "id": 1,
  "location_name": "Bhimavaram, Andhra Pradesh",
  "latitude": 16.5449,
  "longitude": 81.5212,
  "primary_risk": {
    "primary_hazard": "Flood Risk",
    "risk_level": "HIGH",
    "risk_percentage": 78.5,
    "warning_advice": "⚠️ HIGH FLOOD RISK WARNING. Prepare precautionary safety measures."
  },
  "environmental_data": {
    "temperature": 28.5,
    "humidity": 82.0,
    "surface_pressure": 1008.0,
    "wind_speed": 18.0,
    "rainfall_24h": 68.5,
    "rainfall_7d": 195.0,
    "elevation": 12.0,
    "status": "Live data retrieved from Open-Meteo API"
  },
  "disaster_risks": {
    "flood": {
      "disaster_type": "Flood Risk",
      "risk_percentage": 78.5,
      "risk_level": "HIGH",
      "validation_status": "Validated",
      "top_factors": [...]
    },
    "landslide": { ... },
    "cyclone": { ... },
    "heatwave": { ... },
    "drought": { ... }
  },
  "timestamp": "2026-08-19T10:00:00.000Z",
  "disclaimer": "This application provides AI-based multi-disaster risk estimation for educational and decision-support purposes...",
  "is_simulation": false
}
```
