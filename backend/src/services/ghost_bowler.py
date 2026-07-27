from __future__ import annotations

import statistics
from uuid import UUID

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.ghost_bowler import (
    GhostBowlerProfile,
    SessionTypeBreakdown,
)

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

# Scales standard deviation of scores into a 1-100 consistency score. A
# stdev of 0 maps to a perfect 100; a stdev of ~66 (an unusually erratic
# bowler) maps down to the floor of 1.
CONSISTENCY_SCALE_FACTOR = 1.5


def _connection():
    return connect(get_settings().postgres_url, row_factory=dict_row)


def _empty_profile() -> GhostBowlerProfile:
    return GhostBowlerProfile(
        average_score=0,
        high_game=0,
        total_games=0,
        total_sessions=0,
        sessions_by_type=[],
        trend="consistent",
        predicted_next_game=0,
        consistency_score=0,
        performance_tier="beginner",
    )


def _performance_tier(average_score: float) -> str:
    if average_score >= 200:
        return "expert"
    if average_score >= 170:
        return "advanced"
    if average_score >= 130:
        return "intermediate"
    return "beginner"


def _trend(scores_chronological: list[int]) -> str:
    if len(scores_chronological) < 2:
        return "consistent"
    recent = scores_chronological[-10:]
    previous = scores_chronological[:-10] if len(scores_chronological) > 10 else []
    if not previous:
        midpoint = max(1, len(recent) // 2)
        previous, recent = recent[:midpoint], recent[midpoint:]
    if not previous or not recent:
        return "consistent"
    recent_avg = statistics.mean(recent)
    previous_avg = statistics.mean(previous)
    delta = recent_avg - previous_avg
    if delta > 5:
        return "improving"
    if delta < -5:
        return "declining"
    return "consistent"


def _predicted_next_game(scores_chronological: list[int]) -> float:
    recent = scores_chronological[-5:]
    if not recent:
        return 0
    weights = list(range(1, len(recent) + 1))
    weighted_sum = sum(score * weight for score, weight in zip(recent, weights))
    return round(weighted_sum / sum(weights), 1)


def _consistency_score(scores: list[int]) -> int:
    if len(scores) < 2:
        return 50 if scores else 0
    stdev = statistics.stdev(scores)
    # Typical bowling score standard deviations range roughly 0-65 for
    # recreational to advanced bowlers. Scaling by CONSISTENCY_SCALE_FACTOR
    # maps a stdev of 0 to a perfect 100 and a stdev of ~66 down to the
    # floor of 1, so the score degrades smoothly across that realistic range.
    score = max(1, min(100, round(100 - stdev * CONSISTENCY_SCALE_FACTOR)))
    return score


def get_profile(user_id: UUID = DEFAULT_USER_ID) -> GhostBowlerProfile:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT g.score, g.created_at, s.session_type
                FROM games g
                JOIN bowling_sessions s ON s.id = g.session_id
                WHERE s.user_id = %s
                ORDER BY s.started_at ASC, g.game_number ASC
                """,
                (user_id,),
            )
            game_rows = cursor.fetchall()

            cursor.execute(
                """
                SELECT session_type, COUNT(*) AS count
                FROM bowling_sessions
                WHERE user_id = %s
                GROUP BY session_type
                ORDER BY count DESC
                """,
                (user_id,),
            )
            session_type_rows = cursor.fetchall()

            cursor.execute(
                "SELECT COUNT(*) AS count FROM bowling_sessions WHERE user_id = %s",
                (user_id,),
            )
            total_sessions = cursor.fetchone()["count"]

    if not game_rows:
        profile = _empty_profile()
        profile.total_sessions = total_sessions
        return profile

    scores = [row["score"] for row in game_rows]
    average_score = round(statistics.mean(scores), 1)
    high_game = max(scores)

    return GhostBowlerProfile(
        average_score=average_score,
        high_game=high_game,
        total_games=len(scores),
        total_sessions=total_sessions,
        sessions_by_type=[
            SessionTypeBreakdown(session_type=row["session_type"], count=row["count"])
            for row in session_type_rows
        ],
        trend=_trend(scores),
        predicted_next_game=_predicted_next_game(scores),
        consistency_score=_consistency_score(scores),
        performance_tier=_performance_tier(average_score),
    )
