from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Protocol
from uuid import UUID, uuid4

from psycopg import Connection, connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.session_progress import (
    SessionCreateRequest,
    SessionProgressItem,
    SessionProgressSnapshot,
)

DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
DEMO_USER_EMAIL = "demo@bowling-hq.local"
DEMO_USER_NAME = "Demo User"


class SessionProgressRepository(Protocol):
    def create_session(
        self,
        payload: SessionCreateRequest,
    ) -> SessionProgressItem:
        ...

    def complete_session(self, session_id: UUID) -> SessionProgressItem:
        ...

    def list_sessions(self) -> list[SessionProgressItem]:
        ...


class PostgresSessionProgressRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def create_session(
        self,
        payload: SessionCreateRequest,
    ) -> SessionProgressItem:
        session_id = uuid4()
        started_at = datetime.now(timezone.utc)
        with connect(self.postgres_url, row_factory=dict_row) as connection:
            self._ensure_demo_user(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO bowling_sessions (
                        id,
                        user_id,
                        session_type,
                        location_name,
                        started_at
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, session_type, location_name, started_at,
                        completed_at
                    """,
                    (
                        session_id,
                        DEMO_USER_ID,
                        payload.session_type,
                        payload.location_name,
                        started_at,
                    ),
                )
                row = cursor.fetchone()
        return SessionProgressItem.model_validate(row)

    def complete_session(self, session_id: UUID) -> SessionProgressItem:
        with connect(self.postgres_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE bowling_sessions
                    -- Keep completion idempotent: return existing completion
                    -- timestamp for already-completed sessions.
                    SET completed_at = COALESCE(completed_at, NOW())
                    WHERE id = %s
                    RETURNING id, session_type, location_name, started_at,
                        completed_at
                    """,
                    (session_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise KeyError(f"Session {session_id} not found")
        return SessionProgressItem.model_validate(row)

    def list_sessions(self) -> list[SessionProgressItem]:
        with connect(self.postgres_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, session_type, location_name, started_at,
                        completed_at
                    FROM bowling_sessions
                    WHERE user_id = %s
                    ORDER BY started_at DESC
                    """,
                    (DEMO_USER_ID,),
                )
                rows = cursor.fetchall()
        return [
            SessionProgressItem.model_validate(row)
            for row in rows
        ]

    def _ensure_demo_user(self, connection: Connection) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    id, email, display_name, password_hash
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    DEMO_USER_ID,
                    DEMO_USER_EMAIL,
                    DEMO_USER_NAME,
                    "demo",
                ),
            )


@lru_cache
def get_session_repository() -> SessionProgressRepository:
    return PostgresSessionProgressRepository(
        postgres_url=get_settings().postgres_url,
    )


def get_session_progress_snapshot(
    repository: SessionProgressRepository | None = None,
) -> SessionProgressSnapshot:
    repo = repository or get_session_repository()
    sessions = repo.list_sessions()
    completed_sessions = sum(
        1 for session in sessions if session.completed_at is not None
    )
    total_sessions = len(sessions)
    return SessionProgressSnapshot(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        active_sessions=total_sessions - completed_sessions,
        sessions=sessions,
    )


def start_session(
    payload: SessionCreateRequest,
    repository: SessionProgressRepository | None = None,
) -> SessionProgressItem:
    repo = repository or get_session_repository()
    return repo.create_session(payload)


def finish_session(
    session_id: UUID,
    repository: SessionProgressRepository | None = None,
) -> SessionProgressItem:
    repo = repository or get_session_repository()
    return repo.complete_session(session_id)
