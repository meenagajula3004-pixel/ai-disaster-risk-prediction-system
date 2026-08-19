from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.core.database import get_db
from backend.app.models.db_models import PredictionRecordDB, EnvironmentalObservationDB

router = APIRouter()

@router.get("/history/location")
def get_location_history(
    location_name: str = Query("Selected Location"),
    db: Session = Depends(get_db)
):
    try:
        records = (
            db.query(PredictionRecordDB)
            .filter(PredictionRecordDB.location_name.ilike(f"%{location_name}%"))
            .order_by(PredictionRecordDB.created_at.desc())
            .limit(20)
            .all()
        )

        history_items = []
        for r in records:
            history_items.append({
                "id": r.id,
                "location_name": r.location_name,
                "primary_risk": r.primary_risk,
                "primary_level": r.primary_level,
                "primary_probability": r.primary_probability,
                "environmental_summary": r.environmental_json,
                "disaster_risks": {
                    "flood": r.flood_risk_json,
                    "landslide": r.landslide_risk_json,
                    "cyclone": r.cyclone_risk_json,
                    "heatwave": r.heatwave_risk_json,
                    "drought": r.drought_risk_json
                },
                "timestamp": r.created_at.isoformat() if r.created_at else ""
            })
        return history_items
    except Exception:
        return []
