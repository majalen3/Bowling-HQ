from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.games import FrameItem, GameItem
from src.services.games import parse_csv_scores, parse_throws_to_frames

client = TestClient(app)

SESSION_ID = UUID("11111111-1111-1111-1111-111111111111")


class FakeGamesRepository:
    def __init__(self) -> None:
        self.games: dict[UUID, list[GameItem]] = {}
        self.frames: dict[UUID, list[FrameItem]] = {}

    def add_games(
        self,
        session_id: UUID,
        scores: list[int],
    ) -> list[GameItem]:
        existing = self.games.setdefault(session_id, [])
        next_number = len(existing) + 1
        created = []
        for offset, score in enumerate(scores):
            item = GameItem(
                id=uuid4(),
                session_id=session_id,
                game_number=next_number + offset,
                score=score,
                created_at=datetime.now(timezone.utc),
            )
            existing.append(item)
            created.append(item)
        return created

    def list_games(self, session_id: UUID) -> list[GameItem]:
        return list(self.games.get(session_id, []))

    def add_game_with_frames(
        self,
        session_id: UUID,
        score: int,
        frame_dicts: list[dict],
    ) -> tuple[GameItem, list[FrameItem]]:
        existing = self.games.setdefault(session_id, [])
        game_id = uuid4()
        game = GameItem(
            id=game_id,
            session_id=session_id,
            game_number=len(existing) + 1,
            score=score,
            created_at=datetime.now(timezone.utc),
        )
        existing.append(game)
        frame_items: list[FrameItem] = []
        for fd in frame_dicts:
            fi = FrameItem(
                id=uuid4(),
                game_id=game_id,
                frame_number=fd["frame_number"],
                ball1=fd["ball1"],
                ball2=fd.get("ball2"),
                ball3=fd.get("ball3"),
                is_strike=fd["is_strike"],
                is_spare=fd["is_spare"],
            )
            self.frames.setdefault(game_id, []).append(fi)
            frame_items.append(fi)
        return game, frame_items

    def list_frames(self, game_id: UUID) -> list[FrameItem]:
        return list(self.frames.get(game_id, []))


@pytest.fixture
def fake_games_repo(
    monkeypatch: pytest.MonkeyPatch,
) -> FakeGamesRepository:
    fake = FakeGamesRepository()
    monkeypatch.setattr(
        "src.services.games.get_games_repository",
        lambda: fake,
    )
    return fake


def test_post_games_returns_sequence(
    fake_games_repo: FakeGamesRepository,
) -> None:
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/games",
        json={"scores": [180, 200]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert [g["game_number"] for g in payload["games"]] == [1, 2]

    second = client.post(
        f"/api/v1/sessions/{SESSION_ID}/games",
        json={"scores": [210]},
    )
    assert second.status_code == 200
    numbers = [g["game_number"] for g in second.json()["games"]]
    assert numbers == [1, 2, 3]
    assert second.json()["average"] == round((180 + 200 + 210) / 3, 2)


def test_post_games_rejects_out_of_range(
    fake_games_repo: FakeGamesRepository,
) -> None:
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/games",
        json={"scores": [301]},
    )
    assert response.status_code == 422


def test_get_games_returns_list(
    fake_games_repo: FakeGamesRepository,
) -> None:
    client.post(
        f"/api/v1/sessions/{SESSION_ID}/games",
        json={"scores": [150, 160]},
    )
    response = client.get(f"/api/v1/sessions/{SESSION_ID}/games")
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_import_lanetalk_csv(
    fake_games_repo: FakeGamesRepository,
) -> None:
    csv_text = "Bowler,Game 1,Game 2,Game 3\nAlex,201,178,225\n"
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/import-scores",
        json={"csv_text": csv_text, "source": "lanetalk"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["scores"] == [201, 178, 225]
    assert payload["games_imported"] == 3


def test_import_lanetrax_csv(
    fake_games_repo: FakeGamesRepository,
) -> None:
    # Shot-by-shot: a clean game (all strikes) scores 300.
    rows = ["Game,Frame,Shot,Pins"]
    for frame in range(1, 10):
        rows.append(f"1,{frame},1,10")
    rows.append("1,10,1,10")
    rows.append("1,10,2,10")
    rows.append("1,10,3,10")
    csv_text = "\n".join(rows) + "\n"
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/import-scores",
        json={"csv_text": csv_text, "source": "lanetrak"},
    )
    assert response.status_code == 200
    assert response.json()["scores"] == [300]


def test_import_invalid_csv_returns_422(
    fake_games_repo: FakeGamesRepository,
) -> None:
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/import-scores",
        json={"csv_text": "not,real,data\nfoo,bar,baz\n"},
    )
    assert response.status_code == 422


def test_import_partial_errors_are_non_fatal(
    fake_games_repo: FakeGamesRepository,
) -> None:
    csv_text = "Score\n180\n999\n200\n"
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/import-scores",
        json={"csv_text": csv_text, "source": "generic"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["scores"] == [180, 200]
    assert payload["errors"]


def test_parse_csv_scores_simple() -> None:
    assert parse_csv_scores("Score\n150\n175\n") == [150, 175]


def test_parse_csv_scores_raises_on_garbage() -> None:
    with pytest.raises(ValueError):
        parse_csv_scores("Name\nfoo\nbar\n")


# ── Frame entry tests ────────────────────────────────────────────────────────


# Perfect game: 12 strikes → 300
PERFECT_GAME_THROWS = [10] * 12

# All gutter balls: 20 zeros → 0
GUTTER_GAME_THROWS = [0] * 20

# Spare in every frame then a bonus strike in 10th:
# frames 1-9: 5,5  (18 throws)  + 10th: 5,5,5 (3 throws) = 21 throws → 150
SPARE_GAME_THROWS = [5, 5] * 9 + [5, 5, 5]


def test_parse_throws_to_frames_perfect_game() -> None:
    frames = parse_throws_to_frames(PERFECT_GAME_THROWS)
    assert len(frames) == 10
    assert all(f["is_strike"] for f in frames)
    assert frames[9]["ball3"] == 10  # 10th frame bonus throw


def test_parse_throws_to_frames_gutter_game() -> None:
    frames = parse_throws_to_frames(GUTTER_GAME_THROWS)
    assert len(frames) == 10
    assert all(not f["is_strike"] and not f["is_spare"] for f in frames)
    assert all(f["ball1"] == 0 and f["ball2"] == 0 for f in frames)


def test_parse_throws_to_frames_spare_game() -> None:
    frames = parse_throws_to_frames(SPARE_GAME_THROWS)
    assert len(frames) == 10
    assert all(f["is_spare"] for f in frames)


def test_post_from_throws_perfect_game(
    fake_games_repo: FakeGamesRepository,
) -> None:
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/games/from-throws",
        json={"throws": PERFECT_GAME_THROWS},
    )
    assert response.status_code == 201
    payload = response.json()
    assert "game_id" in payload
    assert len(payload["frames"]) == 10
    # Every frame in a perfect game is a strike
    assert all(f["is_strike"] for f in payload["frames"])
    # The game should be stored with score 300
    assert fake_games_repo.games[SESSION_ID][0].score == 300


def test_post_from_throws_gutter_game(
    fake_games_repo: FakeGamesRepository,
) -> None:
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/games/from-throws",
        json={"throws": GUTTER_GAME_THROWS},
    )
    assert response.status_code == 201
    assert fake_games_repo.games[SESSION_ID][0].score == 0


def test_post_from_throws_rejects_invalid_throw(
    fake_games_repo: FakeGamesRepository,
) -> None:
    bad_throws = [10] * 11 + [11]  # 11 is out of range
    response = client.post(
        f"/api/v1/sessions/{SESSION_ID}/games/from-throws",
        json={"throws": bad_throws},
    )
    assert response.status_code == 422


def test_get_game_frames_returns_breakdown(
    fake_games_repo: FakeGamesRepository,
) -> None:
    post_resp = client.post(
        f"/api/v1/sessions/{SESSION_ID}/games/from-throws",
        json={"throws": PERFECT_GAME_THROWS},
    )
    assert post_resp.status_code == 201
    game_id = post_resp.json()["game_id"]

    get_resp = client.get(
        f"/api/v1/sessions/{SESSION_ID}/games/{game_id}/frames"
    )
    assert get_resp.status_code == 200
    payload = get_resp.json()
    assert payload["game_id"] == game_id
    assert len(payload["frames"]) == 10
