from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.models.games import (
    FramesResponse,
    GameFromThrowsRequest,
    GamesResponse,
)
from src.models.import_scores import ScoreImportResult
from src.services.games import (
    add_game_from_throws,
    add_games,
    get_game_frames,
    get_session_games,
    import_scores,
)

router = APIRouter(prefix="/api/v1/sessions", tags=["games"])


class AddGamesRequest(BaseModel):
    scores: list[int] = Field(min_length=1)


class ImportScoresRequest(BaseModel):
    csv_text: str
    source: str = "generic"


@router.get("/{session_id}/games", response_model=GamesResponse)
def read_session_games(session_id: UUID) -> GamesResponse:
    return get_session_games(session_id)


@router.post("/{session_id}/games", response_model=GamesResponse)
def create_session_games(
    session_id: UUID,
    payload: AddGamesRequest,
) -> GamesResponse:
    try:
        return add_games(session_id, payload.scores)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.post(
    "/{session_id}/games/from-throws",
    response_model=FramesResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_game_from_throws(
    session_id: UUID,
    payload: GameFromThrowsRequest,
) -> FramesResponse:
    """Record a game by submitting throw values; score is computed."""
    try:
        game, frames = add_game_from_throws(session_id, payload.throws)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    return FramesResponse(game_id=game.id, frames=frames)


@router.get(
    "/{session_id}/games/{game_id}/frames",
    response_model=FramesResponse,
)
def read_game_frames(session_id: UUID, game_id: UUID) -> FramesResponse:
    """Return the frame-by-frame breakdown for a recorded game."""
    frames = get_game_frames(game_id)
    return FramesResponse(game_id=game_id, frames=frames)


@router.post(
    "/{session_id}/import-scores",
    response_model=ScoreImportResult,
)
def import_session_scores(
    session_id: UUID,
    payload: ImportScoresRequest,
) -> ScoreImportResult:
    scores, errors = import_scores(
        session_id,
        payload.csv_text,
        payload.source,
    )
    if not scores:
        detail = "; ".join(errors) if errors else "No scores parsed"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
    return ScoreImportResult(
        session_id=session_id,
        games_imported=len(scores),
        scores=scores,
        errors=errors,
    )
