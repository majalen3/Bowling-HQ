from __future__ import annotations

from typing import Optional
from uuid import UUID

from src.models.commander import CommanderRequest, CommanderResponse
from src.models.patterns import PatternAnalysisRequest
from src.models.simulator import SimulatorBallInput, SimulatorRequest
from src.services.arsenal import get_arsenal_repository
from src.services.ghost_bowler import get_ghost_bowler_baseline
from src.services.pattern_intelligence import analyze_pattern
from src.services.recommendations import get_opening_ball_recommendation
from src.services.simulator import run_simulation


def get_commander_recommendation(
    request: CommanderRequest,
    user_id: UUID,
) -> CommanderResponse:
    ghost = get_ghost_bowler_baseline(user_id)
    pattern = analyze_pattern(PatternAnalysisRequest(pattern=request.pattern), user_id)
    opening = get_opening_ball_recommendation(request)

    top_simulation = None
    if opening.recommendations:
        best = opening.recommendations[0]
        ball = None
        if best.ball_id is not None:
            ball = get_arsenal_repository().get_ball(best.ball_id)
        if ball is not None:
            top_simulation = run_simulation(
                SimulatorRequest(
                    pattern=request.pattern,
                    bowler=request.bowler,
                    ball=SimulatorBallInput(
                        name=ball.name,
                        coverstock=ball.coverstock,
                        rg=ball.rg,
                        differential=ball.differential,
                        mass_bias=ball.mass_bias,
                        surface_grit=ball.surface_grit,
                    ),
                ),
                user_id,
            )

    confidence_factors = [opening.recommendations[0].confidence if opening.recommendations else 0.5]
    if top_simulation:
        confidence_factors.append(top_simulation.confidence)
    confidence_factors.append(max(0.5, 1 - abs(pattern.transition_rate - 0.5)))
    confidence = round(sum(confidence_factors) / len(confidence_factors), 3)

    rationale = [
        f"Ghost baseline average: {ghost.overall.average_score}.",
        f"Pattern difficulty is {pattern.difficulty_label} ({pattern.difficulty_score}).",
    ]
    if opening.recommendations:
        rationale.append(
            f"Top ball fit: {opening.recommendations[0].ball_name} ({opening.recommendations[0].fit_score}/100)."
        )
    if top_simulation:
        rationale.append(
            f"Simulated score range {top_simulation.confidence_low}-{top_simulation.confidence_high}."
        )

    return CommanderResponse(
        ghost_bowler=ghost,
        pattern_analysis=pattern,
        opening_ball=opening,
        top_ball_simulation=top_simulation,
        confidence=confidence,
        rationale=rationale,
    )
