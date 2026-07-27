export type Trend = 'improving' | 'consistent' | 'declining';
export type PerformanceTier = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export type SessionTypeBreakdown = {
  session_type: string;
  count: number;
};

export type GhostBowlerProfile = {
  average_score: number;
  high_game: number;
  total_games: number;
  total_sessions: number;
  sessions_by_type: SessionTypeBreakdown[];
  trend: Trend;
  predicted_next_game: number;
  consistency_score: number;
  performance_tier: PerformanceTier;
};
