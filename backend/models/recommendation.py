from pydantic import BaseModel
from typing import Optional, Any


class AlternativeBall(BaseModel):
    ball_id: int
    ball_name: str
    confidence: float
    reason: str


class RecommendationRequest(BaseModel):
    center_id: Optional[int] = None
    pattern_id: int
    session_type: str = "league"  # 'league' | 'tournament' | 'practice' | 'open'
    user_id: int = 1


class RecommendationResponse(BaseModel):
    ball_id: int
    ball_name: str
    brand: str
    confidence_score: float
    reason: str
    alternatives: list[AlternativeBall]
    pattern_name: str
    pattern_difficulty: int
    tip: Optional[str] = None
