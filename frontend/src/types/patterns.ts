import type { BowlingBall, CoverstockType } from './arsenal';

export type PatternType = 'house' | 'sport' | 'challenge' | 'pba';

export type LanePattern = {
  id: string;
  name: string;
  pattern_type: PatternType;
  oil_volume: number | null;
  oil_distance: number | null;
  difficulty: number | null;
  description: string | null;
  recommended_coverstock: CoverstockType | null;
  recommended_hook_min: number | null;
  recommended_hook_max: number | null;
  notes: string | null;
  created_at: string;
};

export type LanePatternDetail = LanePattern & {
  recommended_balls: BowlingBall[];
};
