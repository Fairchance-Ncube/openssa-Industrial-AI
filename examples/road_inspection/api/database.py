"""Database utilities for the road inspection API."""

import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string for PostgreSQL database.  This value comes from the
# environment so that this example can be easily configured without
# hardcoding credentials.
DATABASE_URL = os.getenv("DATABASE_URL")

# Flag indicating whether the database should be used.  If the connection
# fails for any reason we fall back to JSON storage and this flag is set to
# ``False``.
USE_DB = True

# Global SQLAlchemy objects; these are initialised only when a connection is
# successfully established.
engine = None
SessionLocal = None
Base = declarative_base()

# Attempt to create a database engine if a connection string has been
# provided.  This is wrapped in a ``try`` block so that if the database is not
# yet available (for example during local development) the application will
# gracefully degrade to using a JSON file for persistence.
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        # Simple connectivity check so we can fall back to JSON if the DB is
        # unreachable.
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception:  # pragma: no cover - fallback logic
        USE_DB = False
else:
    USE_DB = False

# Location of the JSON file used when the database is not reachable.
JSON_DATA_FILE = os.path.join(os.path.dirname(__file__), "road_segments.json")

if not USE_DB:
    # Inform the user that the application is operating in offline mode so they
    # are aware data will not be persisted to a database.
    print("Database not available, falling back to JSON storage.")


def get_db():
    """Provide a database session to path operations.

    When running without a database (``USE_DB`` is ``False``) this yields
    ``None`` so the CRUD layer knows to operate on the JSON file instead.
    """

    if not USE_DB:
        return None

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
