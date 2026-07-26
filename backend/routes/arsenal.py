from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.postgres import get_db
from models.ball import Ball, BallCreate

router = APIRouter(prefix="/arsenal", tags=["Arsenal"])


@router.get("/", response_model=list[Ball])
def list_balls(active_only: bool = True, db: Session = Depends(get_db)):
    """Return all balls in the arsenal."""
    query = "SELECT * FROM balls"
    if active_only:
        query += " WHERE active = TRUE"
    query += " ORDER BY is_spare_ball, brand, name"
    rows = db.execute(text(query)).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{ball_id}", response_model=Ball)
def get_ball(ball_id: int, db: Session = Depends(get_db)):
    """Return a single ball by ID."""
    row = db.execute(text("SELECT * FROM balls WHERE id = :id"), {"id": ball_id}).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Ball not found")
    return dict(row._mapping)


@router.post("/", response_model=Ball, status_code=201)
def add_ball(ball: BallCreate, db: Session = Depends(get_db)):
    """Add a new ball to the arsenal."""
    row = db.execute(
        text("""
            INSERT INTO balls
              (name, brand, weight_lbs, coverstock_type, core_type, rg, differential,
               finish, layout, purpose, hook_potential, length_rating, backend_rating,
               is_spare_ball, active, notes)
            VALUES
              (:name, :brand, :weight_lbs, :coverstock_type, :core_type, :rg, :differential,
               :finish, :layout, :purpose, :hook_potential, :length_rating, :backend_rating,
               :is_spare_ball, :active, :notes)
            RETURNING *
        """),
        ball.model_dump(),
    ).fetchone()
    db.commit()
    return dict(row._mapping)
