from typing import Literal

from pydantic import BaseModel

Trend = Literal["improving", "consistent", "declining"]
PerformanceTier = Literal["beginner", "intermediate", "advanced", "expert"]


class SessionTypeBreakdown(BaseModel):
    session_type: str
    count: int


class GhostBowlerProfile(BaseModel):
    average_score: float
    high_game: int
    total_games: int
    total_sessions: int
    sessions_by_type: list[SessionTypeBreakdown]
    trend: Trend
    predicted_next_game: float
    consistency_score: int
    performance_tier: PerformanceTier
