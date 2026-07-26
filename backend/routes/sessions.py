from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date

from database.postgres import get_db
from models.session import Session as SessionModel, SessionCreate

router = APIRouter(prefix="/sessions", tags=["Sessions"])

DEFAULT_USER = 1


@router.get("/", response_model=list[SessionModel])
def list_sessions(user_id: int = DEFAULT_USER, db: Session = Depends(get_db)):
    """Return all sessions for a user."""
    rows = db.execute(
        text("SELECT * FROM bowling_sessions WHERE user_id = :uid ORDER BY session_date DESC"),
        {"uid": user_id},
    ).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{session_id}", response_model=SessionModel)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Return a single session."""
    row = db.execute(
        text("SELECT * FROM bowling_sessions WHERE id = :id"), {"id": session_id}
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return dict(row._mapping)


@router.post("/", response_model=SessionModel, status_code=201)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Record a new bowling session."""
    row = db.execute(
        text("""
            INSERT INTO bowling_sessions
              (user_id, center_id, pattern_id, session_type, session_date, total_games, notes)
            VALUES
              (:user_id, :center_id, :pattern_id, :session_type, :session_date, :total_games, :notes)
            RETURNING *
        """),
        session.model_dump(),
    ).fetchone()
    db.commit()
    return dict(row._mapping)


@router.get("/{session_id}/games")
def get_session_games(session_id: int, db: Session = Depends(get_db)):
    """Return all games for a session."""
    rows = db.execute(
        text("SELECT * FROM games WHERE session_id = :sid ORDER BY game_number"),
        {"sid": session_id},
    ).fetchall()
    return [dict(r._mapping) for r in rows]
