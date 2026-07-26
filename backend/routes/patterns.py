from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.postgres import get_db
from models.pattern import Pattern, PatternCreate

router = APIRouter(prefix="/patterns", tags=["Patterns"])


@router.get("/", response_model=list[Pattern])
def list_patterns(db: Session = Depends(get_db)):
    """Return all patterns."""
    rows = db.execute(
        text("SELECT * FROM patterns ORDER BY difficulty, name")
    ).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{pattern_id}", response_model=Pattern)
def get_pattern(pattern_id: int, db: Session = Depends(get_db)):
    """Return a single pattern by ID."""
    row = db.execute(
        text("SELECT * FROM patterns WHERE id = :id"), {"id": pattern_id}
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return dict(row._mapping)


@router.post("/", response_model=Pattern, status_code=201)
def create_pattern(pattern: PatternCreate, db: Session = Depends(get_db)):
    """Add a new lane pattern."""
    row = db.execute(
        text("""
            INSERT INTO patterns (name, pattern_type, oil_volume, oil_length_ft, difficulty, description, notes)
            VALUES (:name, :pattern_type, :oil_volume, :oil_length_ft, :difficulty, :description, :notes)
            RETURNING *
        """),
        pattern.model_dump(),
    ).fetchone()
    db.commit()
    return dict(row._mapping)
