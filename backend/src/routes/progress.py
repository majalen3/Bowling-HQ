from fastapi import APIRouter

from src.models.progress import ProgressSnapshot
from src.services.progress import get_progress_snapshot

router = APIRouter(prefix="/api/v1", tags=["progress"])


@router.get("/progress", response_model=ProgressSnapshot)
def read_progress() -> ProgressSnapshot:
    return get_progress_snapshot()
