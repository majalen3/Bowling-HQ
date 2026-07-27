from pydantic import BaseModel

from src.models.ghost_bowler import GhostBowlerBaselineResponse
from src.models.patterns import PatternAnalysisResponse
from src.models.recommendations import (
    RecommendationRequest,
    RecommendationResponse,
)
from src.models.simulator import SimulatorResponse


class CommanderRequest(RecommendationRequest):
    pass


class CommanderResponse(BaseModel):
    ghost_bowler: GhostBowlerBaselineResponse
    pattern_analysis: PatternAnalysisResponse
    opening_ball: RecommendationResponse
    top_ball_simulation: SimulatorResponse | None = None
    confidence: float
    rationale: list[str]
