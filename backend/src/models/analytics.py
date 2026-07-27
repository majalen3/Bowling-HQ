from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ScoreTrendPoint(BaseModel):
    session_id: UUID
    date: datetime
    average: float
    game_count: int
    high_game: int
    location_name: Optional[str] = None


class BallAverage(BaseModel):
    ball_id: UUID
    ball_name: str
    average: float
    game_count: int


class AnalyticsSummary(BaseModel):
    overall_average: float
    high_game: int
    total_games: int
    total_sessions: int
    recent_trend: list[ScoreTrendPoint]
    per_ball_averages: list[BallAverage]
