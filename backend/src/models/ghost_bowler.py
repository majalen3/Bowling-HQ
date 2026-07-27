from pydantic import BaseModel, Field


class ConditionBaseline(BaseModel):
    condition_family: str
    game_count: int = Field(ge=0)
    average_score: float = Field(ge=0.0, le=300.0)
    score_band_low: int = Field(ge=0, le=300)
    score_band_high: int = Field(ge=0, le=300)
    strike_rate: float = Field(ge=0.0, le=1.0)
    spare_rate: float = Field(ge=0.0, le=1.0)
    open_frame_rate: float = Field(ge=0.0, le=1.0)


class GhostBowlerBaselineResponse(BaseModel):
    total_games: int = Field(ge=0)
    overall: ConditionBaseline
    by_condition: list[ConditionBaseline]


class GhostBowlerCompareResponse(BaseModel):
    condition_family: str
    baseline_average: float = Field(ge=0.0, le=300.0)
    current_average: float = Field(ge=0.0, le=300.0)
    delta: float
    trend: str
