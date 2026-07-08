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
