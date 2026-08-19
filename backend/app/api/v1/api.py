from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    location,
    weather,
    predict,
    simulated,
    history,
    admin,
    auth
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(location.router, prefix="/api/v1", tags=["Location"])
api_router.include_router(weather.router, prefix="/api/v1", tags=["Weather"])
api_router.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
api_router.include_router(simulated.router, prefix="/api/v1", tags=["Simulation"])
api_router.include_router(history.router, prefix="/api/v1", tags=["History"])
api_router.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
api_router.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
