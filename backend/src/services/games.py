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
from src.models.games import GameItem, GamesResponse

MIN_SCORE = 0
MAX_SCORE = 300


class GamesRepository(Protocol):
    def add_games(
        self,
        session_id: UUID,
        scores: list[int],
    ) -> list[GameItem]:
        ...

    def list_games(self, session_id: UUID) -> list[GameItem]:
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


__all__ = [
    "GamesRepository",
    "PostgresGamesRepository",
    "get_games_repository",
    "add_games",
    "get_session_games",
    "import_scores",
    "parse_csv_scores",
    "parse_csv_scores_with_errors",
    "validate_scores",
]
