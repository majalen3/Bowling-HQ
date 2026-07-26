"""
Commander AI — Rule-Based Ball Recommendation Engine

Scores each active ball in the arsenal against the given pattern's
characteristics and returns a ranked list of recommendations.

Scoring rubric (0-100 scale):
  - Oil volume match   : up to 38 pts  (coverstock vs. oil_volume)
  - Pattern length     : up to 28 pts  (finish vs. oil_length bucket)
  - Core type bonus    : up to  8 pts  (asym on hard, sym on easy)
  - RG / differential  : up to 10 pts  (fine-tune for oil extremes)
  - Session type adj.  :       +4 pts  (tournament + high-hook bonus)
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as DBSession

# ---------------------------------------------------------------------------
# Named constants
# ---------------------------------------------------------------------------

# Confidence score bounds (displayed 0-100 scale).
# 30 = floor so even a poor match shows a meaningful number.
# 97 = ceiling reserved for when real performance data is integrated.
MIN_CONFIDENCE_SCORE: float = 30.0
MAX_CONFIDENCE_SCORE: float = 97.0

# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

# (oil_volume) -> score per coverstock_type
_COVER_OIL_SCORE: dict[str, dict[str, int]] = {
    "very_heavy": {
        "pearl_reactive":  38,
        "hybrid_reactive": 32,
        "reactive_resin":  28,
        "urethane":         8,
        "plastic":         -20,
    },
    "heavy": {
        "reactive_resin":  38,
        "hybrid_reactive": 35,
        "pearl_reactive":  30,
        "urethane":        10,
        "plastic":         -20,
    },
    "medium": {
        "hybrid_reactive": 38,
        "reactive_resin":  35,
        "pearl_reactive":  28,
        "urethane":        18,
        "plastic":         -15,
    },
    "light": {
        "urethane":        38,
        "pearl_reactive":  30,
        "hybrid_reactive": 22,
        "reactive_resin":  15,
        "plastic":          8,
    },
}

# (length_bucket) -> score per finish type
_FINISH_LENGTH_SCORE: dict[str, dict[str, int]] = {
    "short": {            # < 36 ft — earlier hook needed
        "500_grit":  28,
        "1000_grit": 18,
        "2000_grit":  8,
        "4000_grit":  0,
        "polished":  -15,
    },
    "medium": {           # 36-42 ft — balanced
        "1000_grit": 28,
        "2000_grit": 25,
        "500_grit":  15,
        "4000_grit": 15,
        "polished":  10,
    },
    "long": {             # > 42 ft — longer skid required
        "polished":  28,
        "4000_grit": 22,
        "2000_grit": 15,
        "1000_grit":  5,
        "500_grit":  -10,
    },
}

_DIFFICULTY_TIP: dict[int, str] = {
    1: "House shot — your benchmark ball is a safe, high-confidence choice.",
    2: "Sport-style conditions — match your ball to the oil volume and play straighter.",
    3: "Challenging pattern — trust the data; small miss-hits are penalized.",
    4: "Elite-level pattern — precision and your strongest equipment are mandatory.",
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _length_bucket(oil_length_ft: int) -> str:
    """Bucket an oil length in feet into 'short', 'medium', or 'long'."""
    if oil_length_ft < 36:
        return "short"
    if oil_length_ft <= 42:
        return "medium"
    return "long"


def _score_ball(ball_row, oil_volume: str, length_bucket: str, difficulty: int, session_type: str) -> float:
    """
    Return a confidence score in [MIN_CONFIDENCE_SCORE, MAX_CONFIDENCE_SCORE] for
    one ball against the given lane conditions.

    Scoring components:
      1. Oil volume vs. coverstock type  (up to 38 pts)
      2. Pattern length vs. ball finish  (up to 28 pts)
      3. Core type bonus for difficulty  (up to  8 pts)
      4. RG / differential fine-tune     (up to 10 pts)
      5. Tournament session boost        (       +4 pts)
    """
    score = 0.0

    # 1. Oil volume vs coverstock
    cover = (ball_row.coverstock_type or "").lower()
    oil_map = _COVER_OIL_SCORE.get(oil_volume, _COVER_OIL_SCORE["medium"])
    score += oil_map.get(cover, 5)

    # 2. Pattern length vs finish
    finish = (ball_row.finish or "").lower()
    len_map = _FINISH_LENGTH_SCORE.get(length_bucket, _FINISH_LENGTH_SCORE["medium"])
    score += len_map.get(finish, 5)

    # 3. Core type bonus for pattern difficulty
    core = (ball_row.core_type or "").lower()
    if difficulty >= 3 and core == "asymmetrical":
        score += 8
    elif difficulty <= 2 and core == "symmetrical":
        score += 5

    # 4. RG / differential fine-tuning
    rg = float(ball_row.rg or 2.50)
    diff = float(ball_row.differential or 0.035)
    if oil_volume in ("heavy", "very_heavy"):
        if rg < 2.48:
            score += 5
        if diff > 0.048:
            score += 5
    elif oil_volume == "light":
        if rg > 2.52:
            score += 5

    # 5. Tournament context — boost high-hook-potential balls slightly
    if session_type == "tournament" and (ball_row.hook_potential or 5) >= 8:
        score += 4

    return round(min(MAX_CONFIDENCE_SCORE, max(MIN_CONFIDENCE_SCORE, score)), 1)


def _build_reason(ball_row, oil_volume: str, length_bucket: str, difficulty: int) -> str:
    """Compose a plain-English explanation for why this ball was recommended."""
    cover_labels = {
        "pearl_reactive":  "pearl reactive coverstock (long skid + angular backend)",
        "hybrid_reactive": "hybrid reactive coverstock (balanced motion)",
        "reactive_resin":  "reactive resin coverstock (controllable hook)",
        "urethane":        "urethane coverstock (smooth, controllable arc)",
        "plastic":         "plastic coverstock",
    }
    cover = (ball_row.coverstock_type or "unknown").lower()
    finish = (ball_row.finish or "unknown").lower()
    core = (ball_row.core_type or "unknown").lower()

    parts = [
        f"{ball_row.brand} {ball_row.name} features a {cover_labels.get(cover, cover)}",
        f"finished at {finish.replace('_', ' ')} for a {'longer' if 'polished' in finish else 'earlier'} breakpoint",
        f"with a {core} core (RG {ball_row.rg}, diff {ball_row.differential})",
    ]
    if oil_volume in ("heavy", "very_heavy"):
        parts.append("ideal for the heavier oil volume on this pattern")
    elif oil_volume == "light":
        parts.append("well-suited to the lighter oil volume on this pattern")
    else:
        parts.append("a solid match for medium oil conditions")

    return " — ".join(parts) + "."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_recommendation(db: "DBSession", pattern_id: int, session_type: str, user_id: int) -> dict[str, Any]:
    """
    Query the database for the given pattern and all active non-spare balls,
    score every ball against the pattern conditions, and return the best pick
    plus up to three ranked alternatives.

    Returns a dict compatible with RecommendationResponse:
      {ball_id, ball_name, brand, confidence_score, reason,
       alternatives, pattern_name, pattern_difficulty, tip}
    """
    from sqlalchemy import text

    # Fetch pattern
    pattern_row = db.execute(
        text("SELECT * FROM patterns WHERE id = :pid"),
        {"pid": pattern_id},
    ).fetchone()

    if pattern_row is None:
        raise ValueError(f"Pattern id {pattern_id} not found")

    oil_volume = pattern_row.oil_volume or "medium"
    oil_length = int(pattern_row.oil_length_ft or 38)
    difficulty = int(pattern_row.difficulty or 2)
    length_bucket = _length_bucket(oil_length)

    # Fetch active, non-spare balls
    balls = db.execute(
        text("SELECT * FROM balls WHERE active = TRUE AND is_spare_ball = FALSE ORDER BY id"),
    ).fetchall()

    if not balls:
        raise ValueError("No active balls found in the arsenal")

    # Score every ball and sort descending
    scored: list[tuple[float, Any, str]] = sorted(
        [(
            _score_ball(ball, oil_volume, length_bucket, difficulty, session_type),
            ball,
            _build_reason(ball, oil_volume, length_bucket, difficulty),
        ) for ball in balls],
        key=lambda x: x[0],
        reverse=True,
    )

    best_score, best_ball, best_reason = scored[0]

    alternatives = [
        {
            "ball_id":   row.id,
            "ball_name": f"{row.brand} {row.name}",
            "confidence": s,
            "reason":     r,
        }
        for s, row, r in scored[1:4]  # top 3 alternatives
    ]

    return {
        "ball_id":            best_ball.id,
        "ball_name":          f"{best_ball.brand} {best_ball.name}",
        "brand":              best_ball.brand,
        "confidence_score":   best_score,
        "reason":             best_reason,
        "alternatives":       alternatives,
        "pattern_name":       pattern_row.name,
        "pattern_difficulty": difficulty,
        "tip":                _DIFFICULTY_TIP.get(difficulty),
    }
