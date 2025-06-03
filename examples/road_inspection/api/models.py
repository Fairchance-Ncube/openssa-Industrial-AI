"""Database models used by the road inspection API."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Integer, String, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class RoadStatus(str, Enum):
    """Enumerates the possible lifecycle states for a road segment."""

    ACTIVE = "Active"
    NEEDS_REPAIR = "Needs Repair"
    UNDER_REPAIR = "Under Repair"
    ARCHIVED = "Archived"


class Priority(str, Enum):
    """Represents the priority level assigned to a segment."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RoadSegment(Base):
    """Table storing inspection information for individual road segments."""

    __tablename__ = "road_segments"

    # Unique identifier for the segment. ``uuid.uuid4`` is used to generate a
    # random UUID when new rows are inserted.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Human readable name or location label for the segment.
    name = Column(String, nullable=False)

    # Spatial geometry for the road segment.  For simplicity this is stored as a
    # WKT string, but could be swapped out for PostGIS types in a real project.
    geometry = Column(String, nullable=False)

    # Condition index produced by an ML model.  Lower values indicate poorer
    # quality.
    road_condition_index = Column(Integer, nullable=False)

    # List of damage types detected on the segment.
    damage_types = Column(JSON, nullable=False, default=list)

    # Timestamp for the last inspection event.  Defaults to the row creation
    # time.
    last_inspection = Column(DateTime, default=datetime.utcnow)

    # Derived priority level used for alerting and sorting.
    priority = Column(Enum(Priority), nullable=False, default=Priority.LOW)

    # Current operational state of the segment.
    status = Column(Enum(RoadStatus), nullable=False, default=RoadStatus.ACTIVE)
