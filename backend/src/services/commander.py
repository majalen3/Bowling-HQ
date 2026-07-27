from __future__ import annotations

from uuid import UUID

from src.models.arsenal import BowlingBall
from src.models.commander import (
    BallRecommendation,
    CommanderRequest,
    CommanderResponse,
)
from src.services.arsenal import get_arsenal_with_balls, list_catalog

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

_OIL_ORDER = ["dry", "light", "medium", "heavy", "very_heavy"]

# Recreational-to-competitive ball speeds span roughly 10-22 mph, and
# length ratings run from 1 (early) to 10 (long). These constants map
# that speed range onto the rating scale so faster speeds target a
# longer ball, avoiding an over/under reaction early on the lane.
BALL_SPEED_FLOOR_MPH = 10
SPEED_TO_LENGTH_DIVISOR = 1.2
MAX_LENGTH_RATING = 10


def _oil_score(ball_oil: str | None, lane_condition: str) -> tuple[int, str]:
    if not ball_oil:
        return 20, "No oil rating on file, treated as a neutral option."
    if ball_oil == "any":
        return (
            35,
            "Versatile spare-friendly coverstock works across conditions.",
        )
    if ball_oil == lane_condition:
        return (
            40,
            (
                "Built for exactly this "
                f"{lane_condition.replace('_', ' ')} condition."
            ),
        )
    try:
        ball_index = _OIL_ORDER.index(ball_oil)
        lane_index = _OIL_ORDER.index(lane_condition)
        distance = abs(ball_index - lane_index)
    except ValueError:
        return 15, "Unrecognized oil rating, scored conservatively."
    score = max(0, 40 - distance * 12)
    return score, (
        f"Rated for {ball_oil.replace('_', ' ')}, "
        f"{distance} step(s) from the "
        f"{lane_condition.replace('_', ' ')} condition."
    )


def _release_score(
    hook_potential: int | None,
    release_style: str,
) -> tuple[int, str]:
    hook = hook_potential if hook_potential is not None else 5
    target = {"controlled": 3, "balanced": 6, "power": 9}[release_style]
    distance = abs(hook - target)
    score = max(0, 20 - distance * 3)
    return score, (
        f"Hook potential {hook}/10 fits a {release_style} release "
        f"(target ~{target})."
    )


def _length_score(length: int | None, ball_speed: float) -> tuple[int, str]:
    ball_length = length if length is not None else 5
    # Faster ball speeds benefit from more length to avoid over/under
    # reacting early. See the module-level constants for the mapping.
    target_length = min(
        MAX_LENGTH_RATING,
        max(
            1,
            round(
                (ball_speed - BALL_SPEED_FLOOR_MPH)
                / SPEED_TO_LENGTH_DIVISOR,
            ),
        ),
    )
    distance = abs(ball_length - target_length)
    score = max(0, 20 - distance * 3)
    return score, (
        f"Length rating {ball_length}/10 pairs with a "
        f"{ball_speed:.1f} mph release (target ~{target_length})."
    )


def _pattern_score(
    core_type: str | None,
    pattern_difficulty: int,
) -> tuple[int, str]:
    # Harder patterns reward stronger, asymmetrical cores; easier ones
    # favor symmetrical.
    if core_type == "asymmetrical":
        score = 10 + pattern_difficulty * 2.5
    else:
        score = 20 - pattern_difficulty * 2.5
    score = max(0, min(20, round(score)))
    return score, (
        f"{(core_type or 'unknown').capitalize()} core matched to "
        f"difficulty level {pattern_difficulty}/4."
    )


def _score_ball(
    ball: BowlingBall,
    request: CommanderRequest,
) -> tuple[int, str]:
    oil_pts, oil_reason = _oil_score(
        ball.oil_condition,
        request.lane_condition,
    )
    release_pts, release_reason = _release_score(
        ball.hook_potential, request.release_style,
    )
    length_pts, length_reason = _length_score(ball.length, request.ball_speed)
    pattern_pts, pattern_reason = _pattern_score(
        ball.core_type, request.pattern_difficulty,
    )
    total = oil_pts + release_pts + length_pts + pattern_pts
    reasoning = " ".join(
        [oil_reason, release_reason, length_reason, pattern_reason],
    )
    return total, reasoning


def recommend(
    request: CommanderRequest,
    user_id: UUID = DEFAULT_USER_ID,
) -> CommanderResponse:
    arsenal_rows = get_arsenal_with_balls(user_id=user_id)
    from_arsenal = bool(arsenal_rows)

    scored: list[tuple[int, str, BowlingBall, UUID | None]] = []
    if from_arsenal:
        for row in arsenal_rows:
            ball = BowlingBall(
                id=row["ball_id"],
                brand=row["brand"],
                name=row["name"],
                coverstock_type=row["coverstock_type"],
                core_type=row["core_type"],
                rg=row["rg"],
                differential=row["differential"],
                hook_potential=row["hook_potential"],
                length=row["length"],
                backend=row["backend"],
                oil_condition=row["oil_condition"],
                weight_options=row["weight_options"],
                description=row["description"],
                created_at=row["ball_created_at"],
            )
            score, reasoning = _score_ball(ball, request)
            scored.append((score, reasoning, ball, row["id"]))
    else:
        for ball in list_catalog():
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

    return CommanderResponse(
        from_arsenal=from_arsenal,
        recommendations=recommendations,
    )
