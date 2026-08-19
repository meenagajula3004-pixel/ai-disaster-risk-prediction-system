# Machine Learning Pipeline & Methodology

This document outlines the dataset preparation, feature engineering, time-aware cross-validation, model comparison metrics, and SHAP explainability methodology for the **AI Multi-Disaster Risk Prediction System**.

---

## 1. Feature Engineering

The system computes 15 continuous hydrometeorological features:
1. `temperature`: Surface ambient temperature (°C)
2. `humidity`: Relative atmospheric humidity (%)
3. `surface_pressure`: Surface pressure (hPa)
4. `wind_speed`: 10m wind velocity (km/h)
5. `elevation`: Terrain height above sea level (m)
6. `slope_degree`: Terrain incline angle (0-60°)
7. `rainfall_1h`: Past 1-hour rainfall (mm)
8. `rainfall_3h`: Past 3-hour rainfall (mm)
9. `rainfall_6h`: Past 6-hour rainfall (mm)
10. `rainfall_12h`: Past 12-hour rainfall (mm)
11. `rainfall_24h`: Past 24-hour rainfall (mm)
12. `rainfall_3d`: Past 3-day cumulative rainfall (mm)
13. `rainfall_7d`: Past 7-day cumulative rainfall (mm)
14. `soil_moisture`: Soil volumetric water content index
15. `hot_days_streak`: Consecutive streak of days > 35°C

---

## 2. Time-Aware Validation Split

To prevent temporal data leakage in environmental time-series data:
- **Training Set (70%)**: Chronologically oldest dataset records
- **Validation Set (15%)**: Chronologically middle dataset records
- **Test Set (15%)**: Chronologically newest dataset records

StandardScaler is fitted strictly on the Training Set and applied to Validation/Test sets.

---

## 3. Candidate Model Evaluation Results

| Disaster Module | Candidate Models Evaluated | Best Model Selected | Validation Accuracy | High-Risk Recall | ROC-AUC | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **🌊 Flood Risk** | LogisticRegression, RandomForest, GradientBoosting | **GradientBoosting** | 97.44% | 92.11% | 0.9974 | Validated |
| **⛰️ Landslide Risk** | LogisticRegression, RandomForest, GradientBoosting | **LogisticRegression** | 98.44% | 96.32% | 0.9996 | Validated |
| **🌀 Cyclone / Storm** | LogisticRegression, RandomForest, GradientBoosting | **LogisticRegression** | 97.44% | 98.48% | 0.9994 | Experimental / Limited validation |
| **☀️ Heatwave Risk** | LogisticRegression, RandomForest, GradientBoosting | **LogisticRegression** | 97.33% | 97.24% | 0.9983 | Validated |
| **🏜️ Drought Risk** | LogisticRegression, RandomForest, GradientBoosting | **GradientBoosting** | 96.00% | 96.27% | 0.9985 | Validated |

> Selection criteria score formula: `Composite = (HighRiskRecall * 0.50) + (ROCAUC * 0.30) + (F1 * 0.20)`

---

## 4. SHAP Explainable AI Integration

For every prediction request, `ml.explain.get_shap_explanation` passes the scaled feature vector through `shap.TreeExplainer` or model attribution coefficients to extract exact feature contribution scores and directional effects (`increases_risk` vs `decreases_risk`).
