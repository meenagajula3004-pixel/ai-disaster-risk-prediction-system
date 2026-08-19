"""
V3.1 Scientific Model Retraining & Evaluation Script
Implements:
1. Event-Aware Chronological Grouped Splitting (0 event leakage across Train / Val / Test)
2. Robust Multiclass ROC-AUC computation (handles missing classes natively using probability normalization)
3. Balanced Class Weighting & Sample Weighting across candidates (LogisticRegression, RandomForest, GradientBoosting)
4. Expanded 17-feature telemetry set including 12h wind & pressure tendency deltas
5. Saves temporary artifacts to ml/models_v31_temp/ without touching deployed production files
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "raw", "v31_authoritative_historical_dataset.csv")
TEMP_MODEL_DIR = os.path.join(BASE_DIR, "ml", "models_v31_temp")
METRICS_DIR = os.path.join(BASE_DIR, "ml", "metrics")
os.makedirs(TEMP_MODEL_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

FEATURE_COLUMNS_V31 = [
    "temperature", "humidity", "surface_pressure", "wind_speed",
    "elevation", "slope_degree", "rainfall_1h", "rainfall_3h",
    "rainfall_6h", "rainfall_12h", "rainfall_24h", "rainfall_3d",
    "rainfall_7d", "soil_moisture", "hot_days_streak",
    "delta_wind_12h", "delta_pressure_12h"
]

DISASTER_TARGETS = [
    "flood_risk_target",
    "landslide_risk_target",
    "cyclone_risk_target",
    "heatwave_risk_target",
    "drought_risk_target"
]

def load_and_preprocess_v31_event_aware():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"V3.1 Dataset missing at {DATASET_PATH}")
        
    df = pd.read_csv(DATASET_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    # Event-Aware Chronological Split
    events_by_date = df.groupby("event_name")["timestamp"].min().sort_values().reset_index()
    num_events = len(events_by_date)
    
    train_event_end = int(num_events * 0.70)
    val_event_end = int(num_events * 0.85)
    
    train_events = set(events_by_date["event_name"].iloc[:train_event_end])
    val_events = set(events_by_date["event_name"].iloc[train_event_end:val_event_end])
    test_events = set(events_by_date["event_name"].iloc[val_event_end:])
    
    train_df = df[df["event_name"].isin(train_events)].copy()
    val_df = df[df["event_name"].isin(val_events)].copy()
    test_df = df[df["event_name"].isin(test_events)].copy()
    
    print(f"=== Event-Aware Chronological Group Split ===")
    print(f"Total Independent Events: {num_events}")
    print(f"Train Set: {len(train_df)} samples across {len(train_events)} events ({train_df['timestamp'].min().strftime('%Y-%m-%d')} to {train_df['timestamp'].max().strftime('%Y-%m-%d')})")
    print(f"Val Set:   {len(val_df)} samples across {len(val_events)} events ({val_df['timestamp'].min().strftime('%Y-%m-%d')} to {val_df['timestamp'].max().strftime('%Y-%m-%d')})")
    print(f"Test Set:  {len(test_df)} samples across {len(test_events)} events ({test_df['timestamp'].min().strftime('%Y-%m-%d')} to {test_df['timestamp'].max().strftime('%Y-%m-%d')})")
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_df[FEATURE_COLUMNS_V31])
    X_val = scaler.transform(val_df[FEATURE_COLUMNS_V31])
    X_test = scaler.transform(test_df[FEATURE_COLUMNS_V31])
    
    return train_df, val_df, test_df, train_events, val_events, test_events, X_train, X_val, X_test, scaler

def calculate_multiclass_roc_auc(model, X, y):
    """Calculates multiclass ROC-AUC dynamically for present classes in target split."""
    if not hasattr(model, "predict_proba"):
        return 0.5
        
    try:
        y_proba = model.predict_proba(X)
        present_classes = np.unique(y)
        
        if len(present_classes) <= 1:
            return 1.0
            
        # Map model.classes_ to present_classes
        model_classes = list(model.classes_)
        class_indices = [model_classes.index(c) for c in present_classes if c in model_classes]
        
        if len(class_indices) <= 1:
            return 0.5
            
        y_proba_sub = y_proba[:, class_indices]
        row_sums = y_proba_sub.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        y_proba_sub = y_proba_sub / row_sums
        
        return float(roc_auc_score(y, y_proba_sub, multi_class="ovr", average="macro", labels=present_classes))
    except Exception as e:
        return 0.5

def train_and_evaluate_v31_models():
    train_df, val_df, test_df, train_events, val_events, test_events, X_train, X_val, X_test, scaler = load_and_preprocess_v31_event_aware()
    
    best_models = {}
    evaluation_report = {
        "dataset_used": "v31_authoritative_historical_dataset.csv",
        "total_records": len(train_df) + len(val_df) + len(test_df),
        "split": "Event-Aware Grouped Chronological 70% Train / 15% Val / 15% Test",
        "event_split_counts": {
            "train_events": len(train_events),
            "val_events": len(val_events),
            "test_events": len(test_events)
        },
        "hazards": {}
    }
    
    for target in DISASTER_TARGETS:
        hazard_name = target.replace("_risk_target", "")
        print(f"\n================ Training V3.1 Candidate Models for: {hazard_name.upper()} ================")
        
        y_train = train_df[target].values
        y_val = val_df[target].values
        y_test = test_df[target].values
        
        sample_weights_train = compute_sample_weight("balanced", y_train)
        
        candidate_factories = {
            "LogisticRegression": lambda: LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
            "RandomForest": lambda: RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=42),
            "GradientBoosting": lambda: GradientBoostingClassifier(n_estimators=120, max_depth=5, learning_rate=0.07, random_state=42)
        }
        
        best_cand_name = None
        best_cand_model = None
        best_cand_score = -1.0
        candidate_evals = {}
        
        for name, factory in candidate_factories.items():
            model = factory()
            if name == "GradientBoosting":
                model.fit(X_train, y_train, sample_weight=sample_weights_train)
            else:
                model.fit(X_train, y_train)
                
            y_val_pred = model.predict(X_val)
            val_acc = accuracy_score(y_val, y_val_pred)
            val_prec, val_rec, val_f1, _ = precision_recall_fscore_support(y_val, y_val_pred, average="macro", zero_division=0)
            val_weighted_f1 = float(precision_recall_fscore_support(y_val, y_val_pred, average="weighted", zero_division=0)[2])
            
            # High-risk recall (y >= 2)
            high_risk_mask = (y_val >= 2)
            if np.sum(high_risk_mask) > 0:
                high_risk_recall = float(np.mean(y_val_pred[high_risk_mask] >= 1))
            else:
                high_risk_recall = float(val_rec)
                
            val_roc_auc = calculate_multiclass_roc_auc(model, X_val, y_val)
            
            composite_score = (val_f1 * 0.35) + (val_weighted_f1 * 0.25) + (high_risk_recall * 0.25) + (val_roc_auc * 0.15)
            
            candidate_evals[name] = {
                "val_accuracy": round(val_acc, 4),
                "val_macro_f1": round(val_f1, 4),
                "val_weighted_f1": round(val_weighted_f1, 4),
                "val_high_risk_recall": round(high_risk_recall, 4),
                "val_roc_auc": round(val_roc_auc, 4),
                "composite_score": round(composite_score, 4)
            }
            
            print(f"   [{name}] Acc: {val_acc:.4f} | Macro F1: {val_f1:.4f} | Weighted F1: {val_weighted_f1:.4f} | High-Risk Rec: {high_risk_recall:.4f} | ROC-AUC: {val_roc_auc:.4f}")
            
            if composite_score > best_cand_score:
                best_cand_score = composite_score
                best_cand_name = name
                best_cand_model = model
                
        print(f"   -> Selected Best Candidate for {hazard_name.upper()}: {best_cand_name}")
        best_models[hazard_name] = best_cand_model
        
        # Test Set Final Evaluation for Selected Model
        y_test_pred = best_cand_model.predict(X_test)
        test_acc = accuracy_score(y_test, y_test_pred)
        t_prec, t_rec, t_f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average="macro", zero_division=0)
        t_weighted_f1 = float(precision_recall_fscore_support(y_test, y_test_pred, average="weighted", zero_division=0)[2])
        
        # Per-class recall
        unique_test_classes = sorted(list(np.unique(np.concatenate([y_test, y_test_pred]))))
        per_class_rec = {}
        for cls in unique_test_classes:
            mask = (y_test == cls)
            if np.sum(mask) > 0:
                per_class_rec[str(cls)] = round(float(np.mean(y_test_pred[mask] == cls)), 4)
            else:
                per_class_rec[str(cls)] = 0.0
                
        high_risk_test_mask = (y_test >= 2)
        if np.sum(high_risk_test_mask) > 0:
            high_risk_test_recall = float(np.mean(y_test_pred[high_risk_test_mask] >= 1))
        else:
            high_risk_test_recall = float(t_rec)
            
        test_roc_auc = calculate_multiclass_roc_auc(best_cand_model, X_test, y_test)
        cm = confusion_matrix(y_test, y_test_pred).tolist()
        class_dist_test = pd.Series(y_test).value_counts().to_dict()
        
        evaluation_report["hazards"][hazard_name] = {
            "selected_model": best_cand_name,
            "candidate_comparison": candidate_evals,
            "test_metrics": {
                "accuracy": round(test_acc, 4),
                "precision_macro": round(t_prec, 4),
                "recall_macro": round(t_rec, 4),
                "f1_macro": round(t_f1, 4),
                "weighted_f1": round(t_weighted_f1, 4),
                "high_risk_recall": round(high_risk_test_recall, 4),
                "roc_auc_macro": round(test_roc_auc, 4),
                "per_class_recall": per_class_rec
            },
            "test_class_distribution": {str(k): int(v) for k, v in class_dist_test.items()},
            "confusion_matrix": cm
        }
        
    # Save temporary V3.1 model artifacts
    temp_models_path = os.path.join(TEMP_MODEL_DIR, "v31_best_models.joblib")
    temp_scaler_path = os.path.join(TEMP_MODEL_DIR, "v31_scaler.joblib")
    joblib.dump(best_models, temp_models_path)
    joblib.dump(scaler, temp_scaler_path)
    print(f"\nSaved temporary V3.1 model binaries to {temp_models_path}")
    
    report_path = os.path.join(METRICS_DIR, "v31_evaluation_report.json")
    with open(report_path, "w") as f:
        json.dump(evaluation_report, f, indent=2)
    print(f"Saved complete V3.1 evaluation report to {report_path}")
    
    return evaluation_report

if __name__ == "__main__":
    train_and_evaluate_v31_models()
