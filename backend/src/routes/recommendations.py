from fastapi import APIRouter

from src.models.recommendations import (
    RecommendationRequest,
    RecommendationResponse,
)
from src.services.recommendations import get_opening_ball_recommendation

router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["recommendations"],
)


@router.post("/opening-ball", response_model=RecommendationResponse)
def opening_ball(
    request: RecommendationRequest,
) -> RecommendationResponse:
    # TODO: replace with authenticated user
    return get_opening_ball_recommendation(request)
