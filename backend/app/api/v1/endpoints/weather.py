from fastapi import APIRouter, Query
from backend.app.models.schemas import EnvironmentalData
from backend.app.services.weather_service import fetch_live_environmental_data

router = APIRouter()

@router.get("/weather/live", response_model=EnvironmentalData)
async def get_live_weather(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude")
):
    env_data = await fetch_live_environmental_data(latitude, longitude)
    return env_data
