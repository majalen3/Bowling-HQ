from fastapi import APIRouter

from src.models.simulator import SimulatorRequest, SimulatorResponse
from src.services.session_progress import DEMO_USER_ID
from src.services.simulator import run_simulation

router = APIRouter(prefix="/api/v1/simulator", tags=["simulator"])


@router.post("/run", response_model=SimulatorResponse)
def run_simulator(payload: SimulatorRequest) -> SimulatorResponse:
    return run_simulation(payload, DEMO_USER_ID)
