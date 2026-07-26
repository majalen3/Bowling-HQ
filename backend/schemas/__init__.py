"""Pydantic schemas (request/response) for the Bowling-HQ API."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# ─── Shared config ────────────────────────────────────────────────────────────

class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ─── Bowling Ball ─────────────────────────────────────────────────────────────

class BowlingBallOut(_ORM):
    id: uuid.UUID
    brand: str
    name: str
    weight_oz: float
    core_type: str
    rg_min: float | None
    differential: float | None
    coverstock_type: str
    finish: str | None
    release_year: int | None
    best_conditions: str
    hook_potential: float | None
    length_score: float | None
    backend_score: float | None
    notes: str | None
    created_at: datetime


# ─── Lane Pattern ─────────────────────────────────────────────────────────────

class LanePatternOut(_ORM):
    id: uuid.UUID
    name: str
    pattern_type: str
    oil_volume: str
    length_feet: int | None
    difficulty_score: float | None
    description: str | None
    created_at: datetime


# ─── Bowling Center ───────────────────────────────────────────────────────────

class BowlingCenterOut(_ORM):
    id: uuid.UUID
    name: str
    city: str | None
    state: str | None
    country: str
    lanes_count: int | None
    rating: float | None
    notes: str | None


# ─── Arsenal ─────────────────────────────────────────────────────────────────

class ArsenalEntryOut(_ORM):
    id: uuid.UUID
    user_id: uuid.UUID
    ball_id: uuid.UUID
    ball: BowlingBallOut
    layout: str | None
    purchase_date: date | None
    games_thrown: int
    is_retired: bool
    personal_notes: str | None


# ─── Sessions ────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    center_id: uuid.UUID | None = None
    pattern_id: uuid.UUID | None = None
    session_type: str = "practice"
    session_date: date
    duration_min: int | None = None
    notes: str | None = None


class GameCreate(BaseModel):
    lane_number: int | None = None
    primary_ball_id: uuid.UUID | None = None
    total_score: int | None = None
    strike_count: int = 0
    spare_count: int = 0
    open_count: int = 0
    game_number: int = 1


class GameOut(_ORM):
    id: uuid.UUID
    session_id: uuid.UUID
    lane_number: int | None
    primary_ball_id: uuid.UUID | None
    total_score: int | None
    strike_count: int
    spare_count: int
    open_count: int
    game_number: int
    created_at: datetime


class SessionOut(_ORM):
    id: uuid.UUID
    user_id: uuid.UUID
    center_id: uuid.UUID | None
    pattern_id: uuid.UUID | None
    session_type: str
    session_date: date
    duration_min: int | None
    notes: str | None
    created_at: datetime
    games: list[GameOut] = []


# ─── Commander AI Recommendations ─────────────────────────────────────────────

class RecommendationRequest(BaseModel):
    user_id: uuid.UUID
    pattern_id: uuid.UUID | None = None
    session_type: str = "practice"
    oil_volume: str | None = None   # override if pattern unknown
    length_feet: int | None = None  # override if pattern unknown


class AlternativeBall(BaseModel):
    ball: BowlingBallOut
    reason: str


class RecommendationOut(BaseModel):
    recommended_ball: BowlingBallOut
    confidence: float
    reason: str
    strategy: str
    alternatives: list[AlternativeBall]
    pattern: LanePatternOut | None
    raw_scores: dict[str, Any]
