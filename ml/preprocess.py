"""
ML Preprocessing & Feature Engineering Module
Enforces Time-Aware Validation splitting to eliminate temporal data leakage.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    "temperature", "humidity", "surface_pressure", "wind_speed",
    "elevation", "slope_degree", "rainfall_1h", "rainfall_3h",
    "rainfall_6h", "rainfall_12h", "rainfall_24h", "rainfall_3d",
    "rainfall_7d", "soil_moisture", "hot_days_streak",
    "delta_wind_12h", "delta_pressure_12h"
]

DISASTER_TARGETS = {
    "flood": "flood_risk_target",
    "landslide": "landslide_risk_target",
    "cyclone": "cyclone_risk_target",
    "heatwave": "heatwave_risk_target",
    "drought": "drought_risk_target"
}

def load_raw_dataset(filepath: str) -> pd.DataFrame:
    """Loads dataset and ensures missing values are handled."""
    df = pd.read_csv(filepath)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)
    
    # Missing value imputation using median for continuous variables
    for col in FEATURE_COLUMNS:
        if col in df.columns and df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
            
    return df

def time_aware_split(df: pd.DataFrame, train_ratio: float = 0.70, val_ratio: float = 0.15):
    """
    Performs Time-Aware Chronological Splitting.
    Older records -> Train
    Middle records -> Validation
    Newest records -> Test
    """
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()
    
    return train_df, val_df, test_df

def fit_and_save_scaler(train_df: pd.DataFrame, output_scaler_path: str) -> StandardScaler:
    """Fits StandardScaler strictly on training set to prevent data leakage."""
    scaler = StandardScaler()
    scaler.fit(train_df[FEATURE_COLUMNS])
    os.makedirs(os.path.dirname(output_scaler_path), exist_ok=True)
    joblib.dump(scaler, output_scaler_path)
    return scaler

def transform_features(df: pd.DataFrame, scaler: StandardScaler) -> np.ndarray:
    """Transforms raw features using fitted scaler."""
    return scaler.transform(df[FEATURE_COLUMNS])
