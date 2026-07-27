from __future__ import annotations

from typing import Optional
from uuid import UUID

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.arsenal import BallItem
from src.models.patterns import LanePattern, LanePatternDetail

_PATTERN_COLUMNS = """
    id, name, length_ft, volume_ml, asymmetry_index,
    front_oil_pct, mid_oil_pct, backend_oil_pct, created_at
"""

_BALL_COLUMNS = """
    id, name, brand, coverstock, rg, differential,
    mass_bias, surface_grit, weight_lbs, created_at
"""


def _connection():
    return connect(get_settings().postgres_url, row_factory=dict_row)


def list_patterns(
    difficulty: Optional[int] = None,
    pattern_type: Optional[str] = None,
) -> list[LanePattern]:
    # difficulty and pattern_type are kept for API compatibility but the new
    # schema does not have those columns; we return all patterns.
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_PATTERN_COLUMNS}
                FROM lane_patterns
                ORDER BY length_ft, name
                """,
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

            # Recommend balls whose surface finish suits the oil volume:
            # lower volume → drier → higher grit; higher volume → oilier → lower grit.
            volume = float(row["volume_ml"])
            if volume < 20:
                grit_lo, grit_hi = 3000, 4000
            elif volume < 28:
                grit_lo, grit_hi = 2000, 3500
            else:
                grit_lo, grit_hi = 500, 2500

            cursor.execute(
                f"""
                SELECT {_BALL_COLUMNS}
                FROM bowling_balls
                WHERE surface_grit BETWEEN %s AND %s
                ORDER BY differential DESC
                LIMIT 5
                """,
                (grit_lo, grit_hi),
            )
            ball_rows = cursor.fetchall()

    recommended_balls = [BallItem.model_validate(b) for b in ball_rows]
    return LanePatternDetail(
        **LanePattern.model_validate(row).model_dump(),
        recommended_balls=recommended_balls,
    )
