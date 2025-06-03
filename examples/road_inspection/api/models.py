from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .database import Base


class RoadStatus(str, Enum):
    ACTIVE = "Active"
    NEEDS_REPAIR = "Needs Repair"
    UNDER_REPAIR = "Under Repair"
    ARCHIVED = "Archived"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    geometry = Column(String, nullable=False)
    road_condition_index = Column(Integer, nullable=False)
    damage_types = Column(JSON, nullable=False, default=list)
    last_inspection = Column(DateTime, default=datetime.utcnow)
    priority = Column(Enum(Priority), nullable=False, default=Priority.LOW)
    status = Column(Enum(RoadStatus), nullable=False, default=RoadStatus.ACTIVE)
