from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

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

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
MAX_VIDEO_BYTES = 500 * 1024 * 1024  # 500 MB


class VideoUploadResult(BaseModel):
    session_id: str
    filename: str
    size_bytes: int
    content_type: str
    message: str

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


@router.post(
    "/{session_id}/videos",
    response_model=VideoUploadResult,
    status_code=status.HTTP_201_CREATED,
)
async def upload_session_video(
    session_id: UUID,
    file: UploadFile = File(...),
) -> VideoUploadResult:
    """Accept a video file for a session. Validates type and size."""
    content_type = file.content_type or ""
    if content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type '{content_type}'. "
                "Accepted: mp4, mov, avi, webm."
            ),
        )
    data = await file.read()
    if len(data) > MAX_VIDEO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Video exceeds the 500 MB limit.",
        )
    return VideoUploadResult(
        session_id=str(session_id),
        filename=file.filename or "upload",
        size_bytes=len(data),
        content_type=content_type,
        message="Video received. Processing pipeline coming soon.",
    )
