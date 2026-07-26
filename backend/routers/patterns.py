"""Lane patterns and bowling centers endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import BowlingCenter, LanePattern
from schemas import BowlingCenterOut, LanePatternOut

router = APIRouter(prefix="/patterns", tags=["patterns"])
centers_router = APIRouter(prefix="/centers", tags=["centers"])


# ─── Lane Patterns ────────────────────────────────────────────────────────────

@router.get("", response_model=list[LanePatternOut])
async def list_patterns(
    pattern_type: str | None = None,
    oil_volume: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(LanePattern).order_by(LanePattern.name)
    if pattern_type:
        stmt = stmt.where(LanePattern.pattern_type == pattern_type)
    if oil_volume:
        stmt = stmt.where(LanePattern.oil_volume == oil_volume)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{pattern_id}", response_model=LanePatternOut)
async def get_pattern(pattern_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    pattern = await db.get(LanePattern, pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern


# ─── Bowling Centers ──────────────────────────────────────────────────────────

@centers_router.get("", response_model=list[BowlingCenterOut])
async def list_centers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BowlingCenter).order_by(BowlingCenter.name))
    return result.scalars().all()


@centers_router.get("/{center_id}", response_model=BowlingCenterOut)
async def get_center(center_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    center = await db.get(BowlingCenter, center_id)
    if not center:
        raise HTTPException(status_code=404, detail="Center not found")
    return center
