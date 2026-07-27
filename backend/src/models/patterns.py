from pydantic import BaseModel, Field

from src.models.recommendations import PatternInput


class PatternAnalysisRequest(BaseModel):
    pattern: PatternInput


class PatternAnalysisResponse(BaseModel):
    pattern_name: str
    difficulty_score: float = Field(ge=1.0, le=10.0)
    difficulty_label: str
    breakpoint_board: float = Field(ge=1.0, le=39.0)
    transition_risk: str
    transition_rate: float = Field(ge=0.0, le=1.0)
    guidance: list[str]
