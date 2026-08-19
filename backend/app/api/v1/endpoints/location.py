from fastapi import APIRouter, Query
from typing import List
from backend.app.models.schemas import LocationSearchItem
from backend.app.services.weather_service import search_locations

router = APIRouter()

@router.get("/location/search", response_model=List[LocationSearchItem])
async def search_location_endpoint(query: str = Query(..., min_length=2, description="City or region name to search")):
    results = await search_locations(query)
    return results
