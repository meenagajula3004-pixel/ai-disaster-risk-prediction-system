import pytest
import numpy as np
import pandas as pd
from ml.preprocess import FEATURE_COLUMNS, DISASTER_TARGETS, time_aware_split
from backend.app.services.ml_service import predict_multi_disaster_risk

def test_feature_columns_count():
    assert len(FEATURE_COLUMNS) == 15

def test_disaster_targets_count():
    assert len(DISASTER_TARGETS) == 5

def test_time_aware_split():
    df = pd.DataFrame({'timestamp': pd.date_range('2020-01-01', periods=100)})
    train, val, test = time_aware_split(df, 0.70, 0.15)
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15
    assert train['timestamp'].max() <= val['timestamp'].min()
    assert val['timestamp'].max() <= test['timestamp'].min()

def test_multi_disaster_prediction():
    sample_env = {
        "temperature": 32.5,
        "humidity": 78.0,
        "surface_pressure": 995.0,
        "wind_speed": 45.0,
        "rainfall_24h": 65.0,
        "rainfall_7d": 180.0,
        "elevation": 25.0
    }
    primary_summary, disaster_risks = predict_multi_disaster_risk(sample_env)
    assert "primary_hazard" in primary_summary
    assert "risk_percentage" in primary_summary
    assert len(disaster_risks) == 5
    assert "flood" in disaster_risks
    assert "landslide" in disaster_risks
    assert "cyclone" in disaster_risks
    assert "heatwave" in disaster_risks
    assert "drought" in disaster_risks
