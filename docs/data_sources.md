# Real-World Data Sources & Dataset Provenance (Version 2)

This document provides complete metadata and scientific provenance for the real-world dataset used to train Version 2 of the **AI Multi-Disaster Risk Prediction & Early Warning System**.

---

## 1. Dataset Overview

* **Dataset Name**: Real-World Hydrometeorological & Multi-Hazard Benchmark (V2)
* **Storage Location**: [`data/raw/real_multi_disaster_dataset.csv`](file:///C:/Users/VARSHITA/.gemini/antigravity/scratch/ai-disaster-risk-prediction-system/data/raw/real_multi_disaster_dataset.csv)
* **Metadata Location**: [`data/raw/real_dataset_metadata.json`](file:///C:/Users/VARSHITA/.gemini/antigravity/scratch/ai-disaster-risk-prediction-system/data/raw/real_dataset_metadata.json)
* **Total Samples**: 6,000 observations
* **Time Horizon**: 2018-01-01 to 2024-01-01
* **Feature Count**: 15 input features
* **Target Count**: 5 disaster hazard classification targets

---

## 2. Authoritative Real-World Data Sources

### A. NASA Global Landslide Catalog (GLC)
* **Organization**: NASA Goddard Space Flight Center
* **Source URL**: [https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog/h9d8-gfdw](https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog/h9d8-gfdw)
* **License**: Public Domain (US Government Work)
* **Usage**: Provides verified historical landslide event coordinates (`latitude`, `longitude`), onset dates, and trigger types.

### B. NOAA IBTrACS Tropical Cyclone Database
* **Organization**: NOAA NCEI / World Meteorological Organization (WMO)
* **Source URL**: [https://www.ncei.noaa.gov/products/international-best-track-archive](https://www.ncei.noaa.gov/products/international-best-track-archive)
* **License**: Public Domain (US NOAA)
* **Usage**: Provides 3-hourly tropical cyclone track positions, maximum sustained wind speeds (knots), and surface pressures (hPa).

### C. Copernicus ERA5 Reanalysis & Open-Meteo Historical Archive API
* **Organization**: European Centre for Medium-Range Weather Forecasts (ECMWF) / Open-Meteo
* **Source URL**: [https://archive-api.open-meteo.com/v1/archive](https://archive-api.open-meteo.com/v1/archive)
* **License**: Creative Commons Attribution 4.0 International (CC-BY 4.0)
* **Usage**: Sourced historical 7-day cumulative precipitation windows, surface temperatures, relative humidity, and barometric pressures for every event coordinate.

---

## 3. Input Features & Target Definitions

### Input Feature Matrix (15 Parameters)
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
15. `hot_days_streak`: Streak of consecutive days with temperature > 35°C

### Ordinal Risk Level Targets (4 Classes: 0=Low, 1=Moderate, 2=High, 3=Critical)
* `flood_risk_target`: 24h & 7-day rain, soil moisture, elevation factor.
* `landslide_risk_target`: 3-day & 24h rain, slope incline, soil moisture, NASA event ground truth.
* `cyclone_risk_target`: Wind speed, pressure drop, 6h intense rain.
* `heatwave_risk_target`: Temperature excess, consecutive hot day streak, humidity.
* `drought_risk_target`: 7-day rain deficit, high temperature, low soil moisture.

---

## 4. Legal & Operational Disclaimer

> [!WARNING]
> This system is designed as an **Academic AI Risk Estimation & Research Portfolio System**. It is **NOT** an official emergency disaster management or evacuation warning authority. For life-safety decisions, always consult official government meteorological agencies (such as IMD, NOAA, WMO, or national disaster management authorities).
