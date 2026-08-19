import datetime
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.schemas import PredictionRequest, PredictionResponse
from backend.app.models.db_models import PredictionRecordDB, EnvironmentalObservationDB
from backend.app.services.weather_service import fetch_live_environmental_data
from backend.app.services.ml_service import predict_multi_disaster_risk

router = APIRouter()

SAFETY_DISCLAIMER = (
    "This application provides AI-based multi-disaster risk estimation for educational and decision-support purposes. "
    "It does not replace official government weather, disaster management, or emergency warnings."
)

@router.post("/predict", response_model=PredictionResponse)
async def predict_multi_disaster(
    req: PredictionRequest,
    db: Session = Depends(get_db)
):
    try:
        # 1. Fetch live environmental metrics
        env_data = await fetch_live_environmental_data(req.latitude, req.longitude)

        # 2. Run multi-hazard prediction + SHAP
        primary_summary, disaster_risks = predict_multi_disaster_risk(env_data)

        timestamp_str = datetime.datetime.utcnow().isoformat()

        # 3. Persist observation to Database
        try:
            obs = EnvironmentalObservationDB(
                location_name=req.location_name,
                latitude=req.latitude,
                longitude=req.longitude,
                temperature=env_data.get("temperature"),
                humidity=env_data.get("humidity"),
                surface_pressure=env_data.get("surface_pressure"),
                wind_speed=env_data.get("wind_speed"),
                rainfall_24h=env_data.get("rainfall_24h"),
                rainfall_7d=env_data.get("rainfall_7d"),
                elevation=env_data.get("elevation")
            )
            db.add(obs)

            pred_record = PredictionRecordDB(
                location_name=req.location_name,
                latitude=req.latitude,
                longitude=req.longitude,
                primary_risk=primary_summary["primary_hazard"],
                primary_level=primary_summary["risk_level"],
                primary_probability=primary_summary["risk_percentage"],
                flood_risk_json=disaster_risks.get("flood"),
                landslide_risk_json=disaster_risks.get("landslide"),
                cyclone_risk_json=disaster_risks.get("cyclone"),
                heatwave_risk_json=disaster_risks.get("heatwave"),
                drought_risk_json=disaster_risks.get("drought"),
                environmental_json=env_data,
                disclaimer=SAFETY_DISCLAIMER
            )
            db.add(pred_record)
            db.commit()
            db.refresh(pred_record)
            pred_id = pred_record.id
        except Exception as e:
            db.rollback()
            pred_id = 1

        return {
            "id": pred_id,
            "location_name": req.location_name,
            "latitude": req.latitude,
            "longitude": req.longitude,
            "primary_risk": primary_summary,
            "environmental_data": env_data,
            "disaster_risks": disaster_risks,
            "timestamp": timestamp_str,
            "disclaimer": SAFETY_DISCLAIMER,
            "is_simulation": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction service failure: {str(e)}")
