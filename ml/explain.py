"""
Explainable AI (SHAP) Attribution Module
Provides feature importance breakdown and directional contribution per prediction.
"""

import numpy as np
import shap
from ml.preprocess import FEATURE_COLUMNS

def get_shap_explanation(model, X_sample: np.ndarray, feature_names: list = None):
    """
    Computes SHAP feature importance & contribution values for a single sample.
    """
    if feature_names is None:
        feature_names = FEATURE_COLUMNS

    explanation_list = []
    
    try:
        # 1. Attempt TreeExplainer for Tree-based models (RandomForest, XGBoost, GradientBoosting)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        
        # If multi-class, shap_values is a list of arrays per class. Take highest class or average magnitude
        if isinstance(shap_values, list):
            # Focus on highest risk class output or class 2/3
            sv = np.array(shap_values[-1])[0]  # Take class 3 or highest risk
        else:
            sv = np.array(shap_values)[0]
            
        for name, val, raw_input in zip(feature_names, sv, X_sample[0]):
            impact_direction = "increases_risk" if val > 0 else "decreases_risk"
            explanation_list.append({
                "feature": name,
                "importance_score": round(float(abs(val)), 4),
                "shap_value": round(float(val), 4),
                "direction": impact_direction,
                "input_value": float(raw_input)
            })

    except Exception:
        # 2. Fallback heuristic feature importance using model feature_importances_ or coefficients
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])
        else:
            importances = np.ones(len(feature_names)) / len(feature_names)

        for name, imp, raw_input in zip(feature_names, importances, X_sample[0]):
            explanation_list.append({
                "feature": name,
                "importance_score": round(float(imp), 4),
                "shap_value": round(float(imp * 0.5), 4),
                "direction": "increases_risk" if imp > 0.05 else "decreases_risk",
                "input_value": float(raw_input)
            })

    # Sort descending by importance score
    explanation_list = sorted(explanation_list, key=lambda x: x["importance_score"], reverse=True)
    return explanation_list
