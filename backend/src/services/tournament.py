from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.arsenal import BowlingBall
from src.models.tournament import (
    LineupBall,
    LineupBallAddRequest,
    LineupCreateRequest,
    LineupRecommendation,
    TournamentLineup,
    TournamentLineupDetail,
)

DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

_STRATEGY_WEIGHT = {
    "conservative": -1,
    "defensive": -1,
    "versatile": 0,
    "aggressive": 1,
}

_ROLE_ORDER = ["primary", "secondary", "tertiary", "spare"]


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
            (DEFAULT_USER_ID, "demo@bowling-hq.local", "Demo User"),
        )


def list_lineups(user_id: UUID = DEFAULT_USER_ID) -> list[TournamentLineup]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, name, tournament_name, pattern_id,
                    strategy, notes, created_at
                FROM tournament_lineups
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
    return [TournamentLineup.model_validate(row) for row in rows]


def create_lineup(
    payload: LineupCreateRequest,
    user_id: UUID = DEFAULT_USER_ID,
) -> TournamentLineup:
    lineup_id = uuid4()
    with _connection() as connection:
        _ensure_default_user(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tournament_lineups (
                    id, user_id, name, tournament_name, pattern_id,
                    strategy, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, name, tournament_name, pattern_id,
                    strategy, notes, created_at
                """,
                (
                    lineup_id,
                    user_id,
                    payload.name,
                    payload.tournament_name,
                    payload.pattern_id,
                    payload.strategy,
                    payload.notes,
                ),
            )
            row = cursor.fetchone()
    return TournamentLineup.model_validate(row)


def _row_to_ball(row: dict) -> BowlingBall:
    return BowlingBall(
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


def get_lineup(
    lineup_id: UUID,
    user_id: UUID = DEFAULT_USER_ID,
) -> Optional[TournamentLineupDetail]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, name, tournament_name, pattern_id,
                    strategy, notes, created_at
                FROM tournament_lineups
                WHERE id = %s AND user_id = %s
                """,
                (lineup_id, user_id),
            )
            lineup_row = cursor.fetchone()
            if lineup_row is None:
                return None

            cursor.execute(
                """
                SELECT
                    lb.id, lb.user_arsenal_id, lb.role, lb.order_index,
                    lb.notes,
                    bb.id AS ball_id, bb.brand, bb.name, bb.coverstock_type,
                    bb.core_type, bb.rg, bb.differential, bb.hook_potential,
                    bb.length, bb.backend, bb.oil_condition,
                    bb.weight_options, bb.description,
                    bb.created_at AS ball_created_at
                FROM lineup_balls lb
                JOIN user_arsenal ua ON ua.id = lb.user_arsenal_id
                JOIN bowling_balls bb ON bb.id = ua.ball_id
                WHERE lb.lineup_id = %s
                ORDER BY lb.order_index ASC
                """,
                (lineup_id,),
            )
            ball_rows = cursor.fetchall()

    balls = [
        LineupBall(
            id=row["id"],
            user_arsenal_id=row["user_arsenal_id"],
            role=row["role"],
            order_index=row["order_index"],
            notes=row["notes"],
            ball=_row_to_ball(row),
        )
        for row in ball_rows
    ]
    return TournamentLineupDetail(
        **TournamentLineup.model_validate(lineup_row).model_dump(),
        balls=balls,
    )


def add_ball_to_lineup(
    lineup_id: UUID,
    payload: LineupBallAddRequest,
    user_id: UUID = DEFAULT_USER_ID,
) -> LineupBall:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM tournament_lineups WHERE id = %s AND user_id = %s",
                (lineup_id, user_id),
            )
            if cursor.fetchone() is None:
                raise KeyError(f"Lineup {lineup_id} not found")

            cursor.execute(
                "SELECT id FROM user_arsenal WHERE id = %s AND user_id = %s",
                (payload.user_arsenal_id, user_id),
            )
            if cursor.fetchone() is None:
                raise ValueError(f"Arsenal item {payload.user_arsenal_id} not found")

            cursor.execute(
                "SELECT COALESCE(MAX(order_index), -1) + 1 AS next_index "
                "FROM lineup_balls WHERE lineup_id = %s",
                (lineup_id,),
            )
            next_index = cursor.fetchone()["next_index"]

            lineup_ball_id = uuid4()
            cursor.execute(
                """
                INSERT INTO lineup_balls (
                    id, lineup_id, user_arsenal_id, role, order_index, notes
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    lineup_ball_id,
                    lineup_id,
                    payload.user_arsenal_id,
                    payload.role,
                    next_index,
                    payload.notes,
                ),
            )

            cursor.execute(
                """
                SELECT
                    lb.id, lb.user_arsenal_id, lb.role, lb.order_index,
                    lb.notes,
                    bb.id AS ball_id, bb.brand, bb.name, bb.coverstock_type,
                    bb.core_type, bb.rg, bb.differential, bb.hook_potential,
                    bb.length, bb.backend, bb.oil_condition,
                    bb.weight_options, bb.description,
                    bb.created_at AS ball_created_at
                FROM lineup_balls lb
                JOIN user_arsenal ua ON ua.id = lb.user_arsenal_id
                JOIN bowling_balls bb ON bb.id = ua.ball_id
                WHERE lb.id = %s
                """,
                (lineup_ball_id,),
            )
            row = cursor.fetchone()
    return LineupBall(
        id=row["id"],
        user_arsenal_id=row["user_arsenal_id"],
        role=row["role"],
        order_index=row["order_index"],
        notes=row["notes"],
        ball=_row_to_ball(row),
    )


def remove_ball_from_lineup(
    lineup_id: UUID,
    lineup_ball_id: UUID,
    user_id: UUID = DEFAULT_USER_ID,
) -> None:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM lineup_balls
                WHERE id = %s AND lineup_id = %s
                    AND lineup_id IN (
                        SELECT id FROM tournament_lineups WHERE user_id = %s
                    )
                RETURNING id
                """,
                (lineup_ball_id, lineup_id, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise KeyError(f"Lineup ball {lineup_ball_id} not found")


def _score_arsenal_ball(
    row: dict,
    pattern_row: Optional[dict],
    strategy: Optional[str],
) -> tuple[int, str]:
    hook = row["hook_potential"] if row["hook_potential"] is not None else 5
    score = 20
    reasoning_parts = []

    if pattern_row:
        if row["coverstock_type"] == pattern_row["recommended_coverstock"]:
            score += 40
            reasoning_parts.append("Coverstock matches the target pattern.")
        hook_min = pattern_row["recommended_hook_min"] or 1
        hook_max = pattern_row["recommended_hook_max"] or 10
        if hook_min <= hook <= hook_max:
            score += 30
            reasoning_parts.append(
                f"Hook potential {hook} is within the pattern's recommended range.",
            )
        else:
            distance = min(abs(hook - hook_min), abs(hook - hook_max))
            score -= distance * 3
            reasoning_parts.append(
                f"Hook potential {hook} is outside the pattern's ideal range.",
            )
    else:
        reasoning_parts.append("No target pattern specified; scored on general versatility.")

    weight = _STRATEGY_WEIGHT.get(strategy or "versatile", 0)
    score += weight * (hook - 5) * 2
    if strategy:
        reasoning_parts.append(f"Adjusted for a {strategy} strategy.")

    return max(0, round(score)), " ".join(reasoning_parts)


def recommend_lineup(
    lineup_id: UUID,
    user_id: UUID = DEFAULT_USER_ID,
) -> list[LineupRecommendation]:
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, pattern_id, strategy
                FROM tournament_lineups
                WHERE id = %s AND user_id = %s
                """,
                (lineup_id, user_id),
            )
            lineup_row = cursor.fetchone()
            if lineup_row is None:
                raise KeyError(f"Lineup {lineup_id} not found")

            pattern_row = None
            if lineup_row["pattern_id"]:
                cursor.execute(
                    """
                    SELECT recommended_coverstock, recommended_hook_min,
                        recommended_hook_max
                    FROM lane_patterns
                    WHERE id = %s
                    """,
                    (lineup_row["pattern_id"],),
                )
                pattern_row = cursor.fetchone()

            cursor.execute(
                """
                SELECT
                    ua.id AS user_arsenal_id, bb.id AS ball_id, bb.brand,
                    bb.name, bb.coverstock_type, bb.core_type, bb.rg,
                    bb.differential, bb.hook_potential, bb.length,
                    bb.backend, bb.oil_condition, bb.weight_options,
                    bb.description, bb.created_at AS ball_created_at
                FROM user_arsenal ua
                JOIN bowling_balls bb ON bb.id = ua.ball_id
                WHERE ua.user_id = %s
                """,
                (user_id,),
            )
            arsenal_rows = cursor.fetchall()

    if not arsenal_rows:
        return []

    scored = []
    for row in arsenal_rows:
        score, reasoning = _score_arsenal_ball(
            row, pattern_row, lineup_row["strategy"],
        )
        scored.append((score, reasoning, row))
    scored.sort(key=lambda item: item[0], reverse=True)

    # Reserve the lowest-hook, most spare-friendly ball for the "spare" role.
    def _hook_potential(index: int) -> int:
        _, _, candidate_row = scored[index]
        return candidate_row.get("hook_potential") or 0

    spare_index = min(range(len(scored)), key=_hook_potential)
    spare_candidate = scored[spare_index]
    remaining = [item for i, item in enumerate(scored) if i != spare_index]

    recommendations: list[LineupRecommendation] = []
    role_pool = ["primary", "secondary", "tertiary"]
    for index, (score, reasoning, row) in enumerate(remaining[: len(role_pool)]):
        recommendations.append(
            LineupRecommendation(
                user_arsenal_id=row["user_arsenal_id"],
                role=role_pool[index],
                reasoning=reasoning,
                ball=_row_to_ball(row),
            ),
        )

    if len(scored) > 1:
        spare_score, spare_reasoning, spare_row = spare_candidate
        recommendations.append(
            LineupRecommendation(
                user_arsenal_id=spare_row["user_arsenal_id"],
                role="spare",
                reasoning=f"Lowest hook potential in your arsenal: {spare_reasoning}",
                ball=_row_to_ball(spare_row),
            ),
        )

    _apply_recommendations(lineup_id, recommendations)
    return recommendations


def _apply_recommendations(
    lineup_id: UUID,
    recommendations: list[LineupRecommendation],
) -> None:
    """Auto-fill the lineup: replace existing lineup balls with the
    freshly computed recommendation set so the lineup reflects the
    latest suggested roles."""
    with _connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM lineup_balls WHERE lineup_id = %s",
                (lineup_id,),
            )
            for index, recommendation in enumerate(recommendations):
                cursor.execute(
                    """
                    INSERT INTO lineup_balls (
                        id, lineup_id, user_arsenal_id, role, order_index,
                        notes
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid4(),
                        lineup_id,
                        recommendation.user_arsenal_id,
                        recommendation.role,
                        index,
                        recommendation.reasoning,
                    ),
                )
