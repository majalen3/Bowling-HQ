"""Sessions and game recording endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db import get_db
from models import BowlingSession, Game
from schemas import GameCreate, GameOut, SessionCreate, SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=201)
async def create_session(
    user_id: uuid.UUID,
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    session = BowlingSession(user_id=user_id, **payload.model_dump())
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    user_id: uuid.UUID,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(BowlingSession)
        .where(BowlingSession.user_id == user_id)
        .options(selectinload(BowlingSession.games))
        .order_by(BowlingSession.session_date.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(BowlingSession)
        .where(BowlingSession.id == session_id)
        .options(selectinload(BowlingSession.games))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/{session_id}/games", response_model=GameOut, status_code=201)
async def add_game(
    session_id: uuid.UUID,
    payload: GameCreate,
    db: AsyncSession = Depends(get_db),
):
    session = await db.get(BowlingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    game = Game(session_id=session_id, **payload.model_dump())
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game
