from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.arsenal import BowlingBall

Strategy = Literal["conservative", "versatile", "aggressive", "defensive"]
LineupRole = Literal["primary", "secondary", "tertiary", "spare"]


class LineupCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    tournament_name: Optional[str] = Field(default=None, max_length=200)
    pattern_id: Optional[UUID] = None
    strategy: Optional[Strategy] = None
    notes: Optional[str] = None


class LineupBallAddRequest(BaseModel):
    user_arsenal_id: UUID
    role: LineupRole
    notes: Optional[str] = None


class LineupBall(BaseModel):
    id: UUID
    user_arsenal_id: UUID
    role: LineupRole
    order_index: int
    notes: Optional[str]
    ball: BowlingBall


class TournamentLineup(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    tournament_name: Optional[str]
    pattern_id: Optional[UUID]
    strategy: Optional[str]
    notes: Optional[str]
    created_at: datetime


class TournamentLineupDetail(TournamentLineup):
    balls: list[LineupBall] = []


class LineupRecommendation(BaseModel):
    user_arsenal_id: UUID
    role: LineupRole
    reasoning: str
    ball: BowlingBall
