from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BallCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    brand: str = Field(min_length=1, max_length=100)
    coverstock: str = Field(min_length=1, max_length=100)
    rg: float = Field(ge=2.40, le=2.65)
    differential: float = Field(ge=0.0, le=0.080)
    mass_bias: float = Field(default=0.0, ge=0.0, le=0.080)
    surface_grit: int = Field(default=3000, ge=80, le=4000)
    weight_lbs: int = Field(default=15, ge=12, le=16)


class BallItem(BaseModel):
    id: UUID
    name: str
    brand: str
    coverstock: str
    rg: float
    differential: float
    mass_bias: float
    surface_grit: int
    weight_lbs: int
    created_at: datetime


class UserArsenalBall(BaseModel):
    id: UUID
    ball: BallItem
    notes: Optional[str] = None
    added_at: datetime


class ArsenalResponse(BaseModel):
    user_id: UUID
    balls: list[UserArsenalBall]
    count: int


class AddBallToArsenalRequest(BaseModel):
    ball_id: UUID
    notes: Optional[str] = None


class CreateAndAddBallRequest(BallCreate):
    notes: Optional[str] = None
