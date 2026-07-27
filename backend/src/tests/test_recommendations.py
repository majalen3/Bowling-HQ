from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.arsenal import BallItem

client = TestClient(app)


def make_ball(
    name: str,
    coverstock: str,
    rg: float,
    differential: float,
    surface_grit: int = 3000,
) -> BallItem:
    return BallItem(
        id=uuid4(),
        name=name,
        brand="TestBrand",
        coverstock=coverstock,
        rg=rg,
        differential=differential,
        mass_bias=0.0,
        surface_grit=surface_grit,
        weight_lbs=15,
        created_at=datetime.now(timezone.utc),
    )


class FakeRecommendationRepository:
    def __init__(
        self,
        arsenal_balls: list[BallItem],
        catalog_balls: Optional[list[BallItem]] = None,
    ) -> None:
        self.arsenal_balls = arsenal_balls
        self.catalog_balls = catalog_balls or []
        self.logged: list[dict] = []

    def get_arsenal_balls(self, user_id: UUID) -> list[BallItem]:
        return self.arsenal_balls

    def get_catalog_balls(self) -> list[BallItem]:
        return self.catalog_balls

    def log_recommendation(self, **kwargs) -> None:
        self.logged.append(kwargs)


def patch_repo(
    monkeypatch: pytest.MonkeyPatch,
    repo: FakeRecommendationRepository,
) -> None:
    monkeypatch.setattr(
        "src.services.recommendations.get_recommendation_repository",
        lambda: repo,
    )


def _request(pattern: dict, bowler: dict, top_n: int = 3) -> dict:
    return {"pattern": pattern, "bowler": bowler, "top_n": top_n}


HEAVY_PATTERN = {"name": "Heavy", "length_ft": 42.0, "volume_ml": 30.0}
DRY_PATTERN = {"name": "Dry", "length_ft": 36.0, "volume_ml": 18.0}
NEUTRAL_PATTERN = {"name": "Neutral", "length_ft": 39.0, "volume_ml": 24.0}
BALANCED_BOWLER = {"average": 190, "speed_mph": 17.0, "rev_rate": 350}


def _score_for(payload: dict, ball_name: str) -> float:
    for rec in payload["recommendations"]:
        if rec["ball_name"] == ball_name:
            return rec["fit_score"]
    raise AssertionError(f"{ball_name} not found")


def test_returns_ranked_recommendations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    balls = [
        make_ball("Solid A", "solid reactive", 2.48, 0.05),
        make_ball("Pearl B", "pearl reactive", 2.52, 0.045),
        make_ball("Urethane C", "urethane", 2.55, 0.028),
    ]
    repo = FakeRecommendationRepository(balls)
    patch_repo(monkeypatch, repo)
    response = client.post(
        "/api/v1/recommendations/opening-ball",
        json=_request(NEUTRAL_PATTERN, BALANCED_BOWLER, top_n=2),
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recommendations"]) == 2
    assert [r["rank"] for r in payload["recommendations"]] == [1, 2]
    assert repo.logged
    assert payload["recommendations"][0]["reasoning"]


def test_solid_beats_pearl_on_heavy_oil(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    balls = [
        make_ball("Solid A", "solid reactive", 2.48, 0.05, 1500),
        make_ball("Pearl B", "pearl reactive", 2.52, 0.045, 4000),
    ]
    patch_repo(monkeypatch, FakeRecommendationRepository(balls))
    response = client.post(
        "/api/v1/recommendations/opening-ball",
        json=_request(HEAVY_PATTERN, BALANCED_BOWLER),
    )
    payload = response.json()
    assert _score_for(payload, "Solid A") > _score_for(payload, "Pearl B")
    assert payload["recommendations"][0]["ball_name"] == "Solid A"


def test_pearl_beats_solid_on_dry_lane(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    balls = [
        make_ball("Solid A", "solid reactive", 2.48, 0.05, 1500),
        make_ball("Pearl B", "pearl reactive", 2.54, 0.045, 4000),
    ]
    patch_repo(monkeypatch, FakeRecommendationRepository(balls))
    response = client.post(
        "/api/v1/recommendations/opening-ball",
        json=_request(DRY_PATTERN, BALANCED_BOWLER),
    )
    payload = response.json()
    assert _score_for(payload, "Pearl B") > _score_for(payload, "Solid A")


def test_rev_dominant_prefers_higher_rg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    balls = [
        make_ball("Low RG", "hybrid reactive", 2.47, 0.055),
        make_ball("High RG", "hybrid reactive", 2.54, 0.030),
    ]
    patch_repo(monkeypatch, FakeRecommendationRepository(balls))
    rev_bowler = {"average": 200, "speed_mph": 13.0, "rev_rate": 450}
    response = client.post(
        "/api/v1/recommendations/opening-ball",
        json=_request(NEUTRAL_PATTERN, rev_bowler),
    )
    payload = response.json()
    assert payload["bowler_type"] == "rev_dominant"
    assert payload["recommendations"][0]["ball_name"] == "High RG"


def test_speed_dominant_prefers_lower_rg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    balls = [
        make_ball("Low RG", "hybrid reactive", 2.47, 0.050),
        make_ball("High RG", "hybrid reactive", 2.56, 0.030),
    ]
    patch_repo(monkeypatch, FakeRecommendationRepository(balls))
    speed_bowler = {"average": 180, "speed_mph": 17.0, "rev_rate": 200}
    response = client.post(
        "/api/v1/recommendations/opening-ball",
        json=_request(NEUTRAL_PATTERN, speed_bowler),
    )
    payload = response.json()
    assert payload["bowler_type"] == "speed_dominant"
    assert payload["recommendations"][0]["ball_name"] == "Low RG"


def test_rule_of_31_breakpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    balls = [make_ball("Solid A", "solid reactive", 2.48, 0.05)]
    patch_repo(monkeypatch, FakeRecommendationRepository(balls))
    pattern = {"name": "P40", "length_ft": 40.0, "volume_ml": 24.0}
    response = client.post(
        "/api/v1/recommendations/opening-ball",
        json=_request(pattern, BALANCED_BOWLER),
    )
    assert response.json()["breakpoint_board"] == 9.0


def test_empty_arsenal_falls_back_to_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    catalog = [make_ball("Catalog Ball", "solid reactive", 2.48, 0.05)]
    repo = FakeRecommendationRepository([], catalog_balls=catalog)
    patch_repo(monkeypatch, repo)
    response = client.post(
        "/api/v1/recommendations/opening-ball",
        json=_request(NEUTRAL_PATTERN, BALANCED_BOWLER),
    )
    payload = response.json()
    assert len(payload["recommendations"]) == 1
    assert payload["recommendations"][0]["ball_name"] == "Catalog Ball"
