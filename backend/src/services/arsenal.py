from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.arsenal import ArsenalAddRequest, ArsenalItem, BowlingBall

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

_BALL_COLUMNS = """
    id, brand, name, coverstock_type, core_type, rg, differential,
    hook_potential, length, backend, oil_condition, weight_options,
    description, created_at
"""


def _connection():
    return connect(get_settings().postgres_url, row_factory=dict_row)


def list_catalog(
    oil_condition: Optional[str] = None,
    coverstock_type: Optional[str] = None,
) -> list[BowlingBall]:
    filters = []
    params: list[str] = []
    if oil_condition:
        filters.append("oil_condition = %s")
        params.append(oil_condition)
    if coverstock_type:
        filters.append("coverstock_type = %s")
        params.append(coverstock_type)
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_BALL_COLUMNS}
                FROM bowling_balls
                {where_clause}
                ORDER BY brand, name
                """,
                params,
            )
            rows = cursor.fetchall()
    return [BowlingBall.model_validate(row) for row in rows]


def get_catalog_ball(ball_id: UUID) -> Optional[BowlingBall]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT {_BALL_COLUMNS}
                FROM bowling_balls
                WHERE id = %s
                """,
                (ball_id,),
            )
            row = cursor.fetchone()
    return BowlingBall.model_validate(row) if row else None


def _row_to_arsenal_item(row: dict) -> ArsenalItem:
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
    return ArsenalItem(
        id=row["id"],
        ball_id=row["ball_id"],
        purchase_date=row["purchase_date"],
        layout=row["layout"],
        notes=row["notes"],
        games_played=row["games_played"],
        added_at=row["added_at"],
        ball=ball,
    )


def _ensure_default_user(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (id, email, display_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (DEFAULT_USER_ID, "demo@bowling-hq.local", "Demo User"),
        )


def list_user_arsenal(user_id: UUID = DEFAULT_USER_ID) -> list[ArsenalItem]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ua.id, ua.ball_id, ua.purchase_date, ua.layout, ua.notes,
                    ua.games_played, ua.added_at,
                    bb.brand, bb.name, bb.coverstock_type, bb.core_type,
                    bb.rg, bb.differential, bb.hook_potential, bb.length,
                    bb.backend, bb.oil_condition, bb.weight_options,
                    bb.description, bb.created_at AS ball_created_at
                FROM user_arsenal ua
                JOIN bowling_balls bb ON bb.id = ua.ball_id
                WHERE ua.user_id = %s
                ORDER BY ua.added_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
    return [_row_to_arsenal_item(row) for row in rows]


def add_to_arsenal(
    payload: ArsenalAddRequest,
    user_id: UUID = DEFAULT_USER_ID,
) -> ArsenalItem:
    arsenal_id = uuid4()
    with _connection() as connection:
        _ensure_default_user(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM bowling_balls WHERE id = %s",
                (payload.ball_id,),
            )
            if cursor.fetchone() is None:
                raise KeyError(f"Ball {payload.ball_id} not found")
            cursor.execute(
                """
                INSERT INTO user_arsenal (
                    id, user_id, ball_id, purchase_date, layout, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, ball_id) DO UPDATE SET
                    purchase_date = EXCLUDED.purchase_date,
                    layout = EXCLUDED.layout,
                    notes = EXCLUDED.notes
                RETURNING id
                """,
                (
                    arsenal_id,
                    user_id,
                    payload.ball_id,
                    payload.purchase_date,
                    payload.layout,
                    payload.notes,
                ),
            )
            row = cursor.fetchone()
            resolved_id = row["id"]

            cursor.execute(
                """
                SELECT
                    ua.id, ua.ball_id, ua.purchase_date, ua.layout, ua.notes,
                    ua.games_played, ua.added_at,
                    bb.brand, bb.name, bb.coverstock_type, bb.core_type,
                    bb.rg, bb.differential, bb.hook_potential, bb.length,
                    bb.backend, bb.oil_condition, bb.weight_options,
                    bb.description, bb.created_at AS ball_created_at
                FROM user_arsenal ua
                JOIN bowling_balls bb ON bb.id = ua.ball_id
                WHERE ua.id = %s
                """,
                (resolved_id,),
            )
            row = cursor.fetchone()
    return _row_to_arsenal_item(row)


def remove_from_arsenal(
    user_arsenal_id: UUID,
    user_id: UUID = DEFAULT_USER_ID,
) -> None:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM user_arsenal
                WHERE id = %s AND user_id = %s
                RETURNING id
                """,
                (user_arsenal_id, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise KeyError(f"Arsenal item {user_arsenal_id} not found")


def get_arsenal_with_balls(user_id: UUID = DEFAULT_USER_ID) -> list[dict]:
    """Return raw arsenal rows joined with ball data, used by other services.
    """
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ua.id, ua.ball_id, ua.purchase_date, ua.layout, ua.notes,
                    ua.games_played, ua.added_at,
                    bb.brand, bb.name, bb.coverstock_type, bb.core_type,
                    bb.rg, bb.differential, bb.hook_potential, bb.length,
                    bb.backend, bb.oil_condition, bb.weight_options,
                    bb.description, bb.created_at AS ball_created_at
                FROM user_arsenal ua
                JOIN bowling_balls bb ON bb.id = ua.ball_id
                WHERE ua.user_id = %s
                ORDER BY ua.added_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
    return rows
