"""Pydantic schemas for request and response models."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from .models import Priority, RoadStatus


class RoadSegmentBase(BaseModel):
    """Shared properties across create and update operations."""

    # Human readable segment name or location label
    name: str
    # Geometry string (e.g. WKT or GeoJSON)
    geometry: str
    # ML-derived quality index, enforced between 0 and 100 by Pydantic
    road_condition_index: int = Field(ge=0, le=100)
    # Types of damage found on the segment
    damage_types: List[str]
    # Timestamp of the last inspection
    last_inspection: Optional[datetime] = None
    # Operational status of the segment
    status: Optional[RoadStatus] = RoadStatus.ACTIVE


class RoadSegmentCreate(RoadSegmentBase):
    pass


class RoadSegmentUpdate(BaseModel):
    """Fields that can be modified for an existing segment."""

    name: Optional[str] = None
    geometry: Optional[str] = None
    road_condition_index: Optional[int] = Field(default=None, ge=0, le=100)
    damage_types: Optional[List[str]] = None
    last_inspection: Optional[datetime] = None
    status: Optional[RoadStatus] = None


class RoadSegmentOut(RoadSegmentBase):
    """Representation used in API responses."""

    id: UUID
    priority: Priority
    status: RoadStatus

    class Config:
        orm_mode = True
