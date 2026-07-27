from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GameCreate(BaseModel):
    session_id: UUID
    scores: list[int] = Field(min_length=1)


class GameItem(BaseModel):
    id: UUID
    session_id: UUID
    game_number: int
    score: int
    created_at: datetime


class GamesResponse(BaseModel):
    session_id: UUID
    games: list[GameItem]
    count: int
    average: float


class FrameItem(BaseModel):
    id: UUID
    game_id: UUID
    frame_number: int
    ball1: int
    ball2: Optional[int]
    ball3: Optional[int]
    is_strike: bool
    is_spare: bool


class FramesResponse(BaseModel):
    game_id: UUID
    frames: list[FrameItem]


class GameFromThrowsRequest(BaseModel):
    """Record a game by entering individual throw values (0-10 each)."""

    throws: list[int] = Field(
        min_length=12,
        max_length=21,
        description=(
            "Throws in order. Minimum 12 (perfect game), "
            "maximum 21 (all spares / strikes in 10th)."
        ),
    )
