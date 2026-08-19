# AI Multi-Disaster Risk Prediction & Early Warning System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.3.6-38BDF8.svg)](https://tailwindcss.com/)

A production-grade Machine Learning and Full-Stack Web Application designed for **Multi-Disaster Risk Prediction & Early Warning**.

The platform automatically retrieves real-time environmental weather metrics and elevation profiles for any location globally, evaluating risk levels, probabilities, and **SHAP Explainable AI** feature contributions across **5 distinct natural disaster hazards**:
1. 🌊 **Flood Risk**
2. ⛰️ **Landslide Risk**
3. 🌀 **Cyclone / Severe Storm Risk** *(Tagged as Experimental / Limited validation)*
4. ☀️ **Heatwave Risk**
5. 🏜️ **Drought Risk**

> **Live Demo**: `[Deployment URL will be added after deployment]`

---

## 🌟 Key Features

* 📍 **Automatic Location & Environmental Sourcing**: User selects a location via search autocomplete, clicking on the map, or clicking "Detect My Location". Live weather (Temperature, Humidity, Pressure, Wind, 1h to 7-day Rainfall windows) and Elevation are auto-fetched from Open-Meteo APIs.
* 📊 **100% Data Transparency**: Raw environmental measurements are visually displayed to the user alongside evaluated hazard risk cards.
* 🚨 **Primary Risk Highlight**: Highlights the highest-severity hazard with early warning advice (LOW / MODERATE / HIGH / CRITICAL).
* 🧠 **Explainable AI (SHAP)**: Interactive SHAP TreeExplainer feature attribution charts detailing top positive (risk-increasing) and negative factors for every prediction.
* 🔮 **What-If Climate Simulator**: Interactive slider controls allowing users to adjust rainfall (+%), temperature (+°C), humidity (+%), or wind (+%) and observe simulated multi-hazard risk shifts with explicit `"SIMULATION ONLY"` disclaimers.
* 🗺️ **Interactive Spatial Map**: Powered by Leaflet + OpenStreetMap displaying selected pins and spatial risk intensity circles.
* 📈 **Admin Analytics Dashboard**: System statistics, hazard distribution pie charts, model comparison matrices, and prediction logs.

---

## 🏗️ Technology Architecture

```
React 18 + Vite Frontend  ──────>  Python FastAPI Backend  ──────>  Open-Meteo APIs
(Tailwind, Leaflet, Recharts)      (Async Engine, CORS, Auth)        (Weather & Elevation)
                                            │
                                  ┌─────────┴─────────┐
                                  ▼                   ▼
                           ML Model Binaries    PostgreSQL / SQLite
                           (Scikit-Learn, SHAP)   (Prediction History)
```

---

## 📊 Machine Learning Model Comparison Results

Candidates evaluated: **Logistic Regression**, **Random Forest**, **XGBoost / Gradient Boosting**.  
Validation Strategy: **Time-Aware Chronological Split (70% Train, 15% Val, 15% Test)** to eliminate temporal data leakage.

| Disaster Module | Candidate Models | Selected Model | Accuracy | High-Risk Recall | ROC-AUC | Validation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **🌊 Flood Risk** | LogReg, RF, XGBoost | **GradientBoosting** | 97.44% | 92.11% | 0.9974 | Validated |
| **⛰️ Landslide Risk** | LogReg, RF, XGBoost | **LogisticRegression** | 98.44% | 96.32% | 0.9996 | Validated |
| **🌀 Cyclone / Storm** | LogReg, RF, XGBoost | **LogisticRegression** | 97.44% | 98.48% | 0.9994 | Experimental / Limited validation |
| **☀️ Heatwave Risk** | LogReg, RF, XGBoost | **LogisticRegression** | 97.33% | 97.24% | 0.9983 | Validated |
| **🏜️ Drought Risk** | LogReg, RF, XGBoost | **GradientBoosting** | 96.00% | 96.27% | 0.9985 | Validated |

> **Selection Criteria**: Evaluated with composite score `Composite = (HighRiskRecall * 0.50) + (ROCAUC * 0.30) + (F1 * 0.20)` prioritizing High-Risk Recall to ensure critical events are never missed.

---

## 📁 Repository Structure

```text
ai-disaster-risk-prediction-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # Health, Location, Weather, Predict, Simulated, History, Admin, Auth
│   │   ├── core/                 # Config & Database Session
│   │   ├── models/               # DB Models & Pydantic Schemas
│   │   ├── services/             # WeatherService, MLService, SHAPService
│   │   └── main.py               # FastAPI entrypoint
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/           # Navbar, Footer, LocationSearch, PrimaryRiskBanner, DisasterRiskCards, RiskMap, SHAPExplainerWidget, WhatIfSimulator, AdminDashboard
│   │   ├── pages/                # DashboardPage
│   │   ├── services/             # Axios API Client
│   │   └── App.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── ml/
│   ├── train.py                  # Reproducible training & selection script
│   ├── preprocess.py             # Preprocessing & Time-Aware Validation split
│   ├── evaluate.py               # Evaluation metrics
│   ├── explain.py                # SHAP feature attribution
│   ├── metrics/                  # Comparison JSON reports
│   └── models/                   # Serialized best_models.joblib
├── data/
│   ├── raw/                      # Hydrometeorological benchmark data
│   └── download_datasets.py      # Dataset compilation script
├── database/
│   ├── init.sql                  # PostgreSQL initialization schema
│   └── schema.md
├── docs/                         # Architecture, ML Pipeline, API & Data Sources documentation
├── tests/                        # Pytest suite for ML, API endpoints, and Database
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start & Local Installation

### Prerequisites
* Python 3.11+
* Node.js v18+ & npm
* Docker Desktop *(Optional for containerized run)*

### 1. Backend & ML Setup
```bash
# Navigate to project root
cd ai-disaster-risk-prediction-system

# Create virtual environment & install requirements
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# Run ML Training pipeline to generate model binaries
python ml/train.py

# Start FastAPI Server
uvicorn backend.app.main:app --reload --port 8000
```
FastAPI documentation will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
# Open a new terminal in frontend/
cd frontend

# Install Node dependencies
npm install

# Start Vite Development Server
npm run dev
```
Dashboard will open at `http://localhost:5173`.

---

## 🐳 Docker Deployment

To run the complete application stack (Frontend, FastAPI Backend, PostgreSQL Database) locally with Docker Compose:

```bash
docker-compose up --build -d
```
- React Frontend: `http://localhost:5173`
- FastAPI Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

---

## 🧪 Testing

Run backend & ML test suite:
```bash
pytest tests/
```

Verify frontend build:
```bash
cd frontend && npm run build
```

---

## ⚠️ Important Safety & Accuracy Disclaimer

> **This application provides AI-based multi-disaster risk estimation for educational and decision-support purposes. It does not replace official government weather, disaster management, or emergency warnings.**  
> For real-world emergencies, users should follow official local government emergency authorities.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
