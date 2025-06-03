import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
USE_DB = True
engine = None
SessionLocal = None
Base = declarative_base()

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception:  # pragma: no cover - fallback logic
        USE_DB = False
else:
    USE_DB = False

JSON_DATA_FILE = os.path.join(os.path.dirname(__file__), "road_segments.json")

if not USE_DB:
    print("Database not available, falling back to JSON storage.")


def get_db():
    if not USE_DB:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
