from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.models.session_progress import (
    SessionCreateRequest,
    SessionProgressItem,
    SessionProgressSnapshot,
)
from src.services.session_progress import (
    finish_session,
    get_session_progress_snapshot,
    start_session,
)

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.get("/progress", response_model=SessionProgressSnapshot)
def read_session_progress() -> SessionProgressSnapshot:
    return get_session_progress_snapshot()


@router.post(
    "",
    response_model=SessionProgressItem,
    status_code=status.HTTP_201_CREATED,
)
def create_session(payload: SessionCreateRequest) -> SessionProgressItem:
    return start_session(payload)


@router.post("/{session_id}/complete", response_model=SessionProgressItem)
def complete_session(session_id: UUID) -> SessionProgressItem:
    try:
        return finish_session(session_id)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from error
