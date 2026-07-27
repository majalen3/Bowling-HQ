from __future__ import annotations

from uuid import UUID

from src.models.arsenal import BallItem
from src.models.commander import (
    BallRecommendation,
    CommanderRequest,
    CommanderResponse,
)
from src.services.arsenal import (
    get_arsenal_repository,
    get_settings,
    list_balls_catalog,
)
from src.services.session_progress import DEMO_USER_ID

# Surface grit thresholds for oil-condition matching.
# Lower grit = more friction = suited for heavier oil.
_GRIT_OIL_MAP = {
    "very_heavy": (80, 1000),
    "heavy": (1000, 2000),
    "medium": (2000, 3000),
    "light": (3000, 3500),
    "dry": (3500, 4000),
}

# Differential thresholds for hook-potential categorisation.
_DIFF_THRESHOLDS = {
    "low": 0.025,
    "medium": 0.045,
}


def _oil_score(surface_grit: int, lane_condition: str) -> tuple[int, str]:
    lo, hi = _GRIT_OIL_MAP.get(lane_condition, (2000, 3000))
    if lo <= surface_grit <= hi:
        return 40, f"Surface grit {surface_grit} is ideal for {lane_condition.replace('_', ' ')} conditions."
    distance = min(abs(surface_grit - lo), abs(surface_grit - hi))
    score = max(0, 40 - int(distance / 200) * 5)
    return score, (
        f"Surface grit {surface_grit} is {distance} away from the ideal range "
        f"for {lane_condition.replace('_', ' ')} conditions."
    )


def _release_score(differential: float, release_style: str) -> tuple[int, str]:
    # Map differential to hook potential: controlled→low, balanced→medium, power→high
    if release_style == "controlled":
        target = _DIFF_THRESHOLDS["low"]
    elif release_style == "balanced":
        target = _DIFF_THRESHOLDS["medium"]
    else:
        target = 0.060
    distance = abs(differential - target)
    score = max(0, 20 - int(distance * 400))
    return score, (
        f"Differential {differential:.3f} fits a {release_style} release "
        f"(target ~{target:.3f})."
    )


def _length_score(rg: float, ball_speed: float) -> tuple[int, str]:
    # Higher rg = longer arcing shape → suits faster speeds.
    # Target rg range: ~2.40 (slow) to ~2.60 (fast, 22 mph)
    SPEED_FLOOR = 10.0
    target_rg = 2.40 + max(0.0, (ball_speed - SPEED_FLOOR) / 100.0)
    target_rg = min(2.62, target_rg)
    distance = abs(rg - target_rg)
    score = max(0, 20 - int(distance * 400))
    return score, (
        f"RG {rg:.3f} pairs with a {ball_speed:.1f} mph release "
        f"(target ~{target_rg:.3f})."
    )


def _pattern_score(mass_bias: float, pattern_difficulty: int) -> tuple[int, str]:
    # Higher mass bias → asymmetric core → better for harder patterns.
    if mass_bias > 0.010:
        score = 10 + pattern_difficulty * 2.5
        label = "asymmetric"
    else:
        score = 20 - pattern_difficulty * 2.5
        label = "symmetric"
    score = max(0, min(20, round(score)))
    return score, (
        f"{label.capitalize()} core (mass bias {mass_bias:.3f}) matched to "
        f"difficulty level {pattern_difficulty}/4."
    )


def _score_ball(ball: BallItem, request: CommanderRequest) -> tuple[int, str]:
    oil_pts, oil_reason = _oil_score(ball.surface_grit, request.lane_condition)
    release_pts, release_reason = _release_score(
        ball.differential, request.release_style,
    )
    length_pts, length_reason = _length_score(ball.rg, request.ball_speed)
    pattern_pts, pattern_reason = _pattern_score(
        ball.mass_bias, request.pattern_difficulty,
    )
    total = oil_pts + release_pts + length_pts + pattern_pts
    reasoning = " ".join([oil_reason, release_reason, length_reason, pattern_reason])
    return total, reasoning


def recommend(
    request: CommanderRequest,
    user_id: UUID = DEMO_USER_ID,
) -> CommanderResponse:
    repo = get_arsenal_repository()
    arsenal_balls = repo.list_arsenal(user_id)
    from_arsenal = bool(arsenal_balls)

    scored: list[tuple[int, str, BallItem, UUID | None]] = []
    if from_arsenal:
        for entry in arsenal_balls:
            ball = entry.ball
            score, reasoning = _score_ball(ball, request)
            scored.append((score, reasoning, ball, entry.id))
    else:
        for ball in list_balls_catalog():
            score, reasoning = _score_ball(ball, request)
            scored.append((score, reasoning, ball, None))

    scored.sort(key=lambda item: item[0], reverse=True)
    if not from_arsenal:
        scored = scored[:3]

    roles = ["primary", "alternative", "backup"]
    recommendations = []
    for index, (score, reasoning, ball, arsenal_id) in enumerate(scored):
        role = roles[index] if index < len(roles) else "backup"
        confidence = max(1, min(100, score))
        recommendations.append(
            BallRecommendation(
                role=role,
                confidence=confidence,
                reasoning=reasoning,
                ball=ball,
                arsenal_id=arsenal_id,
            ),
        )

    return CommanderResponse(from_arsenal=from_arsenal, recommendations=recommendations)
