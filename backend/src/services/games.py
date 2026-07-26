from __future__ import annotations

import csv
import io
import re
from functools import lru_cache
from typing import Optional, Protocol
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from src.config import get_settings
from src.models.games import FrameItem, GameItem, GamesResponse

MIN_SCORE = 0
MAX_SCORE = 300
MIN_THROW = 0
MAX_THROW = 10


class GamesRepository(Protocol):
    def add_games(
        self,
        session_id: UUID,
        scores: list[int],
    ) -> list[GameItem]:
        ...

    def list_games(self, session_id: UUID) -> list[GameItem]:
        ...

    def add_game_with_frames(
        self,
        session_id: UUID,
        score: int,
        frame_dicts: list[dict],
    ) -> tuple[GameItem, list[FrameItem]]:
        ...

    def list_frames(self, game_id: UUID) -> list[FrameItem]:
        ...


class PostgresGamesRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def add_games(
        self,
        session_id: UUID,
        scores: list[int],
    ) -> list[GameItem]:
        created: list[GameItem] = []
        with connect(self.postgres_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COALESCE(MAX(game_number), 0) AS max_number
                    FROM games
                    WHERE session_id = %s
                    """,
                    (session_id,),
                )
                row = cursor.fetchone()
                next_number = (row["max_number"] if row else 0) + 1
                for offset, score in enumerate(scores):
                    game_id = uuid4()
                    cursor.execute(
                        """
                        INSERT INTO games (
                            id, session_id, game_number, score
                        ) VALUES (%s, %s, %s, %s)
                        RETURNING id, session_id, game_number, score,
                            created_at
                        """,
                        (
                            game_id,
                            session_id,
                            next_number + offset,
                            score,
                        ),
                    )
                    created.append(
                        GameItem.model_validate(cursor.fetchone())
                    )
        return created

    def list_games(self, session_id: UUID) -> list[GameItem]:
        with connect(self.postgres_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, session_id, game_number, score, created_at
                    FROM games
                    WHERE session_id = %s
                    ORDER BY game_number ASC
                    """,
                    (session_id,),
                )
                rows = cursor.fetchall()
        return [GameItem.model_validate(row) for row in rows]

    def add_game_with_frames(
        self,
        session_id: UUID,
        score: int,
        frame_dicts: list[dict],
    ) -> tuple[GameItem, list[FrameItem]]:
        with connect(self.postgres_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COALESCE(MAX(game_number), 0) AS max_number
                    FROM games
                    WHERE session_id = %s
                    """,
                    (session_id,),
                )
                row = cursor.fetchone()
                next_number = (row["max_number"] if row else 0) + 1
                game_id = uuid4()
                cursor.execute(
                    """
                    INSERT INTO games (id, session_id, game_number, score)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, session_id, game_number, score, created_at
                    """,
                    (game_id, session_id, next_number, score),
                )
                game = GameItem.model_validate(cursor.fetchone())
                frames: list[FrameItem] = []
                for fd in frame_dicts:
                    frame_id = uuid4()
                    cursor.execute(
                        """
                        INSERT INTO frames (
                            id, game_id, frame_number,
                            ball1, ball2, ball3,
                            is_strike, is_spare
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, game_id, frame_number,
                            ball1, ball2, ball3,
                            is_strike, is_spare
                        """,
                        (
                            frame_id,
                            game_id,
                            fd["frame_number"],
                            fd["ball1"],
                            fd.get("ball2"),
                            fd.get("ball3"),
                            fd["is_strike"],
                            fd["is_spare"],
                        ),
                    )
                    frames.append(FrameItem.model_validate(cursor.fetchone()))
        return game, frames

    def list_frames(self, game_id: UUID) -> list[FrameItem]:
        with connect(self.postgres_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, game_id, frame_number,
                        ball1, ball2, ball3,
                        is_strike, is_spare
                    FROM frames
                    WHERE game_id = %s
                    ORDER BY frame_number ASC
                    """,
                    (game_id,),
                )
                rows = cursor.fetchall()
        return [FrameItem.model_validate(row) for row in rows]


@lru_cache
def get_games_repository() -> GamesRepository:
    return PostgresGamesRepository(postgres_url=get_settings().postgres_url)


def _build_response(
    session_id: UUID,
    games: list[GameItem],
) -> GamesResponse:
    count = len(games)
    average = (
        round(sum(game.score for game in games) / count, 2)
        if count
        else 0.0
    )
    return GamesResponse(
        session_id=session_id,
        games=games,
        count=count,
        average=average,
    )


def validate_scores(scores: list[int]) -> None:
    for score in scores:
        if score < MIN_SCORE or score > MAX_SCORE:
            raise ValueError(
                f"Score {score} is out of range (0-300)"
            )


def add_games(
    session_id: UUID,
    scores: list[int],
    repository: Optional[GamesRepository] = None,
) -> GamesResponse:
    validate_scores(scores)
    repo = repository or get_games_repository()
    repo.add_games(session_id, scores)
    return _build_response(session_id, repo.list_games(session_id))


def get_session_games(
    session_id: UUID,
    repository: Optional[GamesRepository] = None,
) -> GamesResponse:
    repo = repository or get_games_repository()
    return _build_response(session_id, repo.list_games(session_id))


def _score_game(throws: list[int]) -> int:
    """Compute a standard 10-pin bowling score from a list of throws."""
    score = 0
    index = 0
    for _frame in range(10):
        if index >= len(throws):
            break
        first = throws[index]
        if first == 10:
            bonus = throws[index + 1: index + 3]
            score += 10 + sum(bonus)
            index += 1
        else:
            second = throws[index + 1] if index + 1 < len(throws) else 0
            if first + second == 10:
                third = throws[index + 2] if index + 2 < len(throws) else 0
                score += 10 + third
            else:
                score += first + second
            index += 2
    return score


def _find_column(fieldnames: list[str], *needles: str) -> Optional[str]:
    for name in fieldnames:
        lowered = name.strip().lower()
        if any(needle in lowered for needle in needles):
            return name
    return None


def _game_columns(fieldnames: list[str]) -> list[str]:
    pattern = re.compile(r"^game\s*\d+$", re.IGNORECASE)
    return [name for name in fieldnames if pattern.match(name.strip())]


def _coerce_score(raw: str) -> int:
    value = int(float(raw.strip()))
    if value < MIN_SCORE or value > MAX_SCORE:
        raise ValueError(f"Score {value} out of range")
    return value


def _parse_wide(
    rows: list[dict[str, str]],
    columns: list[str],
) -> tuple[list[int], list[str]]:
    scores: list[int] = []
    errors: list[str] = []
    for row in rows:
        for column in columns:
            raw = (row.get(column) or "").strip()
            if not raw:
                continue
            try:
                scores.append(_coerce_score(raw))
            except (ValueError, TypeError):
                errors.append(f"Invalid score '{raw}' in column {column}")
    return scores, errors


def _parse_lanetrax(
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> tuple[list[int], list[str]]:
    game_col = _find_column(fieldnames, "game")
    pins_col = _find_column(fieldnames, "pins", "pinfall", "count")
    total_col = _find_column(fieldnames, "total", "score")
    scores: list[int] = []
    errors: list[str] = []
    grouped: dict[str, list[int]] = {}
    order: list[str] = []
    for row in rows:
        key = (row.get(game_col) if game_col else None) or "1"
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        raw = ""
        if pins_col:
            raw = (row.get(pins_col) or "").strip()
        if not raw and total_col:
            raw = (row.get(total_col) or "").strip()
        if not raw:
            continue
        try:
            grouped[key].append(int(float(raw)))
        except (ValueError, TypeError):
            errors.append(f"Invalid pin value '{raw}' in game {key}")
    for key in order:
        throws = grouped[key]
        if not throws:
            continue
        total = _score_game(throws)
        if total < MIN_SCORE or total > MAX_SCORE:
            errors.append(
                f"Computed score {total} out of range for game {key}"
            )
            continue
        scores.append(total)
    return scores, errors


def _parse_simple(
    rows: list[dict[str, str]],
    score_col: str,
) -> tuple[list[int], list[str]]:
    scores: list[int] = []
    errors: list[str] = []
    for row in rows:
        raw = (row.get(score_col) or "").strip()
        if not raw:
            continue
        try:
            scores.append(_coerce_score(raw))
        except (ValueError, TypeError):
            errors.append(f"Invalid score '{raw}'")
    return scores, errors


def _parse_plain_numbers(text: str) -> tuple[list[int], list[str]]:
    scores: list[int] = []
    errors: list[str] = []
    tokens = re.split(r"[\s,;]+", text.strip())
    for token in tokens:
        if not token:
            continue
        try:
            scores.append(_coerce_score(token))
        except (ValueError, TypeError):
            errors.append(f"Invalid score '{token}'")
    return scores, errors


def parse_csv_scores_with_errors(
    csv_text: str,
    source: Optional[str] = None,
) -> tuple[list[int], list[str]]:
    text = (csv_text or "").strip()
    if not text:
        return [], ["No content provided"]
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = reader.fieldnames or []
    has_header = any(
        not name.strip().lstrip("-").isdigit()
        for name in fieldnames
    )
    if not fieldnames or not has_header:
        return _parse_plain_numbers(text)

    rows = list(reader)
    game_cols = _game_columns(fieldnames)
    if game_cols:
        return _parse_wide(rows, game_cols)
    if _find_column(fieldnames, "frame", "shot"):
        return _parse_lanetrax(rows, fieldnames)
    score_col = _find_column(fieldnames, "score", "total")
    if score_col:
        return _parse_simple(rows, score_col)
    return _parse_plain_numbers(text)


def parse_csv_scores(
    csv_text: str,
    source: Optional[str] = None,
) -> list[int]:
    scores, errors = parse_csv_scores_with_errors(csv_text, source)
    if not scores:
        message = "; ".join(errors) if errors else "No scores found"
        raise ValueError(f"Could not parse any scores: {message}")
    return scores


def import_scores(
    session_id: UUID,
    csv_text: str,
    source: Optional[str] = None,
    repository: Optional[GamesRepository] = None,
) -> tuple[list[int], list[str]]:
    scores, errors = parse_csv_scores_with_errors(csv_text, source)
    if scores:
        repo = repository or get_games_repository()
        repo.add_games(session_id, scores)
    return scores, errors


def validate_throws(throws: list[int]) -> None:
    """Validate that every throw value is in the 0–10 range."""
    for throw in throws:
        if throw < MIN_THROW or throw > MAX_THROW:
            raise ValueError(
                f"Throw value {throw} is out of range (0-10)"
            )


def parse_throws_to_frames(throws: list[int]) -> list[dict]:
    """Convert an ordered list of throws into frame-by-frame dicts."""
    frames: list[dict] = []
    i = 0
    for frame_num in range(1, 11):
        if i >= len(throws):
            break
        ball1 = throws[i]
        if frame_num < 10:
            if ball1 == 10:
                frames.append(
                    {
                        "frame_number": frame_num,
                        "ball1": 10,
                        "ball2": None,
                        "ball3": None,
                        "is_strike": True,
                        "is_spare": False,
                    }
                )
                i += 1
            else:
                ball2 = throws[i + 1] if i + 1 < len(throws) else 0
                is_spare = (ball1 + ball2) == 10
                frames.append(
                    {
                        "frame_number": frame_num,
                        "ball1": ball1,
                        "ball2": ball2,
                        "ball3": None,
                        "is_strike": False,
                        "is_spare": is_spare,
                    }
                )
                i += 2
        else:
            # 10th frame: up to 3 throws
            ball2 = throws[i + 1] if i + 1 < len(throws) else 0
            ball3 = throws[i + 2] if i + 2 < len(throws) else None
            is_strike = ball1 == 10
            is_spare = not is_strike and (ball1 + ball2) == 10
            frames.append(
                {
                    "frame_number": 10,
                    "ball1": ball1,
                    "ball2": ball2,
                    "ball3": ball3,
                    "is_strike": is_strike,
                    "is_spare": is_spare,
                }
            )
    return frames


def add_game_from_throws(
    session_id: UUID,
    throws: list[int],
    repository: Optional[GamesRepository] = None,
) -> tuple[GameItem, list[FrameItem]]:
    validate_throws(throws)
    score = _score_game(throws)
    if score < MIN_SCORE or score > MAX_SCORE:
        raise ValueError(f"Computed score {score} is out of range (0-300)")
    frame_dicts = parse_throws_to_frames(throws)
    repo = repository or get_games_repository()
    return repo.add_game_with_frames(session_id, score, frame_dicts)


def get_game_frames(
    game_id: UUID,
    repository: Optional[GamesRepository] = None,
) -> list[FrameItem]:
    repo = repository or get_games_repository()
    return repo.list_frames(game_id)


__all__ = [
    "GamesRepository",
    "PostgresGamesRepository",
    "get_games_repository",
    "add_games",
    "add_game_from_throws",
    "get_game_frames",
    "get_session_games",
    "import_scores",
    "parse_csv_scores",
    "parse_csv_scores_with_errors",
    "parse_throws_to_frames",
    "validate_scores",
    "validate_throws",
]
