from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.arsenal import BallItem
from src.services.ghost_bowler import ScoredGame

client = TestClient(app)


class FakeGhostRepo:
    def __init__(self) -> None:
        self.saved = []

    def list_games(self, user_id: UUID) -> list[ScoredGame]:
        return [
            ScoredGame(score=205, session_type='house', started_at=datetime.now(timezone.utc)),
            ScoredGame(score=188, session_type='sport', started_at=datetime.now(timezone.utc)),
            ScoredGame(score=176, session_type='dry', started_at=datetime.now(timezone.utc)),
        ]

    def save_baseline(self, user_id: UUID, baseline) -> None:
        self.saved.append((user_id, baseline))


class FakePatternRepo:
    def __init__(self) -> None:
        self.logged = []

    def log_analysis(self, user_id: UUID, response) -> None:
        self.logged.append((user_id, response))


class FakeSimulatorRepo:
    def __init__(self) -> None:
        self.logged = []

    def log_run(self, user_id: UUID, request, response) -> None:
        self.logged.append((user_id, request, response))


class FakeRecommendationRepo:
    def __init__(self, balls: list[BallItem]) -> None:
        self._balls = balls

    def get_arsenal_balls(self, user_id: UUID) -> list[BallItem]:
        return self._balls

    def get_catalog_balls(self) -> list[BallItem]:
        return self._balls

    def log_recommendation(self, **kwargs) -> None:
        return None


class FakeArsenalRepo:
    def __init__(self, balls: list[BallItem]) -> None:
        self._balls = balls

    def list_arsenal(self, user_id: UUID):
        return []

    def list_catalog(self):
        return self._balls

    def get_ball(self, ball_id: UUID):
        for ball in self._balls:
            if ball.id == ball_id:
                return ball
        return None


def make_ball(name: str = 'Storm Phaze II') -> BallItem:
    return BallItem(
        id=uuid4(),
        name=name,
        brand='Storm',
        coverstock='solid reactive',
        rg=2.48,
        differential=0.048,
        mass_bias=0.0,
        surface_grit=3000,
        weight_lbs=15,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def vertical_slice_mocks(monkeypatch: pytest.MonkeyPatch):
    balls = [make_ball()]
    monkeypatch.setattr('src.services.ghost_bowler.get_ghost_bowler_repository', lambda: FakeGhostRepo())
    monkeypatch.setattr('src.services.pattern_intelligence.get_pattern_analysis_repository', lambda: FakePatternRepo())
    monkeypatch.setattr('src.services.simulator.get_simulator_repository', lambda: FakeSimulatorRepo())
    monkeypatch.setattr('src.services.recommendations.get_recommendation_repository', lambda: FakeRecommendationRepo(balls))
    monkeypatch.setattr('src.services.arsenal.get_arsenal_repository', lambda: FakeArsenalRepo(balls))


def _pattern() -> dict:
    return {
        'name': 'House',
        'length_ft': 40,
        'volume_ml': 24,
        'asymmetry_index': 0.0,
        'front_oil_pct': 0.34,
        'mid_oil_pct': 0.33,
        'backend_oil_pct': 0.33,
        'lane_surface': 'synthetic',
    }


def _bowler() -> dict:
    return {
        'average': 190,
        'speed_mph': 17,
        'rev_rate': 350,
        'axis_rotation_deg': 45,
        'axis_tilt_deg': 15,
        'consistency': 0.75,
    }


def test_ghost_bowler_endpoints(vertical_slice_mocks) -> None:
    baseline = client.get('/api/v1/ghost-bowler')
    assert baseline.status_code == 200
    payload = baseline.json()
    assert payload['total_games'] == 3
    assert payload['overall']['average_score'] > 0

    compare = client.get('/api/v1/ghost-bowler/compare?current_average=200&condition_family=house')
    assert compare.status_code == 200
    assert compare.json()['trend'] in {'above_baseline', 'below_baseline', 'even'}


def test_pattern_analysis_endpoint(vertical_slice_mocks) -> None:
    response = client.post('/api/v1/patterns/analyze', json={'pattern': _pattern()})
    assert response.status_code == 200
    payload = response.json()
    assert payload['difficulty_score'] >= 1
    assert payload['breakpoint_board'] > 0


def test_simulator_endpoint(vertical_slice_mocks) -> None:
    response = client.post(
        '/api/v1/simulator/run',
        json={
            'pattern': _pattern(),
            'bowler': _bowler(),
            'ball': {
                'name': 'Storm Phaze II',
                'coverstock': 'solid reactive',
                'rg': 2.48,
                'differential': 0.048,
                'mass_bias': 0,
                'surface_grit': 3000,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['predicted_score'] > 0
    assert payload['confidence_high'] >= payload['confidence_low']


def test_arsenal_fit_endpoint(vertical_slice_mocks) -> None:
    response = client.post(
        '/api/v1/arsenal/fit',
        json={
            'pattern': _pattern(),
            'bowler': _bowler(),
            'top_n': 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload['recommendations']) == 1
    assert payload['recommendations'][0]['fit_score'] > 0


def test_commander_orchestration_endpoint(vertical_slice_mocks) -> None:
    response = client.post(
        '/api/v1/commander/recommendation',
        json={
            'pattern': _pattern(),
            'bowler': _bowler(),
            'top_n': 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['confidence'] > 0
    assert payload['opening_ball']['recommendations']
    assert payload['ghost_bowler']['overall']['average_score'] > 0
