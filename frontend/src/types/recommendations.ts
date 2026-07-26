export type PatternInput = {
  name?: string;
  length_ft: number;
  volume_ml: number;
  asymmetry_index: number;
  front_oil_pct: number;
  mid_oil_pct: number;
  backend_oil_pct: number;
  lane_surface: string;
};

export type BowlerInput = {
  average: number;
  speed_mph: number;
  rev_rate: number;
  axis_rotation_deg: number;
  axis_tilt_deg: number;
  consistency: number;
};

export type RecommendationRequest = {
  pattern: PatternInput;
  bowler: BowlerInput;
  top_n: number;
  session_id?: string;
};

export type BallRecommendation = {
  rank: number;
  ball_id: string | null;
  ball_name: string;
  fit_score: number;
  confidence: number;
  matched_shape: string;
  reasoning: string[];
  breakpoint_board: number;
  entry_angle_deg: number;
  strike_probability: number;
};

export type RecommendationResponse = {
  pattern_difficulty_score: number;
  pattern_difficulty_label: string;
  breakpoint_board: number;
  recommendations: BallRecommendation[];
  bowler_type: string;
  session_id: string | null;
};
