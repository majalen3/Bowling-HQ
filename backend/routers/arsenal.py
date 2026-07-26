"""Arsenal endpoints — catalog of bowling balls and user arsenals."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import get_db
from models import BowlingBall, UserArsenal
from schemas import ArsenalEntryOut, BowlingBallOut

router = APIRouter(prefix="/arsenal", tags=["arsenal"])


# ─── Ball Catalog ─────────────────────────────────────────────────────────────

@router.get("/balls", response_model=list[BowlingBallOut])
async def list_balls(
    brand: str | None = None,
    conditions: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Return the full ball catalog, optionally filtered."""
    stmt = select(BowlingBall).order_by(BowlingBall.brand, BowlingBall.name)
    if brand:
        stmt = stmt.where(BowlingBall.brand.ilike(f"%{brand}%"))
    if conditions:
        stmt = stmt.where(BowlingBall.best_conditions == conditions)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/balls/{ball_id}", response_model=BowlingBallOut)
async def get_ball(ball_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    ball = await db.get(BowlingBall, ball_id)
    if not ball:
        raise HTTPException(status_code=404, detail="Ball not found")
    return ball


# ─── User Arsenal ─────────────────────────────────────────────────────────────

@router.get("/users/{user_id}", response_model=list[ArsenalEntryOut])
async def get_user_arsenal(
    user_id: uuid.UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Return a user's arsenal, joined with ball details."""
    stmt = (
        select(UserArsenal)
        .where(UserArsenal.user_id == user_id)
        .options(selectinload(UserArsenal.ball))
        .order_by(UserArsenal.created_at.desc())
    )
    if active_only:
        stmt = stmt.where(UserArsenal.is_retired.is_(False))
    result = await db.execute(stmt)
    return result.scalars().all()
