import type { BallItem } from './arsenal';

export type LineupCreateInput = {
  name: string;
  pattern_name?: string;
};

export type LineupBallAddInput = {
  ball_id: string;
  slot_order: number;
  rationale?: string;
};

export type LineupBall = {
  id: string;
  ball_id: string;
  slot_order: number;
  rationale: string | null;
  ball: BallItem;
};

export type TournamentLineup = {
  id: string;
  user_id: string;
  name: string;
  pattern_name: string | null;
  created_at: string;
};

export type TournamentLineupDetail = TournamentLineup & {
  balls: LineupBall[];
};

export type LineupRecommendation = {
  ball_id: string;
  slot_order: number;
  role: string;
  reasoning: string;
  ball: BallItem;
};
