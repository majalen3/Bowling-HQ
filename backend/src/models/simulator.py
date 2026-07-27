from pydantic import BaseModel, Field

from src.models.recommendations import BowlerInput, PatternInput


class SimulatorBallInput(BaseModel):
    name: str
    coverstock: str
    rg: float = Field(ge=2.40, le=2.65)
    differential: float = Field(ge=0.0, le=0.08)
    mass_bias: float = Field(default=0.0, ge=0.0, le=0.08)
    surface_grit: int = Field(default=3000, ge=80, le=4000)


class SimulatorRequest(BaseModel):
    pattern: PatternInput
    bowler: BowlerInput
    ball: SimulatorBallInput


class SimulatorResponse(BaseModel):
    predicted_score: int = Field(ge=0, le=300)
    confidence_low: int = Field(ge=0, le=300)
    confidence_high: int = Field(ge=0, le=300)
    strike_probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    breakpoint_board: float = Field(ge=1.0, le=39.0)
    entry_angle_deg: float = Field(ge=0.0, le=10.0)
    notes: list[str]
