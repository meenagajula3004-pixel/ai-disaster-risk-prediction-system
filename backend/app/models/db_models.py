import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from backend.app.core.database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class LocationDB(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class EnvironmentalObservationDB(Base):
    __tablename__ = "environmental_observations"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    surface_pressure = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    rainfall_24h = Column(Float, nullable=True)
    rainfall_7d = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)
    data_source = Column(String(100), default="Open-Meteo API")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PredictionRecordDB(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    primary_risk = Column(String(50), nullable=False)
    primary_level = Column(String(50), nullable=False)
    primary_probability = Column(Float, nullable=False)
    flood_risk_json = Column(JSON, nullable=True)
    landslide_risk_json = Column(JSON, nullable=True)
    cyclone_risk_json = Column(JSON, nullable=True)
    heatwave_risk_json = Column(JSON, nullable=True)
    drought_risk_json = Column(JSON, nullable=True)
    environmental_json = Column(JSON, nullable=True)
    disclaimer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SystemLogDB(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    level = Column(String(50), default="INFO")
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
