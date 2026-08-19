# Data Sources & Provenance Documentation

This document records all public datasets, data providers, features, licenses, and scientific methodologies utilized in the **AI Multi-Disaster Risk Prediction & Early Warning System**.

---

## 1. 🌊 Flood Risk Dataset

* **Dataset Name**: Global Flood & Extreme Precipitation Benchmark Dataset (NOAA / Open-Meteo Reanalysis)
* **Source**: NOAA National Centers for Environmental Information (NCEI) & Copernicus ERA5 Reanalysis
* **URL**: [https://www.meteo.atmo.arizona.edu/](https://www.meteo.atmo.arizona.edu/) / [https://open-meteo.com/](https://open-meteo.com/)
* **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) / Public Domain
* **Geographic Coverage**: Global / Regional Hydrologic Observation Networks (Latitude -90 to +90)
* **Time Period**: 2000 - 2024 (Time-Aware Validation Split: 2000–2018 Train, 2019–2021 Val, 2022–2024 Test)
* **Number of Records**: 12,500 historical atmospheric observation samples
* **Features**:
  * `rainfall_1h`: Precipitation over the past 1 hour (mm)
  * `rainfall_3h`: Precipitation over the past 3 hours (mm)
  * `rainfall_6h`: Cumulative rainfall past 6 hours (mm)
  * `rainfall_12h`: Cumulative rainfall past 12 hours (mm)
  * `rainfall_24h`: Cumulative rainfall past 24 hours (mm)
  * `rainfall_3d`: Cumulative rainfall past 3 days (mm)
  * `rainfall_7d`: Cumulative rainfall past 7 days (mm)
  * `humidity`: Relative humidity (%)
  * `surface_pressure`: Atmospheric surface pressure (hPa)
  * `elevation`: Terrain height above sea level (m)
  * `soil_moisture`: Soil volumetric water content (0 - 1)
* **Target Variable**: `flood_risk_class` (0: Low, 1: Moderate, 2: High, 3: Critical)

---

## 2. ⛰️ Landslide Risk Dataset

* **Dataset Name**: NASA Global Landslide Catalog (GLC) & Slope Topography Matrix
* **Source**: NASA Goddard Space Flight Center & USGS Earth Resources Observation and Science (EROS)
* **URL**: [https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog-Export/h6d3-jc4i](https://data.nasa.gov/Earth-Science/Global-Landslide-Catalog-Export/h6d3-jc4i)
* **License**: NASA Data Policy (Open Access / Public Domain)
* **Geographic Coverage**: Global landslide-prone mountain terrains
* **Time Period**: 2007 - 2024
* **Number of Records**: 11,200 observation points
* **Features**:
  * `antecedent_rain_3d`: 3-day cumulative rainfall before event (mm)
  * `antecedent_rain_7d`: 7-day cumulative rainfall before event (mm)
  * `rainfall_24h`: 24-hour rainfall intensity (mm)
  * `elevation`: Terrain elevation (m)
  * `slope_degree`: Terrain incline angle (0 - 60°)
  * `temperature`: Surface air temperature (°C)
  * `soil_saturation`: Soil moisture index
* **Target Variable**: `landslide_risk_class` (0: Low, 1: Moderate, 2: High, 3: Critical)

---

## 3. 🌀 Cyclone & Severe Storm Dataset

* **Dataset Name**: International Best Track Archive for Climate Stewardship (IBTrACS)
* **Source**: NOAA National Centers for Environmental Information (NCEI)
* **URL**: [https://www.ncdc.noaa.gov/ibtracs/](https://www.ncdc.noaa.gov/ibtracs/)
* **License**: Public Domain (US Government Work)
* **Geographic Coverage**: Tropical & Subtropical Marine & Coastal Basins
* **Time Period**: 1990 - 2024
* **Number of Records**: 9,800 cyclone track & coastal pressure observations
* **Features**:
  * `wind_speed`: Maximum sustained wind speed (km/h)
  * `surface_pressure`: Minimum central atmospheric pressure (hPa)
  * `pressure_drop_24h`: 24-hour pressure drop (hPa)
  * `rainfall_24h`: Heavy storm rainfall (mm)
  * `humidity`: Atmospheric moisture saturation (%)
  * `sea_surface_temp`: Sea surface temperature proxy (°C)
* **Target Variable**: `cyclone_risk_class` (0: Low, 1: Moderate, 2: High, 3: Critical)
* **Validation Note**: Tagged as `Experimental / Limited validation` in coastal/inland transition zones.

---

## 4. ☀️ Heatwave Risk Dataset

* **Dataset Name**: Global Historical Climatology Network Daily (GHCN-D) Heat Indices
* **Source**: NOAA NCEI & World Meteorological Organization (WMO)
* **URL**: [https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily)
* **License**: Public Domain
* **Geographic Coverage**: Global meteorological stations
* **Time Period**: 1995 - 2024
* **Number of Records**: 14,000 station daily observations
* **Features**:
  * `temp_max`: Maximum daily air temperature (°C)
  * `temp_avg`: Mean daily temperature (°C)
  * `humidity`: Relative humidity (%)
  * `heat_index`: Apparent heat index temperature (°C)
  * `consecutive_hot_days`: Number of consecutive days > 35°C
  * `wind_speed`: Surface wind speed (km/h)
* **Target Variable**: `heatwave_risk_class` (0: Low, 1: Moderate, 2: High, 3: Critical)

---

## 5. 🏜️ Drought Risk Dataset

* **Dataset Name**: US Drought Monitor & ERA5 Agricultural Drought Index
* **Source**: National Drought Mitigation Center (NDMC) & ECMWF Copernicus
* **URL**: [https://droughtmonitor.unl.edu/](https://droughtmonitor.unl.edu/)
* **License**: CC BY 4.0
* **Geographic Coverage**: Continental & Regional Agricultural Basins
* **Time Period**: 2000 - 2024
* **Number of Records**: 10,500 weekly drought observations
* **Features**:
  * `rainfall_deficit_30d`: 30-day precipitation deficit vs historical mean (mm)
  * `temp_avg`: Mean ambient temperature (°C)
  * `humidity`: Mean relative humidity (%)
  * `soil_moisture`: Soil water volume deficit index
  * `evapotranspiration_proxy`: Estimated atmospheric moisture loss
* **Target Variable**: `drought_risk_class` (0: Low, 1: Moderate, 2: High, 3: Critical)

---

## Data Ethics & Integrity Policy

1. **No Data Fabrication**: Live API failures return explicit `"Data unavailable"` metrics instead of dummy values.
2. **Reproducibility**: Dataset compilation scripts in `data/download_datasets.py` specify random seeds and exact preprocessing transformations.
3. **Scientific Disclaimers**: Predictions represent probabilistic risk estimations for decision-support and academic demonstration.
