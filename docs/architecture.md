# System Architecture & Component Design

This document details the multi-tiered architecture of the **AI Multi-Disaster Risk Prediction & Early Warning System**.

---

## High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  REACT FRONTEND                                   |
|   (Vite + React 18 + Tailwind CSS + Leaflet Maps + Recharts + Lucide Icons)       |
+-----------------------------------------------------------------------------------+
                                         │  HTTP / REST (Axios API Client)
                                         ▼
+-----------------------------------------------------------------------------------+
|                                  FASTAPI BACKEND                                  |
|  +---------------------+   +---------------------+   +-------------------------+  |
|  | Weather Service     |   | Multi-Hazard ML     |   | SHAP Explainability     |  |
|  | (Open-Meteo API)    |   | Inference Engine    |   | Attribution Engine      |  |
|  +---------------------+   +---------------------+   +-------------------------+  |
+-----------------------------------------------------------------------------------+
         │                                 │                             │
         ▼                                 ▼                             ▼
+-------------------+             +------------------+         +--------------------+
| External APIs     |             | ML Model Binaries|         | Database           |
| • Open-Meteo      |             | • best_models    |         | • PostgreSQL       |
| • Elevation API   |             | • scaler.joblib  |         | • SQLite Fallback  |
+-------------------+             +------------------+         +--------------------+
```

---

## Core Components

### 1. React Frontend (`frontend/`)
- Single-Page Dashboard built with React 18 and Vite.
- Responsive Tailwind CSS styling with custom glassmorphism design system tokens.
- Interactive spatial maps powered by Leaflet + OpenStreetMap.
- Real-time chart visualizers powered by Recharts.
- Components: `LocationSearch`, `PrimaryRiskBanner`, `EnvironmentalMetricsGrid`, `DisasterRiskCards`, `RiskMap`, `SHAPExplainerWidget`, `WhatIfSimulator`, `AdminDashboard`, `ModelInfoModal`.

### 2. FastAPI Backend (`backend/`)
- Asynchronous Python REST API service exposing endpoint routes for geocoding, live weather, multi-disaster prediction, what-if simulations, historical logs, and admin statistics.
- Pre-loads trained ML models (`best_models.joblib`) and StandardScaler (`scaler.joblib`) during startup lifespan.

### 3. Machine Learning & SHAP Engine (`ml/`)
- Dedicated classifier models evaluating 5 natural hazard categories (Flood, Landslide, Cyclone, Heatwave, Drought).
- Trained using time-aware chronological cross-validation.
- SHAP TreeExplainer calculates directional feature importance scores per request.

### 4. Data Layer & Persistence (`database/`, PostgreSQL)
- Stores location observations, prediction history records, and system logs.
- Native PostgreSQL integration with explicit `USE_SQLITE_FALLBACK=true` option for lightweight standalone execution.
