import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL
use_fallback = settings.USE_SQLITE_FALLBACK

# If DATABASE_URL is postgresql but fallback is allowed, test connection or prepare engine
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(db_url, connect_args=connect_args)
else:
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
    except Exception as e:
        if use_fallback:
            logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database.")
            db_url = "sqlite:///./disaster_risk.db"
            engine = create_engine(db_url, connect_args={"check_same_thread": False})
        else:
            raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
