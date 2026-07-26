from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.config import Settings
from src.main import app
from src.models.session_progress import (
    SessionCreateRequest,
    SessionProgressItem,
)

client = TestClient(app)


class FakeSessionRepository:
    def __init__(self) -> None:
        self.sessions: dict[UUID, SessionProgressItem] = {}

    def create_session(
        self,
        payload: SessionCreateRequest,
    ) -> SessionProgressItem:
        session_id = uuid4()
        item = SessionProgressItem(
            id=session_id,
            session_type=payload.session_type,
            location_name=payload.location_name,
            started_at=datetime.now(timezone.utc),
            completed_at=None,
        )
        self.sessions[session_id] = item
        return item

    def complete_session(self, session_id: UUID) -> SessionProgressItem:
        existing = self.sessions.get(session_id)
        if existing is None:
            raise KeyError(f"Session {session_id} not found")
        completed = existing.model_copy(
            update={"completed_at": datetime.now(timezone.utc)},
        )
        self.sessions[session_id] = completed
        return completed

    def list_sessions(self) -> list[SessionProgressItem]:
        return list(self.sessions.values())


@pytest.fixture
def fake_session_repo(
    monkeypatch: pytest.MonkeyPatch,
) -> FakeSessionRepository:
    fake = FakeSessionRepository()
    monkeypatch.setattr(
        "src.services.session_progress.get_session_repository",
        lambda: fake,
    )
    return fake


def test_root_returns_service_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "Bowling-HQ API"
    assert response.json()["api_prefix"] == "/api/v1"


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_non_development_requires_secret_key() -> None:
    with pytest.raises(ValueError):
        Settings(ENVIRONMENT="production")


def test_progress_endpoint_returns_board_snapshot(
    fake_session_repo: FakeSessionRepository,
) -> None:
    response = client.get("/api/v1/progress")

    assert response.status_code == 200
    payload = response.json()
    assert payload["finished_target"]
    assert payload["scope_lock"]
    assert payload["release_gate"]
    assert payload["board"]
    slice_item = next(
        item for item in payload["board"] if item["id"] == "MVP-004"
    )
    assert slice_item["status"] == "backlog"
    assert "Slice 1 sessions completed: 0/0" in slice_item["done_criteria"]
    statuses = {item["status"] for item in payload["board"]}
    assert statuses == {"backlog", "in_progress", "done"}


def test_session_progress_workflow_updates_progress(
    fake_session_repo: FakeSessionRepository,
) -> None:
    create_response = client.post(
        "/api/v1/sessions",
        json={"session_type": "practice", "location_name": "House Shot"},
    )
    assert create_response.status_code == 201
    created_session_id = create_response.json()["id"]

    progress_response = client.get("/api/v1/progress")
    assert progress_response.status_code == 200
    board = progress_response.json()["board"]
    mvp_004 = next(item for item in board if item["id"] == "MVP-004")
    assert mvp_004["status"] == "in_progress"
    assert "Slice 1 sessions completed: 0/1" in mvp_004["done_criteria"]

    complete_response = client.post(
        f"/api/v1/sessions/{created_session_id}/complete",
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["completed_at"] is not None

    session_progress = client.get("/api/v1/sessions/progress")
    assert session_progress.status_code == 200
    assert session_progress.json()["completed_sessions"] == 1

    updated_progress = client.get("/api/v1/progress")
    assert updated_progress.status_code == 200
    updated_board = updated_progress.json()["board"]
    updated_mvp_004 = next(
        item for item in updated_board if item["id"] == "MVP-004"
    )
    assert updated_mvp_004["status"] == "done"
    assert (
        "Slice 1 sessions completed: 1/1"
        in updated_mvp_004["done_criteria"]
    )


def test_complete_missing_session_returns_not_found(
    fake_session_repo: FakeSessionRepository,
) -> None:
    response = client.post(
        "/api/v1/sessions/0ca79587-cf3b-4df7-a94a-c6f08e26713a/complete",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
