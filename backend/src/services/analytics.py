from __future__ import annotations

from functools import lru_cache
from typing import Optional, Protocol
from uuid import UUID

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.analytics import (
    AnalyticsSummary,
    BallAverage,
    ScoreTrendPoint,
)


class AnalyticsRepository(Protocol):
    def get_games_with_sessions(self, user_id: UUID) -> list[dict]:
        ...

    def get_per_ball_averages(self, user_id: UUID) -> list[BallAverage]:
        ...


class PostgresAnalyticsRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def get_games_with_sessions(self, user_id: UUID) -> list[dict]:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT g.id AS game_id, g.score, g.session_id,
                        s.started_at, s.location_name
                    FROM games g
                    JOIN bowling_sessions s ON s.id = g.session_id
                    WHERE s.user_id = %s
                    ORDER BY s.started_at ASC, g.game_number ASC
                    """,
                    (user_id,),
                )
                return list(cursor.fetchall())

    def get_per_ball_averages(self, user_id: UUID) -> list[BallAverage]:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT cr.recommended_ball_id AS ball_id,
                        b.name AS ball_name,
                        AVG(g.score) AS average,
                        COUNT(g.id) AS game_count
                    FROM commander_recommendations cr
                    JOIN bowling_balls b
                        ON b.id = cr.recommended_ball_id
                    JOIN games g ON g.session_id = cr.session_id
                    WHERE cr.user_id = %s
                        AND cr.recommended_ball_id IS NOT NULL
                        AND cr.session_id IS NOT NULL
                    GROUP BY cr.recommended_ball_id, b.name
                    ORDER BY average DESC
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()
        return [
            BallAverage(
                ball_id=row["ball_id"],
                ball_name=row["ball_name"],
                average=round(float(row["average"]), 2),
                game_count=int(row["game_count"]),
            )
            for row in rows
        ]


@lru_cache
def get_analytics_repository() -> AnalyticsRepository:
    return PostgresAnalyticsRepository(
        postgres_url=get_settings().postgres_url,
    )


def _empty_summary() -> AnalyticsSummary:
    return AnalyticsSummary(
        overall_average=0.0,
        high_game=0,
        total_games=0,
        total_sessions=0,
        recent_trend=[],
        per_ball_averages=[],
    )


def get_analytics_summary(
    user_id: UUID,
    repository: Optional[AnalyticsRepository] = None,
) -> AnalyticsSummary:
    repo = repository or get_analytics_repository()
    games = repo.get_games_with_sessions(user_id)
    if not games:
        return _empty_summary()

    scores = [int(row["score"]) for row in games]
    overall_average = round(sum(scores) / len(scores), 2)
    high_game = max(scores)

    grouped: dict[UUID, dict] = {}
    order: list[UUID] = []
    for row in games:
        session_id = row["session_id"]
        if session_id not in grouped:
            grouped[session_id] = {
                "session_id": session_id,
                "date": row["started_at"],
                "location_name": row.get("location_name"),
                "scores": [],
            }
            order.append(session_id)
        grouped[session_id]["scores"].append(int(row["score"]))

    trend: list[ScoreTrendPoint] = []
    for session_id in order:
        info = grouped[session_id]
        session_scores = info["scores"]
        trend.append(
            ScoreTrendPoint(
                session_id=info["session_id"],
                date=info["date"],
                average=round(
                    sum(session_scores) / len(session_scores), 2
                ),
                game_count=len(session_scores),
                high_game=max(session_scores),
                location_name=info["location_name"],
            )
        )
    trend.sort(key=lambda point: point.date, reverse=True)
    recent_trend = trend[:10]

    per_ball = repo.get_per_ball_averages(user_id)

    return AnalyticsSummary(
        overall_average=overall_average,
        high_game=high_game,
        total_games=len(scores),
        total_sessions=len(order),
        recent_trend=recent_trend,
        per_ball_averages=per_ball,
    )
