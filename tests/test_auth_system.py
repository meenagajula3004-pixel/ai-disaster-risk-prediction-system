import pytest
import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.core.database import get_db, Base, engine
from backend.app.models.db_models import UserDB, OTPRecordDB, PredictionRecordDB
from backend.app.services.security_service import (
    validate_and_normalize_email, validate_strong_password,
    hash_password, verify_password
)

client = TestClient(app)

def test_email_validation():
    # Invalid email formats
    invalid_emails = ["abc", "abc@", "abc.com@", "@gmail.com", "user name@gmail.com"]
    for email in invalid_emails:
        valid, clean, err = validate_and_normalize_email(email)
        assert valid is False, f"Expected {email} to be invalid"

    # Valid email formats
    valid_emails = ["user@gmail.com", "student@outlook.com", "example@yahoo.com", "  TEST@Domain.COM  "]
    for email in valid_emails:
        valid, clean, err = validate_and_normalize_email(email)
        assert valid is True, f"Expected {email} to be valid"
        assert clean == email.strip().lower()

def test_password_policy():
    # Weak passwords
    weak_passwords = ["password", "Password", "Password123", "password@", "12345678", "Short1!"]
    for pwd in weak_passwords:
        valid, err = validate_strong_password(pwd)
        assert valid is False, f"Expected password '{pwd}' to fail strength policy"

    # Valid strong password
    valid, err = validate_strong_password("Meena@2026", "Meena@2026")
    assert valid is True, f"Expected 'Meena@2026' to pass: {err}"

def test_full_auth_direct_registration_flow():
    # Setup test database session
    db: Session = next(get_db())

    test_email = f"authtest_{int(datetime.datetime.utcnow().timestamp())}@example.com"
    test_password = "SecurePassword@2026"
    test_name = "Auth Test User"

    # 1. Register User directly (No OTP required)
    reg_payload = {
        "full_name": test_name,
        "email": test_email,
        "password": test_password,
        "confirm_password": test_password,
        "captcha_token": "bypass_dev_captcha"
    }
    res_reg = client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 200, res_reg.json()
    reg_data = res_reg.json()
    assert "access_token" not in reg_data
    assert "Registration successful! Please login to continue." in reg_data["message"]

    # Verify activated user state in DB
    user_db = db.query(UserDB).filter(UserDB.email == test_email).first()
    assert user_db is not None
    assert user_db.is_verified is True
    assert user_db.is_active is True

    # 2. Login directly with credentials
    res_login = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": test_password,
        "captcha_token": "bypass_dev_captcha"
    })
    assert res_login.status_code == 200, res_login.json()
    token_data = res_login.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # 3. Fetch User Profile (/auth/me)
    headers = {"Authorization": f"Bearer {access_token}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == test_email

    # 4. Make a Prediction as Authenticated User
    pred_payload = {
        "latitude": 16.5449,
        "longitude": 81.5212,
        "location_name": "Bhimavaram"
    }
    res_pred = client.post("/api/v1/predict", json=pred_payload, headers=headers)
    assert res_pred.status_code == 200
    assert "disaster_risks" in res_pred.json()

    # 5. Fetch User Specific History (/history/user)
    res_hist = client.get("/api/v1/history/user", headers=headers)
    assert res_hist.status_code == 200
    history_items = res_hist.json()
    assert len(history_items) > 0
    assert history_items[0]["location_name"] == "Bhimavaram"

    # 6. Test Non-Admin Access to Admin Endpoint (Must return 403 Forbidden)
    res_admin_forbidden = client.get("/api/v1/admin/stats", headers=headers)
    assert res_admin_forbidden.status_code == 403
    assert "Admin privileges required" in res_admin_forbidden.json()["detail"]

    # 7. Test Admin Access
    user_db.role = "admin"
    db.commit()

    res_admin_ok = client.get("/api/v1/admin/stats", headers=headers)
    assert res_admin_ok.status_code == 200
    assert "model_performance" in res_admin_ok.json()

    print("ALL DIRECT AUTH & SECURITY INTEGRATION TESTS PASSED CLEANLY!")
