from __future__ import annotations

from typing import Optional
from uuid import UUID

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.arsenal import BowlingBall
from src.models.patterns import LanePattern, LanePatternDetail

_PATTERN_COLUMNS = """
    id, name, pattern_type, oil_volume, oil_distance, difficulty,
    description, recommended_coverstock, recommended_hook_min,
    recommended_hook_max, notes, created_at
"""


def _connection():
    return connect(get_settings().postgres_url, row_factory=dict_row)


def list_patterns(
    difficulty: Optional[int] = None,
    pattern_type: Optional[str] = None,
) -> list[LanePattern]:
    filters = []
    params: list = []
    if difficulty is not None:
        filters.append("difficulty = %s")
        params.append(difficulty)
    if pattern_type:
        filters.append("pattern_type = %s")
        params.append(pattern_type)
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_PATTERN_COLUMNS}
                FROM lane_patterns
                {where_clause}
                ORDER BY difficulty, name
                """,
                params,
            )
            rows = cursor.fetchall()
    return [LanePattern.model_validate(row) for row in rows]


def get_pattern(pattern_id: UUID) -> Optional[LanePatternDetail]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_PATTERN_COLUMNS}
                FROM lane_patterns
                WHERE id = %s
                """,
                (pattern_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            cursor.execute(
                """
                SELECT
                    id, brand, name, coverstock_type, core_type, rg,
                    differential, hook_potential, length, backend,
                    oil_condition, weight_options, description, created_at
                FROM bowling_balls
                WHERE coverstock_type = %s
                    AND hook_potential BETWEEN %s AND %s
                ORDER BY hook_potential DESC
                LIMIT 5
                """,
                (
                    row["recommended_coverstock"],
                    row["recommended_hook_min"] or 1,
                    row["recommended_hook_max"] or 10,
                ),
            )
            ball_rows = cursor.fetchall()

    recommended_balls = [BowlingBall.model_validate(b) for b in ball_rows]
    return LanePatternDetail(
        **LanePattern.model_validate(row).model_dump(),
        recommended_balls=recommended_balls,
    )
