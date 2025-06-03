"""CRUD helpers for the road inspection API."""

import json
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from .database import USE_DB, JSON_DATA_FILE
from .models import RoadSegment, Priority, RoadStatus
from .schemas import RoadSegmentCreate, RoadSegmentUpdate


def _compute_priority_and_status(index: int, status: Optional[RoadStatus]) -> tuple[Priority, RoadStatus]:
    """Derive priority and status values based on the condition index."""

    if index < 50:
        return Priority.HIGH, RoadStatus.NEEDS_REPAIR
    if index < 75:
        return Priority.MEDIUM, status or RoadStatus.ACTIVE
    return Priority.LOW, status or RoadStatus.ACTIVE


# JSON fallback helpers

def _load_json() -> List[dict]:
    """Load road segment records from the JSON fallback file."""

    with open(JSON_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(data: List[dict]) -> None:
    """Persist road segment records to the JSON fallback file."""

    with open(JSON_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


# CRUD operations

def get_segments(db: Session) -> List[RoadSegment]:
    """Return all known road segments."""

    if USE_DB:
        return db.query(RoadSegment).all()
    return [RoadSegment(**item) for item in _load_json()]


def get_segment(db: Session, segment_id: str) -> Optional[RoadSegment]:
    """Retrieve a single segment by its identifier."""

    if USE_DB:
        return db.query(RoadSegment).filter(RoadSegment.id == segment_id).first()

    items = _load_json()
    for item in items:
        if item["id"] == segment_id:
            return RoadSegment(**item)
    return None


def create_segment(db: Session, segment: RoadSegmentCreate) -> RoadSegment:
    """Insert a new road segment record."""

    priority, status = _compute_priority_and_status(segment.road_condition_index, segment.status)

    if USE_DB:
        db_obj = RoadSegment(
            id=uuid.uuid4(),
            name=segment.name,
            geometry=segment.geometry,
            road_condition_index=segment.road_condition_index,
            damage_types=segment.damage_types,
            last_inspection=segment.last_inspection,
            priority=priority,
            status=status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    items = _load_json()
    db_obj = {
        "id": str(uuid.uuid4()),
        "name": segment.name,
        "geometry": segment.geometry,
        "road_condition_index": segment.road_condition_index,
        "damage_types": segment.damage_types,
        "last_inspection": segment.last_inspection.isoformat() if segment.last_inspection else None,
        "priority": priority.value,
        "status": status.value,
    }
    items.append(db_obj)
    _write_json(items)
    return RoadSegment(**db_obj)


def update_segment(db: Session, segment_id: str, updates: RoadSegmentUpdate) -> Optional[RoadSegment]:
    """Modify an existing segment."""

    if USE_DB:
        db_obj = db.query(RoadSegment).filter(RoadSegment.id == segment_id).first()
        if not db_obj:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)

        if updates.road_condition_index is not None:
            db_obj.priority, db_obj.status = _compute_priority_and_status(
                updates.road_condition_index, updates.status or db_obj.status
            )

        db.commit()
        db.refresh(db_obj)
        return db_obj

    items = _load_json()
    for item in items:
        if item["id"] == segment_id:
            data = updates.model_dump(exclude_unset=True)
            item.update(data)
            index = item.get("road_condition_index")
            if index is not None:
                prio, stat = _compute_priority_and_status(index, RoadStatus(item.get("status", "Active")))
                item["priority"] = prio.value
                item["status"] = stat.value
            _write_json(items)
            return RoadSegment(**item)

    return None


def delete_segment(db: Session, segment_id: str) -> bool:
    """Remove a segment from storage."""

    if USE_DB:
        obj = db.query(RoadSegment).filter(RoadSegment.id == segment_id).first()
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

    items = _load_json()
    new_items = [item for item in items if item["id"] != segment_id]
    if len(new_items) == len(items):
        return False
    _write_json(new_items)
    return True


def alert_segments(db: Session) -> List[RoadSegment]:
    """Return segments flagged as high priority."""

    if USE_DB:
        return db.query(RoadSegment).filter(RoadSegment.priority == Priority.HIGH).all()

    return [RoadSegment(**item) for item in _load_json() if item.get("priority") == Priority.HIGH.value]
