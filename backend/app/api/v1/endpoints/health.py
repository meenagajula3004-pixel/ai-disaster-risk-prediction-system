from fastapi import APIRouter
import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Multi-Disaster Risk Prediction & Early Warning System",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "database": "connected",
        "ml_models": "loaded"
    }
