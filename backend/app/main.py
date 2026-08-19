import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.api import api_router
from backend.app.services.ml_service import load_ml_artifacts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("disaster_risk_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Database table creation skipped: {e}")

    logger.info("Pre-loading ML model binaries & SHAP explainers...")
    load_ml_artifacts()

    yield
    # Shutdown tasks
    logger.info("Application shutdown completed.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade AI Multi-Disaster Risk Prediction & Early Warning System API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root_index():
    return {
        "title": settings.PROJECT_NAME,
        "status": "Online",
        "docs_url": "/docs",
        "health_check": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
