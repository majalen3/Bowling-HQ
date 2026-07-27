from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.models.arsenal import BowlingBall


class LanePattern(BaseModel):
    id: UUID
    name: str
    pattern_type: str
    oil_volume: Optional[int] = None
    oil_distance: Optional[int] = None
    difficulty: Optional[int] = None
    description: Optional[str] = None
    recommended_coverstock: Optional[str] = None
    recommended_hook_min: Optional[int] = None
    recommended_hook_max: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime


class LanePatternDetail(LanePattern):
    recommended_balls: list[BowlingBall] = []
