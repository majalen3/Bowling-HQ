from fastapi import APIRouter, Query

from src.models.ghost_bowler import (
    GhostBowlerBaselineResponse,
    GhostBowlerCompareResponse,
)
from src.services.ghost_bowler import (
    compare_to_ghost_bowler,
    get_ghost_bowler_baseline,
)
from src.services.session_progress import DEMO_USER_ID

router = APIRouter(prefix="/api/v1/ghost-bowler", tags=["ghost-bowler"])


@router.get("", response_model=GhostBowlerBaselineResponse)
def read_ghost_bowler() -> GhostBowlerBaselineResponse:
    return get_ghost_bowler_baseline(DEMO_USER_ID)


@router.get("/compare", response_model=GhostBowlerCompareResponse)
def compare_ghost_bowler(
    current_average: float = Query(ge=0, le=300),
    condition_family: str = Query(default="overall"),
) -> GhostBowlerCompareResponse:
    return compare_to_ghost_bowler(
        DEMO_USER_ID,
        current_average=current_average,
        condition_family=condition_family,
    )
