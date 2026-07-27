from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.arsenal import BallItem

LineupRole = str  # 'primary', 'secondary', 'tertiary', 'spare'


class LineupCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    pattern_name: Optional[str] = Field(default=None, max_length=255)


class LineupBallAddRequest(BaseModel):
    ball_id: UUID
    slot_order: int = Field(ge=1)
    rationale: Optional[str] = None


class LineupBall(BaseModel):
    id: UUID
    ball_id: UUID
    slot_order: int
    rationale: Optional[str]
    ball: BallItem


class TournamentLineup(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    pattern_name: Optional[str]
    created_at: datetime


class TournamentLineupDetail(TournamentLineup):
    balls: list[LineupBall] = []


class LineupRecommendation(BaseModel):
    ball_id: UUID
    slot_order: int
    role: str
    reasoning: str
    ball: BallItem
