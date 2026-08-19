import httpx
import logging
from typing import Dict, Any, List
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

async def search_locations(query: str) -> List[Dict[str, Any]]:
    """Queries Open-Meteo Geocoding API for location search & autocomplete."""
    url = f"{settings.OPEN_METEO_GEOCODING_URL}/search?name={query}&count=5&language=en&format=json"
    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                items = []
                for r in results:
                    items.append({
                        "name": r.get("name"),
                        "latitude": r.get("latitude"),
                        "longitude": r.get("longitude"),
                        "country": r.get("country", ""),
                        "admin1": r.get("admin1", "")
                    })
                return items
        except Exception as e:
            logger.error(f"Geocoding API error: {e}")
    return []

async def fetch_live_environmental_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Retrieves real-time atmospheric, precipitation window, and elevation data from Open-Meteo.
    """
    weather_url = (
        f"{settings.OPEN_METEO_BASE_URL}/forecast?"
        f"latitude={lat}&longitude={lon}&"
        "current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,precipitation&"
        "hourly=precipitation&past_days=7&forecast_days=1"
    )
    elevation_url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"

    metrics = {
        "temperature": None,
        "humidity": None,
        "surface_pressure": None,
        "wind_speed": None,
        "rainfall_1h": None,
        "rainfall_3h": None,
        "rainfall_6h": None,
        "rainfall_12h": None,
        "rainfall_24h": None,
        "rainfall_3d": None,
        "rainfall_7d": None,
        "elevation": None,
        "status": "Live data retrieved from Open-Meteo API"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(weather_url)
            if resp.status_code == 200:
                wdata = resp.json()
                current = wdata.get("current", {})
                hourly = wdata.get("hourly", {})
                precip_series = hourly.get("precipitation", [])

                metrics["temperature"] = current.get("temperature_2m")
                metrics["humidity"] = current.get("relative_humidity_2m")
                metrics["surface_pressure"] = current.get("surface_pressure")
                metrics["wind_speed"] = current.get("wind_speed_10m")

                # Accumulate rainfall windows from past 7 days (168 hours)
                if len(precip_series) >= 24:
                    recent = precip_series[-24:]
                    metrics["rainfall_1h"] = round(float(recent[-1]), 2) if recent else 0.0
                    metrics["rainfall_3h"] = round(float(sum(recent[-3:])), 2)
                    metrics["rainfall_6h"] = round(float(sum(recent[-6:])), 2)
                    metrics["rainfall_12h"] = round(float(sum(recent[-12:])), 2)
                    metrics["rainfall_24h"] = round(float(sum(recent)), 2)
                
                if len(precip_series) >= 72:
                    metrics["rainfall_3d"] = round(float(sum(precip_series[-72:])), 2)
                
                if len(precip_series) >= 168:
                    metrics["rainfall_7d"] = round(float(sum(precip_series[-168:])), 2)

        except Exception as e:
            logger.error(f"Weather API error: {e}")
            metrics["status"] = "Live weather API temporarily unavailable"

        try:
            eresp = await client.get(elevation_url)
            if eresp.status_code == 200:
                edata = eresp.json()
                elevations = edata.get("elevation", [])
                if elevations:
                    metrics["elevation"] = float(elevations[0])
        except Exception as e:
            logger.error(f"Elevation API error: {e}")

    # Default fallbacks if metrics are partially null
    if metrics["temperature"] is None:
        metrics["temperature"] = 24.5
        metrics["status"] = "Default fallback applied due to partial API response"
    if metrics["humidity"] is None:
        metrics["humidity"] = 65.0
    if metrics["surface_pressure"] is None:
        metrics["surface_pressure"] = 1012.0
    if metrics["wind_speed"] is None:
        metrics["wind_speed"] = 12.0
    if metrics["rainfall_24h"] is None:
        metrics["rainfall_24h"] = 5.0
    if metrics["rainfall_7d"] is None:
        metrics["rainfall_7d"] = 22.0
    if metrics["elevation"] is None:
        metrics["elevation"] = 45.0

    return metrics
