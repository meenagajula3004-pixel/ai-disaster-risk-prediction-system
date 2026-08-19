import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_location_search_endpoint():
    response = client.get("/api/v1/location/search?query=Bhimavaram")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_prediction_endpoint():
    payload = {
        "latitude": 16.5449,
        "longitude": 81.5212,
        "location_name": "Bhimavaram, Andhra Pradesh"
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "primary_risk" in data
    assert "disaster_risks" in data
    assert len(data["disaster_risks"]) == 5

def test_what_if_endpoint():
    payload = {
        "latitude": 16.5449,
        "longitude": 81.5212,
        "location_name": "Bhimavaram Test",
        "simulated_rainfall_change_pct": 30.0,
        "simulated_temp_change_celsius": 2.0
    }
    response = client.post("/api/v1/predict/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_simulation"] is True

def test_admin_stats_endpoint():
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "hazard_distribution" in data
