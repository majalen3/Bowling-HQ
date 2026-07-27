from fastapi import APIRouter

from src.models.analytics import AnalyticsSummary
from src.services.analytics import get_analytics_summary
from src.services.session_progress import DEMO_USER_ID

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def read_summary() -> AnalyticsSummary:
    # TODO: replace with authenticated user
    return get_analytics_summary(DEMO_USER_ID)
