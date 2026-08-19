from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime

class LocationSearchItem(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    admin1: Optional[str] = None

class EnvironmentalData(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    surface_pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    rainfall_1h: Optional[float] = None
    rainfall_3h: Optional[float] = None
    rainfall_6h: Optional[float] = None
    rainfall_12h: Optional[float] = None
    rainfall_24h: Optional[float] = None
    rainfall_3d: Optional[float] = None
    rainfall_7d: Optional[float] = None
    elevation: Optional[float] = None
    status: str = "Live data retrieved from Open-Meteo"

class FeatureFactor(BaseModel):
    feature: str
    importance_score: float
    shap_value: float
    direction: str
    input_value: float

class HazardRiskDetail(BaseModel):
    disaster_type: str
    risk_percentage: float
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    validation_status: str  # Validated or Experimental / Limited validation
    top_factors: List[FeatureFactor]

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = "Selected Location"

class WhatIfRequest(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = "Simulated Location"
    simulated_rainfall_change_pct: float = 0.0
    simulated_temp_change_celsius: float = 0.0
    simulated_humidity_change_pct: float = 0.0
    simulated_wind_change_pct: float = 0.0

class PrimaryRiskSummary(BaseModel):
    primary_hazard: str
    risk_level: str
    risk_percentage: float
    warning_advice: str

class PredictionResponse(BaseModel):
    id: Optional[int] = None
    location_name: str
    latitude: float
    longitude: float
    primary_risk: PrimaryRiskSummary
    environmental_data: EnvironmentalData
    disaster_risks: Dict[str, HazardRiskDetail]
    timestamp: str
    disclaimer: str
    is_simulation: bool = False

class AdminStatsResponse(BaseModel):
    total_predictions: int
    high_risk_predictions: int
    critical_risk_predictions: int
    locations_analyzed: int
    hazard_distribution: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
    model_performance: Dict[str, Any]

# --- Authentication & User Management Schemas ---

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str
    confirm_password: str
    captcha_token: Optional[str] = None

class OTPVerifyRequest(BaseModel):
    email: str
    otp: str = Field(..., min_length=6, max_length=6)
    purpose: str = "registration"  # "registration" or "password_reset"

class OTPResendRequest(BaseModel):
    email: str
    purpose: str = "registration"
    captcha_token: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str
    captcha_token: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: str
    captcha_token: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str
    confirm_password: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_verified: bool = False
    is_active: bool = True
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None

class PredictionHistoryItem(BaseModel):
    id: int
    location_name: str
    latitude: float
    longitude: float
    primary_risk: str
    primary_level: str
    primary_probability: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True
