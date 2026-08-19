import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.api import api_router
from backend.app.services.ml_service import load_ml_artifacts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("disaster_risk_api")

def auto_migrate_schema():
    """Applies schema migrations for User authentication & prediction tracking."""
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            inspector = inspect(engine)
            if "users" in inspector.get_table_names():
                cols = [c["name"] for c in inspector.get_columns("users")]
                if "is_verified" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0 NOT NULL;"))
                if "is_active" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL;"))
                if "failed_login_attempts" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0 NOT NULL;"))
                if "locked_until" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN locked_until DATETIME;"))
                if "last_login_at" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at DATETIME;"))
                if "updated_at" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN updated_at DATETIME;"))

            if "prediction_records" in inspector.get_table_names():
                cols = [c["name"] for c in inspector.get_columns("prediction_records")]
                if "user_id" not in cols:
                    conn.execute(text("ALTER TABLE prediction_records ADD COLUMN user_id INTEGER;"))
            conn.commit()
    except Exception as e:
        logger.warning(f"Auto-migration note: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Initializing & synchronizing database tables...")
    auto_migrate_schema()

    logger.info("Pre-loading ML model binaries & SHAP explainers...")
    load_ml_artifacts()

    yield
    # Shutdown tasks
    logger.info("Application shutdown completed.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade AI Multi-Disaster Risk Prediction & Early Warning System API",
    version="3.1.0",
    lifespan=lifespan
)

# Configure CORS Middleware BEFORE Security Headers & Routes
cors_origins = settings.get_cors_origins()
logger.info(f"Configuring CORS middleware with allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

app.include_router(api_router)

@app.get("/")
def root_index():
    return {
        "title": settings.PROJECT_NAME,
        "status": "Online",
        "version": "3.1.0",
        "docs_url": "/docs",
        "health_check": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
