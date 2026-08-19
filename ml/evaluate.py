"""
ML Model Evaluation Module
Calculates Accuracy, Precision, Recall (focusing on High-Risk Recall), F1, ROC-AUC, and Confusion Matrices.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

def evaluate_classifier_model(model, X_val: np.ndarray, y_val: np.ndarray, model_name: str, disaster_name: str):
    """
    Evaluates a trained classifier on validation/test set.
    Returns structured metric dict.
    """
    y_pred = model.predict(X_val)
    
    # Probabilities for ROC-AUC
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_val)
    else:
        y_proba = None

    acc = float(accuracy_score(y_val, y_pred))
    prec = float(precision_score(y_val, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_val, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_val, y_pred, average="weighted", zero_division=0))

    # Recall specifically for High-Risk (class 2) and Critical-Risk (class 3) events
    class_recalls = recall_score(y_val, y_pred, average=None, zero_division=0)
    high_risk_recall = float(class_recalls[2]) if len(class_recalls) > 2 else float(rec)
    critical_risk_recall = float(class_recalls[3]) if len(class_recalls) > 3 else float(rec)

    # Multi-class ROC-AUC score
    try:
        if y_proba is not None:
            auc = float(roc_auc_score(y_val, y_proba, multi_class="ovr"))
        else:
            auc = 0.0
    except Exception:
        auc = 0.0

    cm = confusion_matrix(y_val, y_pred).tolist()

    metrics = {
        "disaster": disaster_name,
        "model_name": model_name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "high_risk_recall": round(high_risk_recall, 4),
        "critical_risk_recall": round(critical_risk_recall, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": cm
    }

    return metrics
