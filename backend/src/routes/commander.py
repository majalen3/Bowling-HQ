from fastapi import APIRouter

from src.models.commander import CommanderRequest, CommanderResponse
from src.services.commander import recommend

router = APIRouter(prefix="/api/v1/commander", tags=["commander"])


@router.post("/recommend", response_model=CommanderResponse)
def recommend_ball(payload: CommanderRequest) -> CommanderResponse:
    return recommend(payload)
