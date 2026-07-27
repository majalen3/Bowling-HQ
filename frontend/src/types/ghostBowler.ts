export type ConditionBaseline = {
  condition_family: string;
  game_count: number;
  average_score: number;
  score_band_low: number;
  score_band_high: number;
  strike_rate: number;
  spare_rate: number;
  open_frame_rate: number;
};

export type GhostBowlerBaselineResponse = {
  total_games: number;
  overall: ConditionBaseline;
  by_condition: ConditionBaseline[];
};

export type GhostBowlerCompareResponse = {
  condition_family: string;
  baseline_average: number;
  current_average: number;
  delta: number;
  trend: string;
};
