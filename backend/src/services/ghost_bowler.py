from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Optional, Protocol
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.ghost_bowler import (
    ConditionBaseline,
    GhostBowlerBaselineResponse,
    GhostBowlerCompareResponse,
)


@dataclass
class ScoredGame:
    score: int
    session_type: str
    started_at: datetime


class GhostBowlerRepository(Protocol):
    def list_games(self, user_id: UUID) -> list[ScoredGame]:
        ...

    def save_baseline(self, user_id: UUID, baseline: GhostBowlerBaselineResponse) -> None:
        ...


class PostgresGhostBowlerRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def list_games(self, user_id: UUID) -> list[ScoredGame]:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT g.score, s.session_type, s.started_at
                    FROM games g
                    JOIN bowling_sessions s ON s.id = g.session_id
                    WHERE s.user_id = %s
                    ORDER BY s.started_at DESC
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()
        return [ScoredGame(score=int(r["score"]), session_type=r["session_type"], started_at=r["started_at"]) for r in rows]

    def save_baseline(self, user_id: UUID, baseline: GhostBowlerBaselineResponse) -> None:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ghost_bowler_baselines (
                        id, user_id, total_games, overall_average,
                        overall_strike_rate, overall_spare_rate,
                        overall_open_rate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid4(),
                        user_id,
                        baseline.total_games,
                        baseline.overall.average_score,
                        baseline.overall.strike_rate,
                        baseline.overall.spare_rate,
                        baseline.overall.open_frame_rate,
                    ),
                )


@lru_cache
def get_ghost_bowler_repository() -> GhostBowlerRepository:
    return PostgresGhostBowlerRepository(get_settings().postgres_url)


def _condition_family(session_type: str) -> str:
    normalized = session_type.lower()
    if "sport" in normalized or "tournament" in normalized:
        return "sport"
    if "dry" in normalized:
        return "dry"
    return "house"


def _rates_from_average(average_score: float) -> tuple[float, float, float]:
    strike_rate = min(0.75, max(0.12, round((average_score - 110) / 180, 3)))
    spare_rate = min(0.90, max(0.25, round(0.65 - (strike_rate - 0.35) * 0.3, 3)))
    open_rate = max(0.02, round(1.0 - strike_rate - spare_rate, 3))
    return strike_rate, spare_rate, open_rate


def _build_condition(name: str, scores: list[int]) -> ConditionBaseline:
    if not scores:
        return ConditionBaseline(
            condition_family=name,
            game_count=0,
            average_score=0.0,
            score_band_low=0,
            score_band_high=0,
            strike_rate=0.0,
            spare_rate=0.0,
            open_frame_rate=0.0,
        )

    average = round(sum(scores) / len(scores), 2)
    strike_rate, spare_rate, open_rate = _rates_from_average(average)
    low = max(0, int(round(average - 12)))
    high = min(300, int(round(average + 12)))
    return ConditionBaseline(
        condition_family=name,
        game_count=len(scores),
        average_score=average,
        score_band_low=low,
        score_band_high=high,
        strike_rate=strike_rate,
        spare_rate=spare_rate,
        open_frame_rate=open_rate,
    )


def get_ghost_bowler_baseline(
    user_id: UUID, repository: Optional[GhostBowlerRepository] = None
) -> GhostBowlerBaselineResponse:
    repo = repository or get_ghost_bowler_repository()
    games = repo.list_games(user_id)

    buckets: dict[str, list[int]] = {"sport": [], "house": [], "dry": []}
    all_scores: list[int] = []
    for game in games:
        all_scores.append(game.score)
        buckets[_condition_family(game.session_type)].append(game.score)

    overall = _build_condition("overall", all_scores)
    by_condition = [
        _build_condition("house", buckets["house"]),
        _build_condition("sport", buckets["sport"]),
        _build_condition("dry", buckets["dry"]),
    ]
    response = GhostBowlerBaselineResponse(
        total_games=len(all_scores),
        overall=overall,
        by_condition=by_condition,
    )
    repo.save_baseline(user_id, response)
    return response


def compare_to_ghost_bowler(
    user_id: UUID,
    current_average: float,
    condition_family: str = "overall",
    repository: Optional[GhostBowlerRepository] = None,
) -> GhostBowlerCompareResponse:
    baseline = get_ghost_bowler_baseline(user_id, repository)
    baseline_average = baseline.overall.average_score
    if condition_family != "overall":
        for row in baseline.by_condition:
            if row.condition_family == condition_family:
                baseline_average = row.average_score
                break

    delta = round(current_average - baseline_average, 2)
    trend = "even"
    if delta >= 5:
        trend = "above_baseline"
    elif delta <= -5:
        trend = "below_baseline"

    return GhostBowlerCompareResponse(
        condition_family=condition_family,
        baseline_average=baseline_average,
        current_average=current_average,
        delta=delta,
        trend=trend,
    )
