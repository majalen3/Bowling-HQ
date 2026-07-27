from __future__ import annotations

from functools import lru_cache
from typing import Optional, Protocol
from uuid import UUID, uuid4

from psycopg import connect
from psycopg.rows import dict_row

from services.physics_engine import (
    BallSpec,
    BowlerProfile,
    OilPattern,
    predict_ball_path,
)
from src.config import get_settings
from src.models.simulator import SimulatorRequest, SimulatorResponse


class SimulatorRepository(Protocol):
    def log_run(
        self,
        user_id: UUID,
        request: SimulatorRequest,
        response: SimulatorResponse,
    ) -> None:
        ...


class PostgresSimulatorRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def log_run(
        self,
        user_id: UUID,
        request: SimulatorRequest,
        response: SimulatorResponse,
    ) -> None:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO simulator_runs (
                        id, user_id, pattern_name, ball_name, predicted_score,
                        confidence_low, confidence_high, strike_probability,
                        confidence, breakpoint_board, entry_angle_deg
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uuid4(),
                        user_id,
                        request.pattern.name or "Custom Pattern",
                        request.ball.name,
                        response.predicted_score,
                        response.confidence_low,
                        response.confidence_high,
                        response.strike_probability,
                        response.confidence,
                        response.breakpoint_board,
                        response.entry_angle_deg,
                    ),
                )


@lru_cache
def get_simulator_repository() -> SimulatorRepository:
    return PostgresSimulatorRepository(get_settings().postgres_url)


def run_simulation(
    request: SimulatorRequest,
    user_id: UUID,
    repository: Optional[SimulatorRepository] = None,
) -> SimulatorResponse:
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
    bowler = BowlerProfile(
        average=request.bowler.average,
        speed_mph=request.bowler.speed_mph,
        rev_rate=request.bowler.rev_rate,
        axis_rotation_deg=request.bowler.axis_rotation_deg,
        axis_tilt_deg=request.bowler.axis_tilt_deg,
        consistency=request.bowler.consistency,
    )
    ball = BallSpec(
        name=request.ball.name,
        coverstock=request.ball.coverstock,
        rg=request.ball.rg,
        differential=request.ball.differential,
        mass_bias=request.ball.mass_bias,
        surface_grit=request.ball.surface_grit,
    )

    path = predict_ball_path(pattern, ball, bowler)
    predicted_score = int(
        round(
            min(
                300,
                max(
                    0,
                    bowler.average * 0.58
                    + path.strike_probability * 120,
                ),
            )
        )
    )
    spread = int(
        round(
            (1 - bowler.consistency) * 28
            + (1 - path.confidence) * 22
        )
    )
    response = SimulatorResponse(
        predicted_score=predicted_score,
        confidence_low=max(0, predicted_score - spread),
        confidence_high=min(300, predicted_score + spread),
        strike_probability=path.strike_probability,
        confidence=path.confidence,
        breakpoint_board=path.breakpoint_board,
        entry_angle_deg=path.entry_angle_deg,
        notes=[
            (
                f"Skid {path.skid_ft}ft, hook {path.hook_ft}ft, "
                f"roll {path.roll_ft}ft."
            ),
            (
                "Use this as a first-pass lane play estimate before "
                "live adjustments."
            ),
        ],
    )

    repo = repository or get_simulator_repository()
    repo.log_run(user_id, request, response)
    return response
