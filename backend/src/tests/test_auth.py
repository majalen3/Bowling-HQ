from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.auth import hash_password, verify_password

client = TestClient(app)


class FakeAuthRepository:
    def __init__(self) -> None:
        self.users: dict[str, dict] = {}

    def get_by_email(self, email: str) -> Optional[dict]:
        return self.users.get(email)

    def insert_user(
        self,
        user_id: UUID,
        email: str,
        display_name: str,
        password_hash: str,
    ) -> dict:
        row = {
            "id": user_id,
            "email": email,
            "display_name": display_name,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc),
        }
        self.users[email] = row
        return row


@pytest.fixture
def fake_auth_repo(
    monkeypatch: pytest.MonkeyPatch,
) -> FakeAuthRepository:
    fake = FakeAuthRepository()
    monkeypatch.setattr(
        "src.services.auth.get_auth_repository",
        lambda: fake,
    )
    return fake


def test_register_creates_user(
    fake_auth_repo: FakeAuthRepository,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "player@example.com",
            "display_name": "Player One",
            "password": "supersecret",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "player@example.com"
    assert payload["display_name"] == "Player One"
    assert "password" not in payload


def test_register_duplicate_returns_409(
    fake_auth_repo: FakeAuthRepository,
) -> None:
    body = {
        "email": "dupe@example.com",
        "display_name": "Dupe",
        "password": "supersecret",
    }
    first = client.post("/api/v1/auth/register", json=body)
    assert first.status_code == 201
    second = client.post("/api/v1/auth/register", json=body)
    assert second.status_code == 409


def test_login_with_correct_password(
    fake_auth_repo: FakeAuthRepository,
) -> None:
    fake_auth_repo.insert_user(
        user_id=uuid4(),
        email="login@example.com",
        display_name="Login User",
        password_hash=hash_password("supersecret"),
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "supersecret"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


def test_login_with_wrong_password(
    fake_auth_repo: FakeAuthRepository,
) -> None:
    fake_auth_repo.insert_user(
        user_id=uuid4(),
        email="login2@example.com",
        display_name="Login User",
        password_hash=hash_password("supersecret"),
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login2@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_hash_password_round_trip() -> None:
    password_hash = hash_password("supersecret")

    assert password_hash != "supersecret"
    assert verify_password("supersecret", password_hash)
