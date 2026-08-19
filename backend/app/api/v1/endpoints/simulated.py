import datetime
from fastapi import APIRouter
from backend.app.models.schemas import WhatIfRequest, PredictionResponse
from backend.app.services.weather_service import fetch_live_environmental_data
from backend.app.services.ml_service import predict_multi_disaster_risk

router = APIRouter()

SIMULATION_DISCLAIMER = (
    "SIMULATION ONLY — NOT A LIVE FORECAST. "
    "This calculation represents hypothetical risk sensitivity based on user-modified environmental inputs."
)

@router.post("/predict/what-if", response_model=PredictionResponse)
async def simulate_what_if_prediction(req: WhatIfRequest):
    # 1. Fetch live base metrics
    env_data = await fetch_live_environmental_data(req.latitude, req.longitude)

    modifiers = {
        "simulated_rainfall_change_pct": req.simulated_rainfall_change_pct,
        "simulated_temp_change_celsius": req.simulated_temp_change_celsius,
        "simulated_humidity_change_pct": req.simulated_humidity_change_pct,
        "simulated_wind_change_pct": req.simulated_wind_change_pct
    }

    # 2. Run simulation inference
    primary_summary, disaster_risks = predict_multi_disaster_risk(env_data, simulated_modifiers=modifiers)

    # 3. Update env_data representation to show modified metrics
    sim_env = dict(env_data)
    if "rainfall_24h" in sim_env and sim_env["rainfall_24h"] is not None:
        sim_env["rainfall_24h"] = round(sim_env["rainfall_24h"] * (1.0 + req.simulated_rainfall_change_pct / 100.0), 2)
    if "temperature" in sim_env and sim_env["temperature"] is not None:
        sim_env["temperature"] = round(sim_env["temperature"] + req.simulated_temp_change_celsius, 2)
    sim_env["status"] = "Hypothetical Simulation Values Applied"

    return {
        "id": 0,
        "location_name": f"{req.location_name} (Simulation)",
        "latitude": req.latitude,
        "longitude": req.longitude,
        "primary_risk": primary_summary,
        "environmental_data": sim_env,
        "disaster_risks": disaster_risks,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "disclaimer": SIMULATION_DISCLAIMER,
        "is_simulation": True
    }
