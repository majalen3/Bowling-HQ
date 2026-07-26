"""
Commander AI — opening-ball and in-session ball recommendations.

Scoring logic:
  score(ball, context) = weighted sum of:
    - condition_match   : does ball.best_conditions match the oil volume?
    - hook_match        : hook_potential aligned with oil_volume
    - length_match      : length_score aligned with pattern length
    - backend_match     : backend_score for drier conditions
"""
from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import BowlingBall, LanePattern, UserArsenal
from schemas import (
    AlternativeBall,
    BowlingBallOut,
    LanePatternOut,
    RecommendationOut,
    RecommendationRequest,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# ─── Scoring weights ──────────────────────────────────────────────────────────

_WEIGHTS = {
    "condition_match": 0.35,
    "hook_match": 0.30,
    "length_match": 0.20,
    "backend_match": 0.15,
}

# Oil volume → ideal hook_potential range (min, max on 0–10 scale)
_OIL_HOOK_IDEAL: dict[str, tuple[float, float]] = {
    "light": (3.0, 6.5),
    "medium": (6.0, 8.0),
    "heavy": (7.5, 10.0),
    "very_heavy": (8.5, 10.0),
}

# best_conditions value that earns full condition_match score
_OIL_TO_CONDITION: dict[str, list[str]] = {
    "light": ["dry", "all"],
    "medium": ["medium", "all"],
    "heavy": ["heavy", "all"],
    "very_heavy": ["heavy", "all"],
}


def _normalise(value: float, low: float, high: float) -> float:
    """Return 0–1 how well value fits within [low, high], degrading outside."""
    if low <= value <= high:
        return 1.0
    if value < low:
        return max(0.0, 1.0 - (low - value) / low)
    return max(0.0, 1.0 - (value - high) / high)


def _score_ball(ball: BowlingBall, oil_volume: str, length_feet: int | None) -> dict[str, float]:
    oil = oil_volume.lower()

    # Condition match
    ideal_conditions = _OIL_TO_CONDITION.get(oil, ["medium"])
    condition_match = 1.0 if ball.best_conditions in ideal_conditions else 0.3

    # Hook match
    hook_low, hook_high = _OIL_HOOK_IDEAL.get(oil, (5.0, 8.0))
    hp = float(ball.hook_potential) if ball.hook_potential is not None else 5.0
    hook_match = _normalise(hp, hook_low, hook_high)

    # Length match — longer patterns prefer higher length_score
    ls = float(ball.length_score) if ball.length_score is not None else 5.0
    if length_feet is not None:
        # Patterns 40+ ft → prefer length_score 6+; shorter → prefer 5-
        ideal_ls_mid = (length_feet - 30) / 2.0  # rough mapping to 0–10
        length_match = _normalise(ls, ideal_ls_mid - 1.5, ideal_ls_mid + 1.5)
    else:
        length_match = 0.5  # neutral when unknown

    # Backend match — drier lanes reward stronger backend
    bs = float(ball.backend_score) if ball.backend_score is not None else 5.0
    if oil in ("dry", "light"):
        backend_match = _normalise(bs, 5.0, 10.0)
    elif oil in ("heavy", "very_heavy"):
        backend_match = _normalise(bs, 0.0, 6.0)
    else:
        backend_match = _normalise(bs, 4.0, 8.0)

    return {
        "condition_match": condition_match,
        "hook_match": hook_match,
        "length_match": length_match,
        "backend_match": backend_match,
    }


def _total_score(sub_scores: dict[str, float]) -> float:
    return sum(_WEIGHTS[k] * v for k, v in sub_scores.items())


def _strategy_text(oil_volume: str, ball: BowlingBall) -> str:
    oil = oil_volume.lower()
    if oil in ("heavy", "very_heavy"):
        return (
            f"Play deep (10–15 board) and let the {ball.name} read the heavy oil. "
            "Expect a smooth, controlled arc into the pocket."
        )
    if oil in ("light", "dry"):
        return (
            f"Play outside (5–10 board) with the {ball.name}. "
            "Strong backend expected — let the ball create angle through the dry."
        )
    return (
        f"Start at 15 board with the {ball.name} and adjust based on ball reaction. "
        "This medium pattern rewards a consistent release."
    )


def _reason_text(oil_volume: str, ball: BowlingBall, scores: dict[str, float]) -> str:
    best_factor = max(scores, key=lambda k: scores[k])
    labels = {
        "condition_match": "matches the oil conditions",
        "hook_match": "hook potential fits the pattern",
        "length_match": "length score suits the pattern distance",
        "backend_match": "backend motion ideal for lane friction",
    }
    return (
        f"{ball.brand} {ball.name} selected because it {labels[best_factor]}. "
        f"Overall confidence: {_total_score(scores):.0%}."
    )


# ─── Route ────────────────────────────────────────────────────────────────────

@router.post("/opening-ball", response_model=RecommendationOut)
async def recommend_opening_ball(
    payload: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Recommend the best opening-ball from a user's active arsenal
    given the pattern or oil conditions.
    """
    # 1. Resolve pattern info
    pattern: LanePattern | None = None
    if payload.pattern_id:
        pattern = await db.get(LanePattern, payload.pattern_id)
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")

    oil_volume = (
        (pattern.oil_volume if pattern else None)
        or payload.oil_volume
        or "medium"
    )
    length_feet: int | None = (
        (pattern.length_feet if pattern else None)
        or payload.length_feet
    )

    # 2. Fetch user's active arsenal with ball details
    stmt = (
        select(UserArsenal)
        .where(UserArsenal.user_id == payload.user_id)
        .where(UserArsenal.is_retired.is_(False))
    )
    result = await db.execute(stmt)
    arsenal_entries = result.scalars().all()

    if not arsenal_entries:
        # Fall back to full catalog if user has no arsenal registered
        ball_result = await db.execute(select(BowlingBall))
        balls = ball_result.scalars().all()
    else:
        ball_ids = [e.ball_id for e in arsenal_entries]
        ball_result = await db.execute(
            select(BowlingBall).where(BowlingBall.id.in_(ball_ids))
        )
        balls = ball_result.scalars().all()

    if not balls:
        raise HTTPException(status_code=404, detail="No balls available to recommend from")

    # 3. Score all balls
    scored = [
        (ball, _score_ball(ball, oil_volume, length_feet))
        for ball in balls
    ]
    scored.sort(key=lambda x: _total_score(x[1]), reverse=True)

    best_ball, best_scores = scored[0]
    confidence = round(_total_score(best_scores), 4)

    alternatives = [
        AlternativeBall(
            ball=BowlingBallOut.model_validate(b),
            reason=_reason_text(oil_volume, b, s),
        )
        for b, s in scored[1:4]  # top 3 alternatives
    ]

    return RecommendationOut(
        recommended_ball=BowlingBallOut.model_validate(best_ball),
        confidence=confidence,
        reason=_reason_text(oil_volume, best_ball, best_scores),
        strategy=_strategy_text(oil_volume, best_ball),
        alternatives=alternatives,
        pattern=LanePatternOut.model_validate(pattern) if pattern else None,
        raw_scores={
            "top_ball": {**best_scores, "total": confidence},
            "oil_volume_used": oil_volume,
            "length_feet_used": length_feet,
        },
    )
