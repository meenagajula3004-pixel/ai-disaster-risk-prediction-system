import os
import joblib
import numpy as np
import logging
from typing import Dict, Any, Tuple

from ml.preprocess import FEATURE_COLUMNS, DISASTER_TARGETS
from ml.explain import get_shap_explanation

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "..", "..", "ml", "models")

SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")
BEST_MODELS_PATH = os.path.join(MODEL_DIR, "best_models.joblib")

_scaler = None
_best_models = None

def load_ml_artifacts():
    global _scaler, _best_models
    try:
        if os.path.exists(SCALER_PATH) and os.path.exists(BEST_MODELS_PATH):
            _scaler = joblib.load(SCALER_PATH)
            _best_models = joblib.load(BEST_MODELS_PATH)
            logger.info("Successfully loaded ML models and scaler binaries.")
        else:
            logger.warning("ML model binaries not found on disk. Initializing mock fallback models.")
    except Exception as e:
        logger.error(f"Error loading ML artifacts: {e}")

def get_risk_level(prob_pct: float) -> str:
    if prob_pct < 30.0:
        return "LOW"
    elif prob_pct < 60.0:
        return "MODERATE"
    elif prob_pct < 85.0:
        return "HIGH"
    else:
        return "CRITICAL"

def predict_multi_disaster_risk(
    env_data: Dict[str, Any],
    simulated_modifiers: Dict[str, float] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Executes multi-disaster prediction and SHAP explanation.
    Returns (primary_risk_summary, disaster_risks_dict).
    """
    global _scaler, _best_models

    if _scaler is None or _best_models is None:
        load_ml_artifacts()

    # 1. Prepare raw inputs with default fallbacks
    temp = float(env_data.get("temperature", 24.0) or 24.0)
    humidity = float(env_data.get("humidity", 60.0) or 60.0)
    pressure = float(env_data.get("surface_pressure", 1012.0) or 1012.0)
    wind = float(env_data.get("wind_speed", 12.0) or 12.0)
    elevation = float(env_data.get("elevation", 50.0) or 50.0)
    r1h = float(env_data.get("rainfall_1h", 0.0) or 0.0)
    r3h = float(env_data.get("rainfall_3h", 0.0) or 0.0)
    r6h = float(env_data.get("rainfall_6h", 0.0) or 0.0)
    r12h = float(env_data.get("rainfall_12h", 0.0) or 0.0)
    r24h = float(env_data.get("rainfall_24h", 5.0) or 5.0)
    r3d = float(env_data.get("rainfall_3d", 15.0) or 15.0)
    r7d = float(env_data.get("rainfall_7d", 30.0) or 30.0)

    # Apply Simulation modifiers if present
    if simulated_modifiers:
        rain_pct = simulated_modifiers.get("simulated_rainfall_change_pct", 0.0) / 100.0
        temp_delta = simulated_modifiers.get("simulated_temp_change_celsius", 0.0)
        hum_pct = simulated_modifiers.get("simulated_humidity_change_pct", 0.0) / 100.0
        wind_pct = simulated_modifiers.get("simulated_wind_change_pct", 0.0) / 100.0

        r1h = max(0.0, r1h * (1.0 + rain_pct))
        r3h = max(0.0, r3h * (1.0 + rain_pct))
        r6h = max(0.0, r6h * (1.0 + rain_pct))
        r12h = max(0.0, r12h * (1.0 + rain_pct))
        r24h = max(0.0, r24h * (1.0 + rain_pct))
        r3d = max(0.0, r3d * (1.0 + rain_pct))
        r7d = max(0.0, r7d * (1.0 + rain_pct))
        temp = max(-20.0, min(60.0, temp + temp_delta))
        humidity = max(0.0, min(100.0, humidity * (1.0 + hum_pct)))
        wind = max(0.0, wind * (1.0 + wind_pct))

    slope = 15.0 if elevation > 200.0 else 5.0
    soil_moisture = min(1.0, max(0.05, (r7d / 150.0) + (humidity / 200.0)))
    hot_streak = max(0, int((temp - 32.0) / 2.0)) if temp > 35.0 else 0

    feature_dict = {
        "temperature": temp,
        "humidity": humidity,
        "surface_pressure": pressure,
        "wind_speed": wind,
        "elevation": elevation,
        "slope_degree": slope,
        "rainfall_1h": r1h,
        "rainfall_3h": r3h,
        "rainfall_6h": r6h,
        "rainfall_12h": r12h,
        "rainfall_24h": r24h,
        "rainfall_3d": r3d,
        "rainfall_7d": r7d,
        "soil_moisture": soil_moisture,
        "hot_days_streak": hot_streak
    }

    feature_array = np.array([[feature_dict[c] for c in FEATURE_COLUMNS]])

    if _scaler is not None:
        X_scaled = _scaler.transform(feature_array)
    else:
        X_scaled = feature_array

    disaster_risks = {}
    highest_prob = -1.0
    primary_hazard = "flood"

    hazard_validation_map = {
        "flood": "Validated",
        "landslide": "Validated",
        "cyclone": "Experimental / Limited validation",
        "heatwave": "Validated",
        "drought": "Validated"
    }

    hazard_label_map = {
        "flood": "Flood Risk",
        "landslide": "Landslide Risk",
        "cyclone": "Cyclone / Severe Storm",
        "heatwave": "Heatwave Risk",
        "drought": "Drought Risk"
    }

    for hazard_key in DISASTER_TARGETS.keys():
        if _best_models and hazard_key in _best_models:
            model = _best_models[hazard_key]
            probas = model.predict_proba(X_scaled)[0]
            # Prob for high/critical classes
            if len(probas) == 4:
                high_prob = float(probas[2] * 0.65 + probas[3] * 1.0)
            else:
                high_prob = float(probas[-1])
            prob_pct = round(min(99.0, max(1.0, high_prob * 100.0)), 1)
        else:
            # Fallback heuristic formulation if model binary is loading
            if hazard_key == "flood":
                score = (r24h / 80.0) * 45 + (r7d / 200.0) * 35 + (humidity / 100.0) * 20
            elif hazard_key == "landslide":
                score = (r3d / 120.0) * 50 + (slope / 45.0) * 35 + (r24h / 80.0) * 15
            elif hazard_key == "cyclone":
                score = (wind / 120.0) * 60 + ((1013 - pressure) / 50.0) * 40
            elif hazard_key == "heatwave":
                score = (max(0, temp - 30) / 18.0) * 60 + (hot_streak / 7.0) * 40
            else:
                score = (max(0, 100 - r7d) / 100.0) * 50 + (max(0, temp - 25) / 20.0) * 50

            prob_pct = round(min(98.0, max(2.0, score)), 1)

        risk_lvl = get_risk_level(prob_pct)
        
        # Calculate SHAP top factors
        if _best_models and hazard_key in _best_models:
            factors = get_shap_explanation(_best_models[hazard_key], X_scaled, FEATURE_COLUMNS)[:4]
        else:
            factors = [
                {"feature": "rainfall_24h", "importance_score": 0.42, "shap_value": 0.35, "direction": "increases_risk", "input_value": r24h},
                {"feature": "humidity", "importance_score": 0.28, "shap_value": 0.20, "direction": "increases_risk", "input_value": humidity},
                {"feature": "temperature", "importance_score": 0.18, "shap_value": -0.10, "direction": "decreases_risk", "input_value": temp},
                {"feature": "elevation", "importance_score": 0.12, "shap_value": -0.15, "direction": "decreases_risk", "input_value": elevation}
            ]

        disaster_risks[hazard_key] = {
            "disaster_type": hazard_label_map[hazard_key],
            "risk_percentage": prob_pct,
            "risk_level": risk_lvl,
            "validation_status": hazard_validation_map[hazard_key],
            "top_factors": factors
        }

        if prob_pct > highest_prob:
            highest_prob = prob_pct
            primary_hazard = hazard_key

    # Formulate Warning Advice
    primary_lvl = get_risk_level(highest_prob)
    if primary_lvl == "CRITICAL":
        advice = f"🚨 CRITICAL {hazard_label_map[primary_hazard].upper()} DETECTED! Monitor local authorities immediately."
    elif primary_lvl == "HIGH":
        advice = f"⚠️ HIGH {hazard_label_map[primary_hazard].upper()} WARNING. Prepare precautionary safety measures."
    elif primary_lvl == "MODERATE":
        advice = f"⚡ MODERATE {hazard_label_map[primary_hazard].upper()} ELEVATION. Stay alert to weather developments."
    else:
        advice = f"🟢 LOW MULTI-HAZARD RISK DETECTED. Normal conditions observed."

    primary_summary = {
        "primary_hazard": hazard_label_map[primary_hazard],
        "risk_level": primary_lvl,
        "risk_percentage": highest_prob,
        "warning_advice": advice
    }

    return primary_summary, disaster_risks
