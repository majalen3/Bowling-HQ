from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BowlingBall(BaseModel):
    id: UUID
    brand: str
    name: str
    coverstock_type: str
    core_type: str
    rg: Optional[float] = None
    differential: Optional[float] = None
    hook_potential: Optional[int] = None
    length: Optional[int] = None
    backend: Optional[int] = None
    oil_condition: Optional[str] = None
    weight_options: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class ArsenalItem(BaseModel):
    id: UUID
    ball_id: UUID
    purchase_date: Optional[date]
    layout: Optional[str]
    notes: Optional[str]
    games_played: int
    added_at: datetime
    ball: BowlingBall


class ArsenalAddRequest(BaseModel):
    ball_id: UUID
    purchase_date: Optional[date] = None
    layout: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
