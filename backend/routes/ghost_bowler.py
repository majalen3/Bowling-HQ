from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.postgres import get_db
from constants import DEFAULT_USER_ID

router = APIRouter(prefix="/ghost-bowler", tags=["Ghost Bowler"])


@router.get("/profile")
def get_profile(user_id: int = DEFAULT_USER_ID, db: Session = Depends(get_db)):
    """Return the Ghost Bowler profile summary for a user."""
    user = db.execute(
        text("SELECT * FROM users WHERE id = :uid"), {"uid": user_id}
    ).fetchone()

    if user is None:
        return {
            "message": (
                "No profile found. Start recording sessions to build your Ghost Bowler profile."
            )
        }

    # Compute basic performance metrics from historical sessions
    stats = db.execute(
        text("""
            SELECT
                COUNT(DISTINCT s.id)   AS total_sessions,
                COUNT(g.id)            AS total_games,
                AVG(g.score)           AS avg_score,
                MAX(g.score)           AS high_game,
                MIN(g.score)           AS low_game
            FROM bowling_sessions s
            LEFT JOIN games g ON g.session_id = s.id
            WHERE s.user_id = :uid
        """),
        {"uid": user_id},
    ).fetchone()

    return {
        "user": dict(user._mapping),
        "performance": {
            "total_sessions": stats.total_sessions or 0,
            "total_games": stats.total_games or 0,
            "avg_score": round(float(stats.avg_score), 1) if stats.avg_score else None,
            "high_game": stats.high_game,
            "low_game": stats.low_game,
        },
        "status": "active" if (stats.total_games or 0) >= 10 else "building",
        "message": (
            "Ghost Bowler profile active — enough data to generate predictions."
            if (stats.total_games or 0) >= 10
            else f"Keep bowling! {max(0, 10 - (stats.total_games or 0))} more games needed"
            " to activate Ghost Bowler predictions."
        ),
    }
