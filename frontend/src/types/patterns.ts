import type { BallItem } from './arsenal';

export type LanePattern = {
  id: string;
  name: string;
  length_ft: number;
  volume_ml: number;
  asymmetry_index: number;
  front_oil_pct: number;
  mid_oil_pct: number;
  backend_oil_pct: number;
  created_at: string;
};

export type LanePatternDetail = LanePattern & {
  recommended_balls: BallItem[];
};
