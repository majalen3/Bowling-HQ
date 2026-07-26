from datetime import datetime
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
