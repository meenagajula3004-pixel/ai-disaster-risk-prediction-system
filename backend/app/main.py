import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.api.v1.api import api_router
from backend.app.services.ml_service import load_ml_artifacts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("disaster_risk_api")

def auto_migrate_schema():
    """Applies robust, cross-database schema migrations for SQLite and PostgreSQL."""
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            # 1. Migrate `users` table
            if "users" in tables:
                cols = [c["name"] for c in inspector.get_columns("users")]
                if "role" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';"))
                if "is_verified" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;"))
                if "is_active" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"))
                if "failed_login_attempts" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;"))
                if "locked_until" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN locked_until TIMESTAMP;"))
                if "last_login_at" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP;"))
                if "updated_at" not in cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP;"))

            # 2. Migrate `otp_records` table
            if "otp_records" in tables:
                cols = [c["name"] for c in inspector.get_columns("otp_records")]
                if "attempts" not in cols:
                    conn.execute(text("ALTER TABLE otp_records ADD COLUMN attempts INTEGER DEFAULT 0;"))
                if "is_used" not in cols:
                    conn.execute(text("ALTER TABLE otp_records ADD COLUMN is_used BOOLEAN DEFAULT FALSE;"))
                if "resend_available_at" not in cols:
                    conn.execute(text("ALTER TABLE otp_records ADD COLUMN resend_available_at TIMESTAMP;"))

            # 3. Migrate `prediction_records` table
            if "prediction_records" in tables:
                cols = [c["name"] for c in inspector.get_columns("prediction_records")]
                if "user_id" not in cols:
                    conn.execute(text("ALTER TABLE prediction_records ADD COLUMN user_id INTEGER;"))

            conn.commit()
            logger.info("Database auto-migration completed successfully.")
    except Exception as e:
        logger.error(f"Auto-migration note: {e}")
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as inner_e:
            logger.error(f"Fatal database schema creation error: {inner_e}")

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

# Global Exception Handler to ensure CORS headers on 500 Internal Server Errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    origin = request.headers.get("origin", "")
    allowed_origins = settings.get_cors_origins()
    
    headers = {}
    if origin and (origin in allowed_origins or "*" in allowed_origins):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"

    return JSONResponse(
        status_code=500,
        content={"detail": f"An internal server error occurred: {str(exc)}"},
        headers=headers
    )

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
