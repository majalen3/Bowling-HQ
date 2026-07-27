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
    calculate_pattern_difficulty,
    predict_ball_path,
    score_equipment_effectiveness,
)
from src.config import get_settings
from src.models.arsenal import BallItem
from src.models.recommendations import (
    BallRecommendation,
    RecommendationRequest,
    RecommendationResponse,
)
from src.services.arsenal import (
    BALL_CATALOG_SEED,
    get_arsenal_repository,
)


class RecommendationRepository(Protocol):
    def get_arsenal_balls(self, user_id: UUID) -> list[BallItem]:
        ...

    def get_catalog_balls(self) -> list[BallItem]:
        ...

    def log_recommendation(
        self,
        user_id: UUID,
        session_id: Optional[UUID],
        recommended_ball_id: Optional[UUID],
        pattern_name: Optional[str],
        pattern_length_ft: float,
        pattern_volume_ml: float,
        fit_score: float,
        confidence: float,
        reasoning: str,
    ) -> None:
        ...


class PostgresRecommendationRepository:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url

    def get_arsenal_balls(self, user_id: UUID) -> list[BallItem]:
        arsenal = get_arsenal_repository().list_arsenal(user_id)
        return [entry.ball for entry in arsenal]

    def get_catalog_balls(self) -> list[BallItem]:
        return get_arsenal_repository().list_catalog()

    def log_recommendation(
        self,
        user_id: UUID,
        session_id: Optional[UUID],
        recommended_ball_id: Optional[UUID],
        pattern_name: Optional[str],
        pattern_length_ft: float,
        pattern_volume_ml: float,
        fit_score: float,
        confidence: float,
        reasoning: str,
    ) -> None:
        with connect(self.postgres_url, row_factory=dict_row) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO commander_recommendations (
                        id, user_id, session_id, recommended_ball_id,
                        pattern_name, pattern_length_ft, pattern_volume_ml,
                        fit_score, confidence, reasoning
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        uuid4(),
                        user_id,
                        session_id,
                        recommended_ball_id,
                        pattern_name,
                        pattern_length_ft,
                        pattern_volume_ml,
                        fit_score,
                        confidence,
                        reasoning,
                    ),
                )


@lru_cache
def get_recommendation_repository() -> RecommendationRepository:
    return PostgresRecommendationRepository(
        postgres_url=get_settings().postgres_url,
    )


def _catalog_fallback_balls() -> list[BallItem]:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    balls: list[BallItem] = []
    for spec in BALL_CATALOG_SEED:
        balls.append(
            BallItem(
                id=uuid4(),
                name=spec["name"],
                brand=spec["brand"],
                coverstock=spec["coverstock"],
                rg=spec["rg"],
                differential=spec["differential"],
                mass_bias=spec.get("mass_bias", 0.0),
                surface_grit=spec.get("surface_grit", 3000),
                weight_lbs=spec.get("weight_lbs", 15),
                created_at=now,
            )
        )
    return balls


def classify_bowler(rev_rate: int, speed_mph: float) -> tuple[str, float]:
    rev_hundreds = max(rev_rate / 100, 0.01)
    speed_to_rev = speed_mph / rev_hundreds
    if speed_to_rev > 4.0:
        return "speed_dominant", round(speed_to_rev, 2)
    if speed_to_rev < 3.0:
        return "rev_dominant", round(speed_to_rev, 2)
    if rev_rate < 280:
        return "stroker", round(speed_to_rev, 2)
    if rev_rate <= 380:
        return "tweener", round(speed_to_rev, 2)
    return "cranker", round(speed_to_rev, 2)


def _calibrate(
    ball: BallItem,
    pattern,
    bowler_type: str,
    base_score: float,
    axis_rotation_deg: float,
) -> tuple[float, list[str]]:
    cover = ball.coverstock.lower()
    is_solid = "solid" in cover
    is_pearl = "pearl" in cover
    is_urethane = "urethane" in cover
    score = base_score
    reasons: list[str] = []
    length = pattern.length_ft
    volume = pattern.volume_ml

    # a) pattern length vs RG
    if length > 41 and ball.rg <= 2.50:
        score += 8
        reasons.append(
            "Low RG core revs up early to handle the long pattern."
        )
    elif length < 37 and ball.rg <= 2.50:
        score -= 8
        reasons.append(
            "Low RG core reads too early for this short pattern."
        )

    # b) oil volume vs coverstock
    if volume > 27:
        if is_solid:
            score += 10
            reasons.append(
                "Solid reactive cover provides traction in heavy oil."
            )
        elif is_pearl:
            score -= 8
            reasons.append(
                "Pearl cover struggles for traction in heavy oil."
            )
        elif is_urethane:
            score -= 15
            reasons.append(
                "Urethane lacks the strength for heavy volume."
            )
    elif volume < 22:
        if is_urethane:
            score += 8
            reasons.append(
                "Urethane gives control on this light volume."
            )
        elif is_pearl:
            score += 6
            reasons.append(
                "Pearl cover conserves energy on dry lanes."
            )
        elif is_solid:
            score -= 10
            reasons.append(
                "Solid reactive over-reads on this dry pattern."
            )

    # c) surface grit vs oil
    if volume > 27:
        if 500 <= ball.surface_grit <= 1500:
            score += 8
            reasons.append(
                "Dull surface reads the heavy oil sooner."
            )
        elif ball.surface_grit > 3500:
            score -= 8
            reasons.append(
                "Polished surface skids too far in heavy oil."
            )
    elif volume < 22:
        if ball.surface_grit > 3500:
            score += 8
            reasons.append(
                "Smooth surface preserves length on dry lanes."
            )
        elif ball.surface_grit <= 1500:
            score -= 6
            reasons.append(
                "Dull surface burns up energy on dry lanes."
            )

    # d) rev-dominant bowler
    if bowler_type == "rev_dominant":
        if ball.differential > 0.05:
            score -= 6
            reasons.append(
                "High differential can over-hook for a rev-dominant "
                "player."
            )
        if ball.rg >= 2.52:
            score += 4
            reasons.append(
                "Higher RG stores energy to control the rev-dominant "
                "release."
            )

    # e) speed-dominant bowler
    if bowler_type == "speed_dominant":
        if ball.rg > 2.53:
            score -= 6
            reasons.append(
                "Higher RG slides through for a speed-dominant player."
            )
        else:
            score += 4
            reasons.append(
                "Lower RG helps a speed-dominant player get the ball "
                "into a roll."
            )
        if ball.differential > 0.047:
            score += 6
            reasons.append(
                "High differential adds needed flare for speed "
                "dominance."
            )

    # f) high axis rotation rewards backend
    if axis_rotation_deg > 60 and (is_pearl or ball.rg >= 2.52):
        score += 4
        reasons.append(
            "Backend-heavy shape matches the high axis rotation."
        )

    return score, reasons


def get_opening_ball_recommendation(
    request: RecommendationRequest,
    repository: Optional[RecommendationRepository] = None,
) -> RecommendationResponse:
    from src.services.session_progress import DEMO_USER_ID

    repo = repository or get_recommendation_repository()
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
    bowler_type, _ratio = classify_bowler(
        request.bowler.rev_rate,
        request.bowler.speed_mph,
    )

    balls = repo.get_arsenal_balls(DEMO_USER_ID)
    if not balls:
        balls = repo.get_catalog_balls()
    if not balls:
        balls = _catalog_fallback_balls()

    difficulty = calculate_pattern_difficulty(pattern)
    breakpoint_board = max(4.0, round(pattern.length_ft - 31, 1))

    scored: list[tuple[float, BallItem, BallRecommendation]] = []
    for ball in balls:
        spec = BallSpec(
            name=ball.name,
            coverstock=ball.coverstock,
            rg=ball.rg,
            differential=ball.differential,
            mass_bias=ball.mass_bias,
            surface_grit=ball.surface_grit,
        )
        fit = score_equipment_effectiveness(pattern, spec, bowler)
        prediction = predict_ball_path(pattern, spec, bowler)
        calibrated, reasons = _calibrate(
            ball,
            pattern,
            bowler_type,
            fit.score,
            request.bowler.axis_rotation_deg,
        )
        calibrated = max(1.0, min(100.0, round(calibrated, 1)))
        combined_reasons = [
            f"Preferred shape for this pattern is {fit.matched_shape}.",
            *reasons,
        ]
        recommendation = BallRecommendation(
            rank=0,
            ball_id=ball.id,
            ball_name=ball.name,
            fit_score=calibrated,
            confidence=prediction.confidence,
            matched_shape=fit.matched_shape,
            reasoning=combined_reasons,
            breakpoint_board=prediction.breakpoint_board,
            entry_angle_deg=prediction.entry_angle_deg,
            strike_probability=prediction.strike_probability,
        )
        scored.append((calibrated, ball, recommendation))

    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[: request.top_n]
    recommendations: list[BallRecommendation] = []
    for index, (_score, _ball, recommendation) in enumerate(top, start=1):
        recommendation.rank = index
        recommendations.append(recommendation)

    if recommendations:
        best = recommendations[0]
        repo.log_recommendation(
            user_id=DEMO_USER_ID,
            session_id=request.session_id,
            recommended_ball_id=best.ball_id,
            pattern_name=pattern.name,
            pattern_length_ft=pattern.length_ft,
            pattern_volume_ml=pattern.volume_ml,
            fit_score=best.fit_score,
            confidence=best.confidence,
            reasoning=" ".join(best.reasoning),
        )

    return RecommendationResponse(
        pattern_difficulty_score=difficulty.score,
        pattern_difficulty_label=difficulty.label,
        breakpoint_board=breakpoint_board,
        recommendations=recommendations,
        bowler_type=bowler_type,
        session_id=request.session_id,
    )
