from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PatternInput(BaseModel):
    name: Optional[str] = None
    length_ft: float = Field(ge=30.0, le=52.0)
    volume_ml: float = Field(ge=5.0, le=60.0)
    asymmetry_index: float = Field(default=0.0, ge=0.0, le=1.0)
    front_oil_pct: float = Field(default=0.34, ge=0.0, le=1.0)
    mid_oil_pct: float = Field(default=0.33, ge=0.0, le=1.0)
    backend_oil_pct: float = Field(default=0.33, ge=0.0, le=1.0)
    lane_surface: str = "synthetic"


class BowlerInput(BaseModel):
    average: int = Field(ge=0, le=300)
    speed_mph: float = Field(ge=8.0, le=25.0)
    rev_rate: int = Field(ge=0, le=800)
    axis_rotation_deg: float = Field(default=45.0, ge=0.0, le=90.0)
    axis_tilt_deg: float = Field(default=15.0, ge=0.0, le=90.0)
    consistency: float = Field(default=0.75, ge=0.0, le=1.0)


class RecommendationRequest(BaseModel):
    pattern: PatternInput
    bowler: BowlerInput
    top_n: int = Field(default=3, ge=1, le=10)
    session_id: Optional[UUID] = None


class BallRecommendation(BaseModel):
    rank: int
    ball_id: Optional[UUID] = None
    ball_name: str
    fit_score: float
    confidence: float
    matched_shape: str
    reasoning: list[str]
    breakpoint_board: float
    entry_angle_deg: float
    strike_probability: float


class RecommendationResponse(BaseModel):
    pattern_difficulty_score: float
    pattern_difficulty_label: str
    breakpoint_board: float
    recommendations: list[BallRecommendation]
    bowler_type: str
    session_id: Optional[UUID] = None
