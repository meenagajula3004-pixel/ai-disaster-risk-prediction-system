# Real-World Data Sources & Dataset Provenance (Version 3.1)

This document provides complete metadata and scientific provenance for the real-world historical dataset and model architecture used in Version 3.1 of the **AI Multi-Disaster Risk Prediction & Early Warning System**.

---

## 1. Dataset Overview

* **Dataset Name**: Authoritative Real-World Historical Multi-Hazard Dataset (V3.1)
* **Storage Location**: [`data/raw/v31_authoritative_historical_dataset.csv`](file:///C:/Users/VARSHITA/.gemini/antigravity/scratch/ai-disaster-risk-prediction-system/data/raw/v31_authoritative_historical_dataset.csv)
* **Metadata Location**: [`data/raw/v31_dataset_provenance_metadata.json`](file:///C:/Users/VARSHITA/.gemini/antigravity/scratch/ai-disaster-risk-prediction-system/data/raw/v31_dataset_provenance_metadata.json)
* **Total Validated Samples**: 1,200 historical observation records
* **Independent Disaster Events**: 49 events (34 Train / 7 Validation / 8 Test events)
* **Time Horizon**: 2005-07-19 to 2024-08-11
* **Feature Count**: 17 input features (added 12h Wind & Pressure tendency deltas)
* **Target Count**: 5 disaster hazard classification targets

---

## 2. Authoritative Real-World Data Sources

### A. NOAA IBTrACS Tropical Cyclone Database
* **Organization**: NOAA NCEI / World Meteorological Organization (WMO)
* **Source URL**: [https://www.ncei.noaa.gov/products/international-best-track-archive](https://www.ncei.noaa.gov/products/international-best-track-archive)
* **License**: Public Domain (US NOAA)
* **Usage**: Sourced track positions, wind speeds, and pressure telemetry across 24 major tropical cyclones (Fani, Hudhud, Amphan, Tauktae, Yaas, Vardah, Gaja, Biparjoy, Katrina, Sandy, Harvey, Irma, Ian, Haiyan, Hagibis, Doksuri, etc.).

### B. NASA Global Landslide Catalog (GLC)
* **Organization**: NASA Goddard Space Flight Center
* **Source URL**: [https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog/h9d8-gfdw](https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog/h9d8-gfdw)
* **License**: Public Domain (US Government Work)
* **Usage**: Provides verified historical landslide event coordinates (`latitude`, `longitude`), onset dates, and severity ratings (Pettimudi, Chooralmala Wayanad, Kedarnath, Malin Pune, Shimla, Manipur, Atami Japan).

### C. Copernicus ERA5 Reanalysis via Open-Meteo Archive API
* **Organization**: European Centre for Medium-Range Weather Forecasts (ECMWF) / Copernicus Climate Change Service
* **Source URL**: [https://archive-api.open-meteo.com/v1/archive](https://archive-api.open-meteo.com/v1/archive)
* **License**: Creative Commons Attribution 4.0 International (CC-BY 4.0)
* **Usage**: Sourced historical temperature, precipitation, humidity, pressure, and wind speed telemetry for all 1,200 observation points.

---

## 3. 17-Feature Architecture & Model Selections

### Input Feature Matrix (17 Parameters)
1. `temperature`: Ambient surface air temperature (°C)
2. `humidity`: Relative atmospheric humidity (%)
3. `surface_pressure`: Barometric surface pressure (hPa)
4. `wind_speed`: 10-meter wind velocity (km/h)
5. `elevation`: Height above sea level (meters)
6. `slope_degree`: Terrain incline angle (0° to 50°)
7. `rainfall_1h`: Past 1-hour precipitation (mm)
8. `rainfall_3h`: Past 3-hour cumulative precipitation (mm)
9. `rainfall_6h`: Past 6-hour cumulative precipitation (mm)
10. `rainfall_12h`: Past 12-hour cumulative precipitation (mm)
11. `rainfall_24h`: Past 24-hour cumulative precipitation (mm)
12. `rainfall_3d`: Past 3-day cumulative precipitation (mm)
13. `rainfall_7d`: Past 7-day cumulative precipitation (mm)
14. `soil_moisture`: Volumetric soil moisture index (0.05 to 0.95)
15. `hot_days_streak`: Consecutive days with temperature > 35°C
16. `delta_wind_12h`: 12-hour wind speed tendency delta (km/h)
17. `delta_pressure_12h`: 12-hour surface pressure tendency delta (hPa)

### Model Selections per Hazard
* **Flood**: Gradient Boosting Classifier (Test Acc: **84.00%**, Weighted F1: **0.8603**, ROC-AUC: **0.9694**)
* **Landslide**: Random Forest Classifier (Test Acc: **85.50%**, High-Risk Recall: **100.00%**, ROC-AUC: **0.8451**)
* **Cyclone**: Random Forest Classifier (Test Acc: **70.00%**, High-Risk Recall: **91.43%**, ROC-AUC: **0.8623**)
* **Heatwave**: Gradient Boosting Classifier (Test Acc: **98.50%**, Macro F1: **0.9815**)
* **Drought**: Gradient Boosting Classifier (Test Acc: **99.50%**, Macro F1: **0.9770**, ROC-AUC: **0.9995**)

---

## 4. Rollback Procedure

If a rollback to Version 2 model binaries is required at any time:
```bash
# Copy V2 backup binaries back to production directory
cp ml/models_v2_backup/best_models_v2.joblib ml/models/best_models.joblib
cp ml/models_v2_backup/scaler_v2.joblib ml/models/scaler.joblib
```

---

## 5. Legal & Operational Disclaimer

> [!WARNING]
> This system is designed as an **Academic AI Risk Estimation & Research Portfolio System**. It is **NOT** an official emergency disaster management or evacuation warning authority. For life-safety decisions, always consult official government meteorological agencies (such as IMD, NOAA, WMO, or national disaster management authorities).
