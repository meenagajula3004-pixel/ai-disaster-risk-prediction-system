-- Database Initialization Script for AI Multi-Disaster Risk Prediction System

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    country VARCHAR(100),
    state VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS environmental_observations (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    surface_pressure DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    rainfall_24h DOUBLE PRECISION,
    rainfall_7d DOUBLE PRECISION,
    elevation DOUBLE PRECISION,
    data_source VARCHAR(100) DEFAULT 'Open-Meteo API',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prediction_records (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    primary_risk VARCHAR(50) NOT NULL,
    primary_level VARCHAR(50) NOT NULL,
    primary_probability DOUBLE PRECISION NOT NULL,
    flood_risk_json JSONB,
    landslide_risk_json JSONB,
    cyclone_risk_json JSONB,
    heatwave_risk_json JSONB,
    drought_risk_json JSONB,
    environmental_json JSONB,
    disclaimer TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    level VARCHAR(50) DEFAULT 'INFO',
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
