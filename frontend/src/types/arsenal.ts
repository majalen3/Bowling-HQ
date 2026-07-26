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
