from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from .models import Priority, RoadStatus


class RoadSegmentBase(BaseModel):
    name: str
    geometry: str
    road_condition_index: int = Field(ge=0, le=100)
    damage_types: List[str]
    last_inspection: Optional[datetime] = None
    status: Optional[RoadStatus] = RoadStatus.ACTIVE


class RoadSegmentCreate(RoadSegmentBase):
    pass


class RoadSegmentUpdate(BaseModel):
    name: Optional[str] = None
    geometry: Optional[str] = None
    road_condition_index: Optional[int] = Field(default=None, ge=0, le=100)
    damage_types: Optional[List[str]] = None
    last_inspection: Optional[datetime] = None
    status: Optional[RoadStatus] = None


class RoadSegmentOut(RoadSegmentBase):
    id: UUID
    priority: Priority
    status: RoadStatus

    class Config:
        orm_mode = True
