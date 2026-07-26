from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.postgres import get_db
from models.recommendation import RecommendationRequest, RecommendationResponse
from services.commander_engine import get_recommendation

router = APIRouter(prefix="/commander", tags=["Commander AI"])


@router.post("/opening-ball", response_model=RecommendationResponse)
def recommend_opening_ball(req: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Return the best opening-ball recommendation for the given pattern and session type.
    """
    try:
        result = get_recommendation(
            db=db,
            pattern_id=req.pattern_id,
            session_type=req.session_type,
            user_id=req.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return result


@router.get("/patterns")
def list_patterns_for_commander(db: Session = Depends(get_db)):
    """List all patterns available for recommendation queries."""
    rows = db.execute(
        text(
            "SELECT id, name, pattern_type, oil_volume, oil_length_ft, difficulty"
            " FROM patterns ORDER BY difficulty, name"
        )
    ).fetchall()
    return [dict(r._mapping) for r in rows]
