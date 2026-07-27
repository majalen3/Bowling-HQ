from fastapi import APIRouter

from src.models.ghost_bowler import GhostBowlerProfile
from src.services.ghost_bowler import get_profile

router = APIRouter(prefix="/api/v1/ghost-bowler", tags=["ghost-bowler"])


@router.get("/profile", response_model=GhostBowlerProfile)
def read_profile() -> GhostBowlerProfile:
    return get_profile()
