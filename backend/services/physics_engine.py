"""Lightweight bowling physics and prediction primitives for Bowling-HQ.

The formulas in this module are intentionally heuristic. They provide an
integration-ready baseline that can be calibrated later as tracked data becomes
available from lanes, balls, and bowlers.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import sqrt
from random import Random
from statistics import mean, pstdev


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _normalize_coverstock(coverstock: str) -> str:
    normalized = coverstock.strip().lower()
    if "particle" in normalized:
        return "particle"
    if "pearl" in normalized:
        return "pearl reactive"
    if "hybrid" in normalized:
        return "hybrid reactive"
    if "solid" in normalized:
        return "solid reactive"
    if "reactive" in normalized:
        return "reactive"
    if "urethane" in normalized:
        return "urethane"
    return "plastic"


@dataclass(frozen=True)
class OilPattern:
    name: str
    length_ft: float
    volume_ml: float
    asymmetry_index: float
    front_oil_pct: float
    mid_oil_pct: float
    backend_oil_pct: float
    lane_surface: str = "synthetic"

    def normalized_segments(self) -> tuple[float, float, float]:
        total = self.front_oil_pct + self.mid_oil_pct + self.backend_oil_pct
        if total <= 0:
            return (0.34, 0.33, 0.33)
        return (
            self.front_oil_pct / total,
            self.mid_oil_pct / total,
            self.backend_oil_pct / total,
        )


@dataclass(frozen=True)
class BallSpec:
    name: str
    coverstock: str
    rg: float
    differential: float
    mass_bias: float = 0.0
    surface_grit: int = 3000


@dataclass(frozen=True)
class BowlerProfile:
    average: int
    speed_mph: float
    rev_rate: int
    axis_rotation_deg: float
    axis_tilt_deg: float = 10.0
    consistency: float = 0.75


@dataclass(frozen=True)
class Environment:
    temperature_f: float = 72.0
    humidity_pct: float = 45.0
    lane_age_years: float = 5.0


@dataclass(frozen=True)
class PatternDifficulty:
    score: float
    label: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class TrajectoryPrediction:
    skid_ft: float
    hook_ft: float
    roll_ft: float
    breakpoint_board: float
    entry_angle_deg: float
    strike_probability: float
    confidence: float


@dataclass(frozen=True)
class PinAction:
    carry_score: float
    deflection_index: float
    messenger_probability: float


@dataclass(frozen=True)
class EquipmentFit:
    score: float
    matched_shape: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class PatternEvolution:
    pattern: OilPattern
    front_breakdown_pct: float
    carrydown_pct: float
    breakpoint_shift_boards: float


@dataclass(frozen=True)
class BowlerOutcome:
    recommended_ball: str
    expected_score: int
    success_probability: float
    confidence_low: int
    confidence_high: int


@dataclass(frozen=True)
class SimulationSummary:
    recommended_ball: str
    mean_score: float
    standard_deviation: float
    confidence_low: float
    confidence_high: float
    strike_probability: float


def estimate_friction(pattern: OilPattern, ball: BallSpec, environment: Environment) -> float:
    coverstock = _normalize_coverstock(ball.coverstock)
    cover_friction = {
        "plastic": 0.20,
        "urethane": 0.42,
        "reactive": 0.66,
        "hybrid reactive": 0.70,
        "pearl reactive": 0.61,
        "solid reactive": 0.76,
        "particle": 0.82,
    }[coverstock]
    grit_factor = _clamp((4000 - ball.surface_grit) / 3500, -0.20, 0.35)
    surface_factor = {"synthetic": 0.00, "hybrid": 0.03, "wood": 0.06}.get(
        pattern.lane_surface.lower(),
        0.00,
    )
    oil_factor = pattern.volume_ml / 90
    humidity_factor = environment.humidity_pct / 500
    temperature_factor = (environment.temperature_f - 70) / 80
    lane_age_factor = min(environment.lane_age_years, 20) / 500
    return _clamp(
        cover_friction
        + grit_factor
        + surface_factor
        - oil_factor
        - humidity_factor
        + temperature_factor
        + lane_age_factor,
        0.12,
        0.95,
    )


def calculate_pattern_difficulty(pattern: OilPattern) -> PatternDifficulty:
    front, mid, backend = pattern.normalized_segments()
    score = (
        1.6
        + (pattern.length_ft - 35) * 0.12
        + (pattern.volume_ml - 20) * 0.11
        + pattern.asymmetry_index * 1.6
        + max(0.0, backend - 0.22) * 4.5
        + max(0.0, front - 0.42) * 3.0
    )
    clamped = round(_clamp(score, 1.0, 10.0), 1)
    if clamped < 3.5:
        label = "easy"
    elif clamped < 6.5:
        label = "moderate"
    elif clamped < 8.5:
        label = "hard"
    else:
        label = "sport-plus"

    notes = []
    if pattern.length_ft >= 42:
        notes.append("Longer patterns delay friction and punish speed errors.")
    if pattern.volume_ml >= 28:
        notes.append("Higher oil volume increases hold in the heads and midlane.")
    if pattern.asymmetry_index >= 0.55:
        notes.append("Higher asymmetry narrows the playable launch window.")
    if backend <= 0.18:
        notes.append("Cleaner backend creates steeper response to friction.")
    return PatternDifficulty(clamped, label, tuple(notes))


def predict_ball_path(
    pattern: OilPattern,
    ball: BallSpec,
    bowler: BowlerProfile,
    environment: Environment | None = None,
) -> TrajectoryPrediction:
    environment = environment or Environment()
    friction = estimate_friction(pattern, ball, environment)
    front, mid, backend = pattern.normalized_segments()
    rev_speed_ratio = bowler.rev_rate / max(bowler.speed_mph * 24, 1)
    skid_ft = _clamp(
        pattern.length_ft * 0.78
        + pattern.volume_ml * 0.16
        + bowler.speed_mph * 0.45
        + front * 5.5
        - friction * 13.5
        - rev_speed_ratio * 3.8,
        15.0,
        48.0,
    )
    hook_ft = _clamp(
        8.0
        + friction * 7.0
        + ball.differential * 75
        + ball.mass_bias * 12
        + (bowler.axis_rotation_deg / 90) * 3.5
        - backend * 4.0,
        4.0,
        19.0,
    )
    roll_ft = _clamp(60.0 - skid_ft - hook_ft, 3.0, 20.0)
    breakpoint_board = _clamp(
        8.0
        + pattern.asymmetry_index * 7.0
        + (pattern.length_ft - 36) * 0.22
        + bowler.axis_rotation_deg * 0.06
        - friction * 3.0
        - (2.50 - ball.rg) * 18,
        5.0,
        22.0,
    )
    entry_angle_deg = _clamp(
        1.8
        + hook_ft * 0.20
        + bowler.axis_rotation_deg * 0.025
        - bowler.speed_mph * 0.08
        - mid * 1.4,
        2.0,
        8.5,
    )
    strike_probability = _clamp(
        0.34
        + bowler.consistency * 0.28
        + max(0.0, 1 - abs(entry_angle_deg - 6.0) / 5) * 0.22
        + friction * 0.12
        - abs(pattern.volume_ml - 24) * 0.004,
        0.18,
        0.86,
    )
    confidence = _clamp(
        0.56
        + bowler.consistency * 0.18
        + min(pattern.volume_ml, 35) * 0.004
        - max(0.0, abs(environment.temperature_f - 72)) * 0.002,
        0.50,
        0.93,
    )
    return TrajectoryPrediction(
        skid_ft=round(skid_ft, 1),
        hook_ft=round(hook_ft, 1),
        roll_ft=round(roll_ft, 1),
        breakpoint_board=round(breakpoint_board, 1),
        entry_angle_deg=round(entry_angle_deg, 1),
        strike_probability=round(strike_probability, 3),
        confidence=round(confidence, 3),
    )


def calculate_pin_action(prediction: TrajectoryPrediction, bowler: BowlerProfile) -> PinAction:
    carry_score = _clamp(
        0.45
        + max(0.0, 1 - abs(prediction.entry_angle_deg - 6.0) / 4) * 0.28
        + bowler.speed_mph * 0.01
        + bowler.rev_rate / 2000,
        0.25,
        0.95,
    )
    deflection_index = _clamp(
        0.55
        - (carry_score - 0.55) * 0.60
        + prediction.roll_ft / 50,
        0.10,
        0.90,
    )
    messenger_probability = _clamp(
        carry_score * 0.42 + bowler.axis_rotation_deg / 260,
        0.10,
        0.70,
    )
    return PinAction(
        carry_score=round(carry_score, 3),
        deflection_index=round(deflection_index, 3),
        messenger_probability=round(messenger_probability, 3),
    )


def score_equipment_effectiveness(
    pattern: OilPattern,
    ball: BallSpec,
    bowler: BowlerProfile,
    environment: Environment | None = None,
) -> EquipmentFit:
    environment = environment or Environment()
    prediction = predict_ball_path(pattern, ball, bowler, environment)
    difficulty = calculate_pattern_difficulty(pattern)
    coverstock = _normalize_coverstock(ball.coverstock)

    preferred_shape = "benchmark"
    if pattern.volume_ml >= 28:
        preferred_shape = "traction"
    elif pattern.volume_ml <= 18:
        preferred_shape = "control"

    shape_fit = {
        "traction": {"solid reactive", "particle", "reactive"},
        "benchmark": {"hybrid reactive", "reactive", "pearl reactive", "urethane"},
        "control": {"urethane", "plastic", "pearl reactive"},
    }
    score = (
        prediction.strike_probability * 70
        + prediction.confidence * 15
        + (10 - difficulty.score) * 0.8
    )
    if coverstock in shape_fit[preferred_shape]:
        score += 8
    notes = [f"Preferred shape for this pattern is {preferred_shape}."]
    if ball.surface_grit <= 2000:
        notes.append("Lower grit surface helps the ball read the midlane sooner.")
    if ball.rg <= 2.50 and pattern.length_ft >= 41:
        notes.append("Lower RG helps the core rev up before the pins.")

    return EquipmentFit(
        score=round(_clamp(score, 1, 100), 1),
        matched_shape=preferred_shape,
        notes=tuple(notes),
    )


def evolve_pattern(
    pattern: OilPattern,
    frame_number: int,
    player_traffic: int,
) -> PatternEvolution:
    breakdown = _clamp(frame_number * 0.012 + player_traffic * 0.003, 0.0, 0.30)
    carrydown = _clamp(player_traffic * 0.002 + max(0, frame_number - 3) * 0.005, 0.0, 0.18)
    front, mid, backend = pattern.normalized_segments()
    new_front = max(0.05, front - breakdown)
    new_mid = max(0.05, mid - breakdown / 2 + carrydown / 3)
    new_backend = max(0.05, backend + carrydown)
    total = new_front + new_mid + new_backend
    updated = replace(
        pattern,
        volume_ml=round(max(8.0, pattern.volume_ml * (1 - breakdown * 0.45)), 1),
        front_oil_pct=round(new_front / total, 3),
        mid_oil_pct=round(new_mid / total, 3),
        backend_oil_pct=round(new_backend / total, 3),
        asymmetry_index=round(
            _clamp(pattern.asymmetry_index + breakdown * 0.20 - carrydown * 0.10, 0.05, 0.95),
            3,
        ),
    )
    return PatternEvolution(
        pattern=updated,
        front_breakdown_pct=round(breakdown, 3),
        carrydown_pct=round(carrydown, 3),
        breakpoint_shift_boards=round((breakdown - carrydown) * 10, 2),
    )


def predict_bowler_outcome(
    pattern: OilPattern,
    balls: list[BallSpec],
    bowler: BowlerProfile,
    environment: Environment | None = None,
) -> BowlerOutcome:
    environment = environment or Environment()
    ranked = sorted(
        (
            (ball, score_equipment_effectiveness(pattern, ball, bowler, environment))
            for ball in balls
        ),
        key=lambda item: item[1].score,
        reverse=True,
    )
    best_ball, best_fit = ranked[0]
    difficulty = calculate_pattern_difficulty(pattern)
    expected_score = round(
        _clamp(
            bowler.average
            + (best_fit.score - 60) * 0.35
            - (difficulty.score - 5) * 4.4
            + bowler.consistency * 8,
            110,
            279,
        )
    )
    spread = round(_clamp(22 - bowler.consistency * 10 + difficulty.score, 10, 30))
    success_probability = _clamp(
        0.30 + (best_fit.score / 100) * 0.38 + bowler.consistency * 0.18 - difficulty.score * 0.02,
        0.16,
        0.88,
    )
    return BowlerOutcome(
        recommended_ball=best_ball.name,
        expected_score=expected_score,
        success_probability=round(success_probability, 3),
        confidence_low=max(0, expected_score - spread),
        confidence_high=min(300, expected_score + spread),
    )


def simulate_scenario(
    pattern: OilPattern,
    balls: list[BallSpec],
    bowler: BowlerProfile,
    games: int = 3,
    trials: int = 250,
    seed: int = 7,
    environment: Environment | None = None,
) -> SimulationSummary:
    environment = environment or Environment()
    outcome = predict_bowler_outcome(pattern, balls, bowler, environment)
    chosen_ball = next(ball for ball in balls if ball.name == outcome.recommended_ball)
    prediction = predict_ball_path(pattern, chosen_ball, bowler, environment)
    rng = Random(seed)
    scores = []
    frame_base = outcome.expected_score / 10
    variance = max(
        2.0,
        (1 - bowler.consistency) * 6
        + calculate_pattern_difficulty(pattern).score / 4,
    )
    for _ in range(trials):
        total = 0.0
        for _frame in range(games * 10):
            total += _clamp(frame_base + rng.gauss(0, variance), 6.0, 30.0)
        scores.append(total / games)
    avg = mean(scores)
    std_dev = pstdev(scores)
    margin = 1.96 * (std_dev / sqrt(len(scores)))
    return SimulationSummary(
        recommended_ball=chosen_ball.name,
        mean_score=round(avg, 1),
        standard_deviation=round(std_dev, 2),
        confidence_low=round(avg - margin, 1),
        confidence_high=round(avg + margin, 1),
        strike_probability=prediction.strike_probability,
    )


def sensitivity_analysis(
    pattern: OilPattern,
    ball: BallSpec,
    bowler: BowlerProfile,
    environment: Environment | None = None,
) -> dict[str, float]:
    environment = environment or Environment()
    baseline = predict_ball_path(pattern, ball, bowler, environment)
    faster = predict_ball_path(
        pattern,
        ball,
        replace(bowler, speed_mph=bowler.speed_mph + 1),
        environment,
    )
    more_revs = predict_ball_path(
        pattern,
        ball,
        replace(bowler, rev_rate=bowler.rev_rate + 40),
        environment,
    )
    more_rotation = predict_ball_path(
        pattern,
        ball,
        replace(bowler, axis_rotation_deg=min(90.0, bowler.axis_rotation_deg + 10)),
        environment,
    )
    return {
        "speed_plus_1mph_entry_angle_delta": round(
            faster.entry_angle_deg - baseline.entry_angle_deg,
            2,
        ),
        "speed_plus_1mph_breakpoint_delta": round(
            faster.breakpoint_board - baseline.breakpoint_board,
            2,
        ),
        "revs_plus_40_breakpoint_delta": round(
            more_revs.breakpoint_board - baseline.breakpoint_board,
            2,
        ),
        "rotation_plus_10deg_entry_angle_delta": round(
            more_rotation.entry_angle_deg - baseline.entry_angle_deg,
            2,
        ),
    }
