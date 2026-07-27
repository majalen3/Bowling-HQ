import type { BowlingBall } from './arsenal';

export type Strategy = 'conservative' | 'versatile' | 'aggressive' | 'defensive';
export type LineupRole = 'primary' | 'secondary' | 'tertiary' | 'spare';

export type LineupCreateInput = {
  name: string;
  tournament_name?: string;
  pattern_id?: string;
  strategy?: Strategy;
  notes?: string;
};

export type LineupBallAddInput = {
  user_arsenal_id: string;
  role: LineupRole;
  notes?: string;
};

export type LineupBall = {
  id: string;
  user_arsenal_id: string;
  role: LineupRole;
  order_index: number;
  notes: string | null;
  ball: BowlingBall;
};

export type TournamentLineup = {
  id: string;
  user_id: string;
  name: string;
  tournament_name: string | null;
  pattern_id: string | null;
  strategy: string | null;
  notes: string | null;
  created_at: string;
};

export type TournamentLineupDetail = TournamentLineup & {
  balls: LineupBall[];
};

export type LineupRecommendation = {
  user_arsenal_id: string;
  role: LineupRole;
  reasoning: string;
  ball: BowlingBall;
};
