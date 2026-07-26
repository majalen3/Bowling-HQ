from __future__ import annotations

from functools import lru_cache
from typing import Optional, Protocol
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.arsenal import (
    ArsenalResponse,
    BallCreate,
    BallItem,
    UserArsenalBall,
)

# Real balls with accurate published specs used to seed the catalog.
BALL_CATALOG_SEED: list[dict] = [
    {
        "name": "Storm Phaze II",
        "brand": "Storm",
        "coverstock": "solid reactive",
        "rg": 2.48,
        "differential": 0.048,
        "mass_bias": 0.0,
        "surface_grit": 3000,
    },
    {
        "name": "Storm IQ Tour",
        "brand": "Storm",
        "coverstock": "solid reactive",
        "rg": 2.49,
        "differential": 0.044,
        "mass_bias": 0.0,
        "surface_grit": 4000,
    },
    {
        "name": "900 Global Zen Gold Label",
        "brand": "900 Global",
        "coverstock": "solid reactive",
        "rg": 2.47,
        "differential": 0.052,
        "mass_bias": 0.018,
        "surface_grit": 2000,
    },
    {
        "name": "Storm Hyroad",
        "brand": "Storm",
        "coverstock": "hybrid reactive",
        "rg": 2.48,
        "differential": 0.047,
        "mass_bias": 0.0,
        "surface_grit": 4000,
    },
    {
        "name": "Motiv Forge Fire",
        "brand": "Motiv",
        "coverstock": "hybrid reactive",
        "rg": 2.50,
        "differential": 0.052,
        "mass_bias": 0.0,
        "surface_grit": 2000,
    },
    {
        "name": "Storm Hy-Road Pearl",
        "brand": "Storm",
        "coverstock": "pearl reactive",
        "rg": 2.52,
        "differential": 0.047,
        "mass_bias": 0.0,
        "surface_grit": 4000,
    },
    {
        "name": "Ebonite Maxim",
        "brand": "Ebonite",
        "coverstock": "plastic",
        "rg": 2.57,
        "differential": 0.025,
        "mass_bias": 0.0,
        "surface_grit": 4000,
    },
    {
        "name": "Columbia 300 White Dot",
        "brand": "Columbia 300",
        "coverstock": "plastic",
        "rg": 2.58,
        "differential": 0.020,
        "mass_bias": 0.0,
        "surface_grit": 4000,
    },
    {
        "name": "900 Global C System Alpha",
        "brand": "900 Global",
        "coverstock": "urethane",
        "rg": 2.55,
        "differential": 0.028,
        "mass_bias": 0.0,
        "surface_grit": 4000,
    },
    {
        "name": "Hammer Black Widow",
        "brand": "Hammer",
        "coverstock": "solid reactive",
        "rg": 2.47,
        "differential": 0.058,
        "mass_bias": 0.018,
        "surface_grit": 1500,
    },
]


class ArsenalRepository(Protocol):
    def list_catalog(self) -> list[BallItem]:
        ...

    def ensure_catalog(self, seed: list[dict]) -> None:
        ...

    def get_ball(self, ball_id: UUID) -> Optional[BallItem]:
        ...

    def create_ball(self, payload: BallCreate) -> BallItem:
        ...

    def list_arsenal(self, user_id: UUID) -> list[UserArsenalBall]:
        ...

    def add_to_arsenal(
        self,
        user_id: UUID,
        ball_id: UUID,
        notes: Optional[str],
    ) -> UserArsenalBall:
        ...

    def remove_from_arsenal(
        self,
        user_id: UUID,
        arsenal_id: UUID,
    ) -> bool:
        ...


class PostgresArsenalRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def list_catalog(self) -> list[BallItem]:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, brand, coverstock, rg, differential,
                        mass_bias, surface_grit, weight_lbs, created_at
                    FROM bowling_balls
                    ORDER BY name ASC
                    """
                )
                rows = cursor.fetchall()
        return [BallItem.model_validate(row) for row in rows]

    def ensure_catalog(self, seed: list[dict]) -> None:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM bowling_balls")
                row = cursor.fetchone()
                if row and row["total"]:
                    return
                for spec in seed:
                    cursor.execute(
                        """
                        INSERT INTO bowling_balls (
                            id, name, brand, coverstock, rg, differential,
                            mass_bias, surface_grit, weight_lbs
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        """,
                        (
                            uuid4(),
                            spec["name"],
                            spec["brand"],
                            spec["coverstock"],
                            spec["rg"],
                            spec["differential"],
                            spec.get("mass_bias", 0.0),
                            spec.get("surface_grit", 3000),
                            spec.get("weight_lbs", 15),
                        ),
                    )

    def get_ball(self, ball_id: UUID) -> Optional[BallItem]:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, brand, coverstock, rg, differential,
                        mass_bias, surface_grit, weight_lbs, created_at
                    FROM bowling_balls
                    WHERE id = %s
                    """,
                    (ball_id,),
                )
                row = cursor.fetchone()
        return BallItem.model_validate(row) if row else None

    def create_ball(self, payload: BallCreate) -> BallItem:
        ball_id = uuid4()
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO bowling_balls (
                        id, name, brand, coverstock, rg, differential,
                        mass_bias, surface_grit, weight_lbs
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, name, brand, coverstock, rg, differential,
                        mass_bias, surface_grit, weight_lbs, created_at
                    """,
                    (
                        ball_id,
                        payload.name,
                        payload.brand,
                        payload.coverstock,
                        payload.rg,
                        payload.differential,
                        payload.mass_bias,
                        payload.surface_grit,
                        payload.weight_lbs,
                    ),
                )
                row = cursor.fetchone()
        return BallItem.model_validate(row)

    def list_arsenal(self, user_id: UUID) -> list[UserArsenalBall]:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ua.id AS arsenal_id, ua.notes, ua.added_at,
                        b.id, b.name, b.brand, b.coverstock, b.rg,
                        b.differential, b.mass_bias, b.surface_grit,
                        b.weight_lbs, b.created_at
                    FROM user_arsenal ua
                    JOIN bowling_balls b ON b.id = ua.ball_id
                    WHERE ua.user_id = %s
                    ORDER BY ua.added_at DESC
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()
        return [self._to_arsenal_ball(row) for row in rows]

    def add_to_arsenal(
        self,
        user_id: UUID,
        ball_id: UUID,
        notes: Optional[str],
    ) -> UserArsenalBall:
        arsenal_id = uuid4()
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO user_arsenal (id, user_id, ball_id, notes)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, ball_id) DO UPDATE
                        SET notes = EXCLUDED.notes
                    RETURNING id AS arsenal_id, notes, added_at
                    """,
                    (arsenal_id, user_id, ball_id, notes),
                )
                entry = cursor.fetchone()
                cursor.execute(
                    """
                    SELECT id, name, brand, coverstock, rg, differential,
                        mass_bias, surface_grit, weight_lbs, created_at
                    FROM bowling_balls
                    WHERE id = %s
                    """,
                    (ball_id,),
                )
                ball_row = cursor.fetchone()
        merged = {**entry, **ball_row}
        return self._to_arsenal_ball(merged)

    def remove_from_arsenal(
        self,
        user_id: UUID,
        arsenal_id: UUID,
    ) -> bool:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM user_arsenal
                    WHERE id = %s AND user_id = %s
                    RETURNING id
                    """,
                    (arsenal_id, user_id),
                )
                deleted = cursor.fetchone()
        return deleted is not None

    @staticmethod
    def _to_arsenal_ball(row: dict) -> UserArsenalBall:
        ball = BallItem.model_validate(row)
        return UserArsenalBall(
            id=row["arsenal_id"],
            ball=ball,
            notes=row.get("notes"),
            added_at=row["added_at"],
        )


@lru_cache
def get_arsenal_repository() -> ArsenalRepository:
    return PostgresArsenalRepository(
        postgres_url=get_settings().postgres_url,
    )


def ensure_ball_catalog(
    repository: Optional[ArsenalRepository] = None,
) -> None:
    repo = repository or get_arsenal_repository()
    repo.ensure_catalog(BALL_CATALOG_SEED)


def list_balls_catalog(
    repository: Optional[ArsenalRepository] = None,
) -> list[BallItem]:
    repo = repository or get_arsenal_repository()
    return repo.list_catalog()


def get_user_arsenal(
    user_id: UUID,
    repository: Optional[ArsenalRepository] = None,
) -> ArsenalResponse:
    repo = repository or get_arsenal_repository()
    balls = repo.list_arsenal(user_id)
    return ArsenalResponse(
        user_id=user_id,
        balls=balls,
        count=len(balls),
    )


def add_ball_to_arsenal(
    user_id: UUID,
    ball_id: UUID,
    notes: Optional[str] = None,
    repository: Optional[ArsenalRepository] = None,
) -> UserArsenalBall:
    repo = repository or get_arsenal_repository()
    ball = repo.get_ball(ball_id)
    if ball is None:
        raise KeyError(f"Ball {ball_id} not found")
    return repo.add_to_arsenal(user_id, ball_id, notes)


def create_and_add_ball(
    user_id: UUID,
    ball_create: BallCreate,
    notes: Optional[str] = None,
    repository: Optional[ArsenalRepository] = None,
) -> UserArsenalBall:
    repo = repository or get_arsenal_repository()
    ball = repo.create_ball(ball_create)
    return repo.add_to_arsenal(user_id, ball.id, notes)


def remove_from_arsenal(
    user_id: UUID,
    arsenal_id: UUID,
    repository: Optional[ArsenalRepository] = None,
) -> bool:
    repo = repository or get_arsenal_repository()
    return repo.remove_from_arsenal(user_id, arsenal_id)
