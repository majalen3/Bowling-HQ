from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.arsenal import BallItem

LaneCondition = Literal["dry", "light", "medium", "heavy", "very_heavy"]
ReleaseStyle = Literal["controlled", "balanced", "power"]
RecommendationRole = Literal["primary", "alternative", "backup"]


class CommanderRequest(BaseModel):
    lane_condition: LaneCondition
    pattern_difficulty: int = Field(ge=1, le=4)
    ball_speed: float = Field(gt=0)
    release_style: ReleaseStyle


class BallRecommendation(BaseModel):
    role: RecommendationRole
    confidence: int
    reasoning: str
    ball: BallItem
    arsenal_id: Optional[UUID] = None


class CommanderResponse(BaseModel):
    from_arsenal: bool
    recommendations: list[BallRecommendation]
