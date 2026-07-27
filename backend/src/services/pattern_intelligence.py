from __future__ import annotations

from functools import lru_cache
from typing import Optional, Protocol
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from services.physics_engine import OilPattern, calculate_pattern_difficulty
from src.config import get_settings
from src.models.patterns import PatternAnalysisRequest, PatternAnalysisResponse


class PatternAnalysisRepository(Protocol):
    def log_analysis(self, user_id: UUID, response: PatternAnalysisResponse) -> None:
        ...


class PostgresPatternAnalysisRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def log_analysis(self, user_id: UUID, response: PatternAnalysisResponse) -> None:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO pattern_analyses (
                        id, user_id, pattern_name, difficulty_score,
                        difficulty_label, breakpoint_board, transition_risk,
                        transition_rate, guidance
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid4(),
                        user_id,
                        response.pattern_name,
                        response.difficulty_score,
                        response.difficulty_label,
                        response.breakpoint_board,
                        response.transition_risk,
                        response.transition_rate,
                        " | ".join(response.guidance),
                    ),
                )


@lru_cache
def get_pattern_analysis_repository() -> PatternAnalysisRepository:
    return PostgresPatternAnalysisRepository(get_settings().postgres_url)


def analyze_pattern(
    request: PatternAnalysisRequest,
    user_id: UUID,
    repository: Optional[PatternAnalysisRepository] = None,
) -> PatternAnalysisResponse:
    pattern = OilPattern(
        name=request.pattern.name or "Custom Pattern",
        length_ft=request.pattern.length_ft,
        volume_ml=request.pattern.volume_ml,
        asymmetry_index=request.pattern.asymmetry_index,
        front_oil_pct=request.pattern.front_oil_pct,
        mid_oil_pct=request.pattern.mid_oil_pct,
        backend_oil_pct=request.pattern.backend_oil_pct,
        lane_surface=request.pattern.lane_surface,
    )
    difficulty = calculate_pattern_difficulty(pattern)
    breakpoint_board = max(4.0, min(20.0, round(pattern.length_ft - 31, 1)))

    transition_rate = min(1.0, max(0.0, round((pattern.volume_ml - 16) / 20, 2)))
    transition_risk = "low"
    if transition_rate > 0.7:
        transition_risk = "high"
    elif transition_rate > 0.4:
        transition_risk = "medium"

    guidance = [
        f"Rule of 31 breakpoint starts near board {breakpoint_board}.",
        f"Pattern rates as {difficulty.label} difficulty.",
    ]
    if transition_risk == "high":
        guidance.append(
            "Expect faster front-lane breakdown; plan at least one ball-down move."
        )
    elif transition_risk == "medium":
        guidance.append(
            "Monitor transition from game 2 onward and adjust 1-2 boards."
        )
    else:
        guidance.append(
            "Transition should be gradual; stay with benchmark line longer."
        )

    response = PatternAnalysisResponse(
        pattern_name=pattern.name,
        difficulty_score=difficulty.score,
        difficulty_label=difficulty.label,
        breakpoint_board=breakpoint_board,
        transition_risk=transition_risk,
        transition_rate=transition_rate,
        guidance=guidance,
    )

    repo = repository or get_pattern_analysis_repository()
    repo.log_analysis(user_id, response)
    return response
