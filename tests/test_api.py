import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import get_db
from backend.app.models.db_models import UserDB
from backend.app.api.v1.endpoints.auth import create_access_token
from backend.app.services.security_service import hash_password

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
    # 1. Unauthenticated request must return 401
    unauth_response = client.get("/api/v1/admin/stats")
    assert unauth_response.status_code == 401

    # 2. Authenticated Admin request must return 200
    db: Session = next(get_db())
    admin_user = db.query(UserDB).filter(UserDB.email == "admin@example.com").first()
    if not admin_user:
        admin_user = UserDB(
            email="admin@example.com",
            hashed_password=hash_password("AdminPass@2026"),
            full_name="System Admin",
            role="admin",
            is_verified=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
    else:
        admin_user.role = "admin"
        admin_user.is_verified = True
        db.commit()

    token = create_access_token({"sub": admin_user.email, "user_id": admin_user.id, "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/admin/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "hazard_distribution" in data
