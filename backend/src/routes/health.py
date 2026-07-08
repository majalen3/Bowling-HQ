from fastapi import APIRouter

from src.config import get_settings
from src.models.health import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
def read_health() -> HealthStatus:
    settings = get_settings()
    return HealthStatus(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )
