from fastapi import APIRouter

from src.models.commander import CommanderRequest, CommanderResponse
from src.services.commander import get_commander_recommendation
from src.services.session_progress import DEMO_USER_ID

router = APIRouter(prefix="/api/v1/commander", tags=["commander"])


@router.post("/recommendation", response_model=CommanderResponse)
def commander_recommendation(payload: CommanderRequest) -> CommanderResponse:
    return get_commander_recommendation(payload, DEMO_USER_ID)
