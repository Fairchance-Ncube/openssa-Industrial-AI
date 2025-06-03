"""Minimal FastAPI application exposing road segment management APIs."""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database import Base, engine, USE_DB, get_db
from .models import RoadSegment
from .schemas import RoadSegmentCreate, RoadSegmentOut, RoadSegmentUpdate
from .crud import (
    get_segments,
    get_segment,
    create_segment,
    update_segment,
    delete_segment,
    alert_segments,
)

app = FastAPI()

# Create database tables on startup when a PostgreSQL database is configured.
if USE_DB and engine is not None:
    Base.metadata.create_all(bind=engine)


@app.get("/road-segments", response_model=list[RoadSegmentOut])
def list_segments(db: Session = Depends(get_db)):
    """Return every road segment in storage."""

    return get_segments(db)


@app.get("/road-segments/{segment_id}", response_model=RoadSegmentOut)
def get_single_segment(segment_id: str, db: Session = Depends(get_db)):
    """Fetch a specific road segment by ID."""

    segment = get_segment(db, segment_id)
    if not segment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return segment


@app.post("/road-segments", response_model=RoadSegmentOut, status_code=status.HTTP_201_CREATED)
def create_new_segment(segment: RoadSegmentCreate, db: Session = Depends(get_db)):
    """Create a new road segment."""

    return create_segment(db, segment)


@app.put("/road-segments/{segment_id}", response_model=RoadSegmentOut)
def update_existing_segment(segment_id: str, updates: RoadSegmentUpdate, db: Session = Depends(get_db)):
    """Update an existing road segment."""

    seg = update_segment(db, segment_id, updates)
    if not seg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return seg


@app.delete("/road-segments/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_segment(segment_id: str, db: Session = Depends(get_db)):
    """Delete a road segment."""

    success = delete_segment(db, segment_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return None


@app.get("/road-segments/alerts", response_model=list[RoadSegmentOut])
def get_alerts(db: Session = Depends(get_db)):
    """Return only segments with a high priority."""

    return alert_segments(db)
