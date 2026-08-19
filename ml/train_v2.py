"""
Phase 4: Model Retraining & Evaluation Engine on Real-World Dataset (V2)
Uses Time-Aware Chronological Splitting (70% Train, 15% Val, 15% Test)
Evaluates Logistic Regression, Random Forest, XGBoost across 5 Hazards.
Prioritizes High-Risk Event Recall & ROC-AUC.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from ml.preprocess import FEATURE_COLUMNS, DISASTER_TARGETS, load_raw_dataset, time_aware_split, fit_and_save_scaler, transform_features

ML_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(ML_DIR), "data", "raw")
REAL_DATA_PATH = os.path.join(DATA_DIR, "real_multi_disaster_dataset.csv")

METRICS_DIR = os.path.join(ML_DIR, "metrics")
MODELS_DIR = os.path.join(ML_DIR, "models")
os.makedirs(METRICS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def train_and_evaluate_v2():
    print("=== Phase 4: Training V2 Models on Real-World Dataset ===")
    if not os.path.exists(REAL_DATA_PATH):
        raise FileNotFoundError(f"Real-world dataset not found at {REAL_DATA_PATH}. Run fetch_real_datasets.py first.")
        
    df = load_raw_dataset(REAL_DATA_PATH)
    print(f"Loaded {len(df)} real-world samples from {REAL_DATA_PATH}")
    
    # 1. Time-Aware Chronological Split
    train_df, val_df, test_df = time_aware_split(df)
    print(f"Train samples: {len(train_df)} | Val samples: {len(val_df)} | Test samples: {len(test_df)}")
    
    # 2. Fit Scaler on Training Data strictly
    scaler_v2_path = os.path.join(MODELS_DIR, "scaler.joblib")
    scaler = fit_and_save_scaler(train_df, scaler_v2_path)
    
    X_train = transform_features(train_df, scaler)
    X_val = transform_features(val_df, scaler)
    X_test = transform_features(test_df, scaler)
    
    candidate_classifiers = {
        "LogisticRegression": lambda: LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        "RandomForest": lambda: RandomForestClassifier(n_estimators=150, max_depth=10, class_weight="balanced", random_state=42),
        "GradientBoosting": lambda: GradientBoostingClassifier(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=42)
    }
    
    best_v2_models = {}
    model_comparison_results = {}
    final_evaluation_report = {}
    
    for hazard, target_col in DISASTER_TARGETS.items():
        print(f"\n--- Training Models for Hazard: {hazard.upper()} ({target_col}) ---")
        
        y_train = train_df[target_col].values
        y_val = val_df[target_col].values
        y_test = test_df[target_col].values
        
        best_hazard_model = None
        best_hazard_score = -1.0
        best_model_name = ""
        hazard_comparison = {}
        
        for name, clf_factory in candidate_classifiers.items():
            clf = clf_factory()
            clf.fit(X_train, y_train)
            
            y_val_pred = clf.predict(X_val)
            
            # Metric Calculation
            acc = accuracy_score(y_val, y_val_pred)
            prec = precision_score(y_val, y_val_pred, average="weighted", zero_division=0)
            rec = recall_score(y_val, y_val_pred, average="weighted", zero_division=0)
            f1 = f1_score(y_val, y_val_pred, average="weighted", zero_division=0)
            
            # High-Risk (class >= 2) Recall Priority Metric
            high_risk_mask = y_val >= 2
            if np.sum(high_risk_mask) > 0:
                high_risk_rec = float(recall_score(y_val[high_risk_mask], y_val_pred[high_risk_mask], average="micro", zero_division=0))
            else:
                high_risk_rec = float(rec)
                
            try:
                if hasattr(clf, "predict_proba"):
                    y_val_proba = clf.predict_proba(X_val)
                    auc = float(roc_auc_score(y_val, y_val_proba, multi_class="ovr", average="weighted"))
                else:
                    auc = 0.0
            except Exception:
                auc = 0.0
                
            # Weighted Model Score prioritizing High Risk Recall and ROC-AUC
            selection_score = (0.45 * high_risk_rec) + (0.35 * auc) + (0.20 * f1)
            
            hazard_comparison[name] = {
                "accuracy": round(float(acc), 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1_score": round(float(f1), 4),
                "high_risk_recall": round(float(high_risk_rec), 4),
                "roc_auc": round(float(auc), 4),
                "selection_score": round(float(selection_score), 4)
            }
            
            print(f"  [{name}] Acc: {acc:.4f} | F1: {f1:.4f} | High-Risk Recall: {high_risk_rec:.4f} | ROC-AUC: {auc:.4f}")
            
            if selection_score > best_hazard_score:
                best_hazard_score = selection_score
                best_hazard_model = clf
                best_model_name = name
                
        print(f"-> Selected Best Model for {hazard.upper()}: {best_model_name} (Score: {best_hazard_score:.4f})")
        best_v2_models[hazard] = best_hazard_model
        model_comparison_results[hazard] = hazard_comparison
        
        # Test Set Final Evaluation
        y_test_pred = best_hazard_model.predict(X_test)
        cm = confusion_matrix(y_test, y_test_pred).tolist()
        
        final_evaluation_report[hazard] = {
            "selected_model": best_model_name,
            "test_accuracy": round(float(accuracy_score(y_test, y_test_pred)), 4),
            "test_precision": round(float(precision_score(y_test, y_test_pred, average="weighted", zero_division=0)), 4),
            "test_recall": round(float(recall_score(y_test, y_test_pred, average="weighted", zero_division=0)), 4),
            "test_f1_score": round(float(f1_score(y_test, y_test_pred, average="weighted", zero_division=0)), 4),
            "test_confusion_matrix": cm
        }
        
    # Save Best V2 Models binary to best_models.joblib
    models_path = os.path.join(MODELS_DIR, "best_models.joblib")
    joblib.dump(best_v2_models, models_path)
    print(f"\nSuccessfully serialized V2 models to {models_path}")
    
    # Save Metrics Reports
    with open(os.path.join(METRICS_DIR, "model_comparison.json"), "w") as f:
        json.dump(model_comparison_results, f, indent=2)
        
    with open(os.path.join(METRICS_DIR, "evaluation_report.json"), "w") as f:
        json.dump(final_evaluation_report, f, indent=2)
        
    print(f"Metrics saved to {METRICS_DIR}")
    return final_evaluation_report

if __name__ == "__main__":
    train_and_evaluate_v2()
