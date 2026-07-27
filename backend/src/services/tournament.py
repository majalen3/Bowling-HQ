from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.arsenal import BallItem
from src.models.tournament import (
    LineupBall,
    LineupBallAddRequest,
    LineupCreateRequest,
    LineupRecommendation,
    TournamentLineup,
    TournamentLineupDetail,
)
from src.services.session_progress import DEMO_USER_ID

_BALL_COLUMNS = """
    id, name, brand, coverstock, rg, differential,
    mass_bias, surface_grit, weight_lbs, created_at
"""

_ROLES = ["primary", "secondary", "tertiary", "spare"]


def _connection():
    return connect(get_settings().postgres_url, row_factory=dict_row)


def _ensure_default_user(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (id, email, display_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (DEMO_USER_ID, "demo@bowling-hq.local", "Demo User"),
        )


def list_lineups(user_id: UUID = DEMO_USER_ID) -> list[TournamentLineup]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, name, pattern_name, created_at
                FROM tournament_bag_lineups
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
    return [TournamentLineup.model_validate(row) for row in rows]


def create_lineup(
    payload: LineupCreateRequest,
    user_id: UUID = DEMO_USER_ID,
) -> TournamentLineup:
    lineup_id = uuid4()
    with _connection() as connection:
        _ensure_default_user(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tournament_bag_lineups (id, user_id, name, pattern_name)
                VALUES (%s, %s, %s, %s)
                RETURNING id, user_id, name, pattern_name, created_at
                """,
                (lineup_id, user_id, payload.name, payload.pattern_name),
            )
            row = cursor.fetchone()
    return TournamentLineup.model_validate(row)


def get_lineup(lineup_id: UUID, user_id: UUID = DEMO_USER_ID) -> Optional[TournamentLineupDetail]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, name, pattern_name, created_at
                FROM tournament_bag_lineups
                WHERE id = %s AND user_id = %s
                """,
                (lineup_id, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            lineup = TournamentLineup.model_validate(row)

            cursor.execute(
                f"""
                SELECT lb.id, lb.ball_id, lb.slot_order, lb.rationale,
                    b.id, b.name, b.brand, b.coverstock, b.rg, b.differential,
                    b.mass_bias, b.surface_grit, b.weight_lbs, b.created_at
                FROM lineup_balls lb
                JOIN bowling_balls b ON b.id = lb.ball_id
                WHERE lb.lineup_id = %s
                ORDER BY lb.slot_order
                """,
                (lineup_id,),
            )
            ball_rows = cursor.fetchall()

    balls = [_row_to_lineup_ball(row) for row in ball_rows]
    return TournamentLineupDetail(**lineup.model_dump(), balls=balls)


def delete_lineup(lineup_id: UUID, user_id: UUID = DEMO_USER_ID) -> bool:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM tournament_bag_lineups
                WHERE id = %s AND user_id = %s
                RETURNING id
                """,
                (lineup_id, user_id),
            )
            return cursor.fetchone() is not None


def add_lineup_ball(
    lineup_id: UUID,
    payload: LineupBallAddRequest,
    user_id: UUID = DEMO_USER_ID,
) -> Optional[LineupBall]:
    lb_id = uuid4()
    with _connection() as connection:
        with connection.cursor() as cursor:
            # Verify lineup belongs to user
            cursor.execute(
                "SELECT id FROM tournament_bag_lineups WHERE id = %s AND user_id = %s",
                (lineup_id, user_id),
            )
            if cursor.fetchone() is None:
                return None

            cursor.execute(
                """
                INSERT INTO lineup_balls (id, lineup_id, ball_id, slot_order, rationale)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (lineup_id, slot_order) DO UPDATE
                    SET ball_id = EXCLUDED.ball_id,
                        rationale = EXCLUDED.rationale
                RETURNING id, ball_id, slot_order, rationale
                """,
                (lb_id, lineup_id, payload.ball_id, payload.slot_order, payload.rationale),
            )
            entry = cursor.fetchone()

            cursor.execute(
                f"""
                SELECT {_BALL_COLUMNS}
                FROM bowling_balls WHERE id = %s
                """,
                (payload.ball_id,),
            )
            ball_row = cursor.fetchone()

    if entry is None or ball_row is None:
        return None
    ball = BallItem.model_validate(ball_row)
    return LineupBall(
        id=entry["id"],
        ball_id=entry["ball_id"],
        slot_order=entry["slot_order"],
        rationale=entry["rationale"],
        ball=ball,
    )


def remove_lineup_ball(
    lineup_id: UUID,
    lineup_ball_id: UUID,
    user_id: UUID = DEMO_USER_ID,
) -> bool:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM lineup_balls lb
                USING tournament_bag_lineups tbl
                WHERE lb.id = %s
                    AND lb.lineup_id = tbl.id
                    AND tbl.id = %s
                    AND tbl.user_id = %s
                RETURNING lb.id
                """,
                (lineup_ball_id, lineup_id, user_id),
            )
            return cursor.fetchone() is not None


def recommend_lineup(
    lineup_id: UUID,
    user_id: UUID = DEMO_USER_ID,
) -> list[LineupRecommendation]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            # Get arsenal balls for this user
            cursor.execute(
                f"""
                SELECT b.{_BALL_COLUMNS.replace('id,', 'id,').strip()}
                FROM user_arsenal ua
                JOIN bowling_balls b ON b.id = ua.ball_id
                WHERE ua.user_id = %s
                ORDER BY b.differential DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()

    if not rows:
        return []

    balls = [BallItem.model_validate(row) for row in rows]

    # Sort: highest differential first (most hook) → primary, spare last
    # Spare ball: lowest differential (straightest)
    balls_sorted = sorted(balls, key=lambda b: b.differential, reverse=True)

    recommendations = []
    used: set[UUID] = set()
    for slot, role in enumerate(_ROLES, start=1):
        if not balls_sorted:
            break
        if role == "spare":
            # Pick the straightest ball (lowest differential) not yet used
            spare = min(
                (b for b in balls_sorted if b.id not in used),
                key=lambda b: b.differential,
                default=None,
            )
            if spare is None:
                continue
            ball = spare
            reasoning = f"Lowest differential ({ball.differential:.3f}) makes it the most predictable spare ball."
        else:
            idx = slot - 1
            ball = next((b for b in balls_sorted if b.id not in used), balls_sorted[0])
            reasoning = f"Differential {ball.differential:.3f} suits the {role} role for this lineup."

        used.add(ball.id)
        recommendations.append(
            LineupRecommendation(
                ball_id=ball.id,
                slot_order=slot,
                role=role,
                reasoning=reasoning,
                ball=ball,
            ),
        )

    return recommendations


def _row_to_lineup_ball(row: dict) -> LineupBall:
    ball = BallItem.model_validate(row)
    return LineupBall(
        id=row["id"],
        ball_id=row["ball_id"],
        slot_order=row["slot_order"],
        rationale=row.get("rationale"),
        ball=ball,
    )
