export type ScoreTrendPoint = {
  session_id: string;
  date: string;
  average: number;
  game_count: number;
  high_game: number;
  location_name: string | null;
};

export type BallAverage = {
  ball_id: string;
  ball_name: string;
  average: number;
  game_count: number;
};

export type AnalyticsSummary = {
  overall_average: number;
  high_game: number;
  total_games: number;
  total_sessions: number;
  recent_trend: ScoreTrendPoint[];
  per_ball_averages: BallAverage[];
};
