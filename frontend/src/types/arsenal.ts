export type BallItem = {
  id: string;
  name: string;
  brand: string;
  coverstock: string;
  rg: number;
  differential: number;
  mass_bias: number;
  surface_grit: number;
  weight_lbs: number;
  created_at: string;
};

export type UserArsenalBall = {
  id: string;
  ball: BallItem;
  notes: string | null;
  added_at: string;
};

export type ArsenalResponse = {
  user_id: string;
  balls: UserArsenalBall[];
  count: number;
};

export type CreateAndAddBallRequest = {
  name: string;
  brand: string;
  coverstock: string;
  rg: number;
  differential: number;
  mass_bias?: number;
  surface_grit?: number;
  weight_lbs?: number;
  notes?: string;
};

export type ArsenalFitRequest = {
  pattern: {
    name?: string;
    length_ft: number;
    volume_ml: number;
    asymmetry_index: number;
    front_oil_pct: number;
    mid_oil_pct: number;
    backend_oil_pct: number;
    lane_surface: string;
  };
  bowler: {
    average: number;
    speed_mph: number;
    rev_rate: number;
    axis_rotation_deg: number;
    axis_tilt_deg: number;
    consistency: number;
  };
  top_n: number;
};

export type ArsenalFitRecommendation = {
  rank: number;
  ball_id: string;
  ball_name: string;
  fit_score: number;
  confidence: number;
  reasons: string[];
};

export type ArsenalFitResponse = {
  recommendations: ArsenalFitRecommendation[];
};
