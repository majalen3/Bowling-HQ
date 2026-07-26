from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.analytics import BallAverage

client = TestClient(app)


class FakeAnalyticsRepository:
    def __init__(
        self,
        games: list[dict],
        per_ball: list[BallAverage] | None = None,
    ) -> None:
        self._games = games
        self._per_ball = per_ball or []

    def get_games_with_sessions(self, user_id: UUID) -> list[dict]:
        return self._games

    def get_per_ball_averages(self, user_id: UUID) -> list[BallAverage]:
        return self._per_ball


def patch_repo(
    monkeypatch: pytest.MonkeyPatch,
    repo: FakeAnalyticsRepository,
) -> None:
    monkeypatch.setattr(
        "src.services.analytics.get_analytics_repository",
        lambda: repo,
    )


def test_summary_returns_correct_average(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_a = uuid4()
    session_b = uuid4()
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    games = [
        {
            "game_id": uuid4(),
            "score": 200,
            "session_id": session_a,
            "started_at": base,
            "location_name": "House",
        },
        {
            "game_id": uuid4(),
            "score": 180,
            "session_id": session_a,
            "started_at": base,
            "location_name": "House",
        },
        {
            "game_id": uuid4(),
            "score": 220,
            "session_id": session_b,
            "started_at": base + timedelta(days=1),
            "location_name": "Club",
        },
    ]
    patch_repo(monkeypatch, FakeAnalyticsRepository(games))
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_average"] == round((200 + 180 + 220) / 3, 2)
    assert payload["high_game"] == 220
    assert payload["total_games"] == 3
    assert payload["total_sessions"] == 2
    assert payload["recent_trend"][0]["location_name"] == "Club"


def test_summary_with_no_games_returns_zeros(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_repo(monkeypatch, FakeAnalyticsRepository([]))
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_average"] == 0.0
    assert payload["high_game"] == 0
    assert payload["total_games"] == 0
    assert payload["total_sessions"] == 0
    assert payload["recent_trend"] == []
    assert payload["per_ball_averages"] == []
