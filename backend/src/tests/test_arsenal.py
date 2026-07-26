from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.arsenal import BallCreate, BallItem, UserArsenalBall
from src.services.arsenal import BALL_CATALOG_SEED

client = TestClient(app)


class FakeArsenalRepository:
    def __init__(self) -> None:
        self.catalog: dict[UUID, BallItem] = {}
        self.arsenal: dict[UUID, UserArsenalBall] = {}
        self.ensure_catalog(BALL_CATALOG_SEED)

    def list_catalog(self) -> list[BallItem]:
        return list(self.catalog.values())

    def ensure_catalog(self, seed: list[dict]) -> None:
        if self.catalog:
            return
        for spec in seed:
            ball = BallItem(
                id=uuid4(),
                name=spec["name"],
                brand=spec["brand"],
                coverstock=spec["coverstock"],
                rg=spec["rg"],
                differential=spec["differential"],
                mass_bias=spec.get("mass_bias", 0.0),
                surface_grit=spec.get("surface_grit", 3000),
                weight_lbs=spec.get("weight_lbs", 15),
                created_at=datetime.now(timezone.utc),
            )
            self.catalog[ball.id] = ball

    def get_ball(self, ball_id: UUID) -> Optional[BallItem]:
        return self.catalog.get(ball_id)

    def create_ball(self, payload: BallCreate) -> BallItem:
        ball = BallItem(
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            **payload.model_dump(),
        )
        self.catalog[ball.id] = ball
        return ball

    def list_arsenal(self, user_id: UUID) -> list[UserArsenalBall]:
        return list(self.arsenal.values())

    def add_to_arsenal(
        self,
        user_id: UUID,
        ball_id: UUID,
        notes: Optional[str],
    ) -> UserArsenalBall:
        entry = UserArsenalBall(
            id=uuid4(),
            ball=self.catalog[ball_id],
            notes=notes,
            added_at=datetime.now(timezone.utc),
        )
        self.arsenal[entry.id] = entry
        return entry

    def remove_from_arsenal(
        self,
        user_id: UUID,
        arsenal_id: UUID,
    ) -> bool:
        return self.arsenal.pop(arsenal_id, None) is not None


@pytest.fixture
def fake_arsenal_repo(
    monkeypatch: pytest.MonkeyPatch,
) -> FakeArsenalRepository:
    fake = FakeArsenalRepository()
    monkeypatch.setattr(
        "src.services.arsenal.get_arsenal_repository",
        lambda: fake,
    )
    return fake


def _ball_payload() -> dict:
    return {
        "name": "Test Ball",
        "brand": "TestBrand",
        "coverstock": "solid reactive",
        "rg": 2.48,
        "differential": 0.05,
        "notes": "fresh oil ball",
    }


def test_get_catalog_returns_seeded_balls(
    fake_arsenal_repo: FakeArsenalRepository,
) -> None:
    response = client.get("/api/v1/arsenal/catalog")
    assert response.status_code == 200
    assert len(response.json()) == len(BALL_CATALOG_SEED)


def test_post_arsenal_creates_entry(
    fake_arsenal_repo: FakeArsenalRepository,
) -> None:
    response = client.post("/api/v1/arsenal", json=_ball_payload())
    assert response.status_code == 201
    payload = response.json()
    assert payload["ball"]["name"] == "Test Ball"
    assert payload["notes"] == "fresh oil ball"


def test_get_arsenal_returns_balls(
    fake_arsenal_repo: FakeArsenalRepository,
) -> None:
    client.post("/api/v1/arsenal", json=_ball_payload())
    response = client.get("/api/v1/arsenal")
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_delete_arsenal_removes_entry(
    fake_arsenal_repo: FakeArsenalRepository,
) -> None:
    created = client.post("/api/v1/arsenal", json=_ball_payload())
    arsenal_id = created.json()["id"]
    response = client.delete(f"/api/v1/arsenal/{arsenal_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True
    assert client.get("/api/v1/arsenal").json()["count"] == 0


def test_delete_missing_arsenal_returns_404(
    fake_arsenal_repo: FakeArsenalRepository,
) -> None:
    response = client.delete(f"/api/v1/arsenal/{uuid4()}")
    assert response.status_code == 404
