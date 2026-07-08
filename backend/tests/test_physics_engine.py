import unittest

from backend.services.physics_engine import (
    BallSpec,
    BowlerProfile,
    Environment,
    OilPattern,
    calculate_pattern_difficulty,
    calculate_pin_action,
    evolve_pattern,
    predict_ball_path,
    predict_bowler_outcome,
    score_equipment_effectiveness,
    sensitivity_analysis,
    simulate_scenario,
)


class PhysicsEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.house = OilPattern(
            name="House",
            length_ft=39,
            volume_ml=22,
            asymmetry_index=0.24,
            front_oil_pct=0.44,
            mid_oil_pct=0.36,
            backend_oil_pct=0.20,
        )
        self.sport = OilPattern(
            name="Wolf Variant",
            length_ft=44,
            volume_ml=31,
            asymmetry_index=0.68,
            front_oil_pct=0.48,
            mid_oil_pct=0.35,
            backend_oil_pct=0.17,
            lane_surface="wood",
        )
        self.bowler = BowlerProfile(
            average=195,
            speed_mph=16.2,
            rev_rate=380,
            axis_rotation_deg=48,
            consistency=0.81,
        )
        self.environment = Environment()
        self.traction_ball = BallSpec(
            name="Benchmark Solid",
            coverstock="solid reactive",
            rg=2.48,
            differential=0.050,
            mass_bias=0.010,
            surface_grit=2000,
        )
        self.control_ball = BallSpec(
            name="Spare Plus",
            coverstock="plastic",
            rg=2.69,
            differential=0.018,
            surface_grit=4000,
        )

    def test_long_heavy_pattern_is_harder(self) -> None:
        self.assertGreater(
            calculate_pattern_difficulty(self.sport).score,
            calculate_pattern_difficulty(self.house).score,
        )

    def test_traction_ball_scores_better_on_heavy_pattern(self) -> None:
        traction = score_equipment_effectiveness(
            self.sport,
            self.traction_ball,
            self.bowler,
            self.environment,
        )
        control = score_equipment_effectiveness(
            self.sport,
            self.control_ball,
            self.bowler,
            self.environment,
        )
        self.assertGreater(traction.score, control.score)

    def test_simulation_and_outcome_are_deterministic(self) -> None:
        outcome = predict_bowler_outcome(
            self.house,
            [self.traction_ball, self.control_ball],
            self.bowler,
            self.environment,
        )
        summary = simulate_scenario(
            self.house,
            [self.traction_ball, self.control_ball],
            self.bowler,
            trials=120,
            seed=11,
            environment=self.environment,
        )
        self.assertEqual(outcome.recommended_ball, "Benchmark Solid")
        self.assertEqual(summary.recommended_ball, "Benchmark Solid")
        self.assertLess(summary.confidence_low, summary.mean_score)
        self.assertGreater(summary.confidence_high, summary.mean_score)

    def test_pattern_evolution_moves_oil_downlane(self) -> None:
        evolved = evolve_pattern(self.house, frame_number=8, player_traffic=5)
        self.assertLess(evolved.pattern.volume_ml, self.house.volume_ml)
        self.assertGreater(evolved.pattern.backend_oil_pct, self.house.backend_oil_pct)

    def test_pin_action_and_sensitivity_outputs_are_bounded(self) -> None:
        path = predict_ball_path(self.house, self.traction_ball, self.bowler, self.environment)
        pin_action = calculate_pin_action(path, self.bowler)
        sensitivity = sensitivity_analysis(
            self.house,
            self.traction_ball,
            self.bowler,
            self.environment,
        )
        self.assertLessEqual(pin_action.carry_score, 0.95)
        self.assertIn("speed_plus_1mph_entry_angle_delta", sensitivity)


if __name__ == "__main__":
    unittest.main()
