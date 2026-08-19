import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Multi-Disaster Risk Prediction & Early Warning System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./disaster_risk.db"
    USE_SQLITE_FALLBACK: bool = True

    # Auth & Security
    SECRET_KEY: str = "dev-secret-key-disaster-risk-ai-system-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # SMTP / Email Service Configuration
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@ai-disaster-risk.org"
    SMTP_TLS: bool = True

    # CAPTCHA Configuration
    CAPTCHA_SITE_KEY: str = ""
    CAPTCHA_SECRET_KEY: str = ""

    # External Data Services
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OPEN_METEO_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1"

    # CORS Allowed Origins Configuration (Supports ALLOWED_ORIGINS, CORS_ORIGINS, or CORS_ORIGIN env vars)
    ALLOWED_ORIGINS: str = (
        "https://ai-disaster-risk-prediction-system.vercel.app,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:4173,"
        "http://127.0.0.1:4173"
    )
    CORS_ORIGINS: str = ""
    CORS_ORIGIN: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        raw_origins = self.CORS_ORIGINS or self.CORS_ORIGIN or self.ALLOWED_ORIGINS
        parsed = [origin.strip().rstrip('/') for origin in raw_origins.split(",") if origin.strip()]
        
        default_origins = [
            "https://ai-disaster-risk-prediction-system.vercel.app",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:4173",
            "http://127.0.0.1:4173"
        ]
        
        for d in default_origins:
            if d not in parsed:
                parsed.append(d)
        return parsed

settings = Settings()
