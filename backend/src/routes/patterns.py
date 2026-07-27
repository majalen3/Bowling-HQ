from fastapi import APIRouter

from src.models.patterns import PatternAnalysisRequest, PatternAnalysisResponse
from src.services.pattern_intelligence import analyze_pattern
from src.services.session_progress import DEMO_USER_ID

router = APIRouter(prefix="/api/v1/patterns", tags=["patterns"])


@router.post("/analyze", response_model=PatternAnalysisResponse)
def analyze_pattern_route(
    payload: PatternAnalysisRequest,
) -> PatternAnalysisResponse:
    return analyze_pattern(payload, DEMO_USER_ID)
