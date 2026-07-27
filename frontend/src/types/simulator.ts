import type { BowlerInput, PatternInput } from './recommendations';

export type SimulatorBallInput = {
  name: string;
  coverstock: string;
  rg: number;
  differential: number;
  mass_bias: number;
  surface_grit: number;
};

export type SimulatorRequest = {
  pattern: PatternInput;
  bowler: BowlerInput;
  ball: SimulatorBallInput;
};

export type SimulatorResponse = {
  predicted_score: number;
  confidence_low: number;
  confidence_high: number;
  strike_probability: number;
  confidence: number;
  breakpoint_board: number;
  entry_angle_deg: number;
  notes: string[];
};
