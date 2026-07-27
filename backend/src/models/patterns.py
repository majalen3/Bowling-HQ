from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from src.models.arsenal import BallItem


class LanePattern(BaseModel):
    id: UUID
    name: str
    length_ft: float
    volume_ml: float
    asymmetry_index: float = 0.0
    front_oil_pct: float = 0.34
    mid_oil_pct: float = 0.33
    backend_oil_pct: float = 0.33
    created_at: datetime


class LanePatternDetail(LanePattern):
    recommended_balls: list[BallItem] = []
