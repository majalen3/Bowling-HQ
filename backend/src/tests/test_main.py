import pytest
from fastapi.testclient import TestClient

from src.config import Settings
from src.main import app

client = TestClient(app)


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


def test_progress_endpoint_returns_board_snapshot() -> None:
    response = client.get("/api/v1/progress")

    assert response.status_code == 200
    payload = response.json()
    assert payload["finished_target"]
    assert payload["scope_lock"]
    assert payload["release_gate"]
    assert payload["board"]
    statuses = {item["status"] for item in payload["board"]}
    assert statuses == {"backlog", "in_progress", "done"}
