export type CoverstockType =
  | 'plastic'
  | 'urethane'
  | 'reactive_resin'
  | 'pearl_reactive';

export type CoreType = 'symmetrical' | 'asymmetrical';

export type OilCondition = 'dry' | 'light' | 'medium' | 'heavy' | 'very_heavy' | 'any';

export type BowlingBall = {
  id: string;
  brand: string;
  name: string;
  coverstock_type: CoverstockType;
  core_type: CoreType;
  rg: number | null;
  differential: number | null;
  hook_potential: number | null;
  length: number | null;
  backend: number | null;
  oil_condition: OilCondition | null;
  weight_options: string | null;
  description: string | null;
  created_at: string;
};

export type ArsenalItem = {
  id: string;
  ball_id: string;
  purchase_date: string | null;
  layout: string | null;
  notes: string | null;
  games_played: number;
  added_at: string;
  ball: BowlingBall;
};

export type ArsenalAddInput = {
  ball_id: string;
  purchase_date?: string;
  layout?: string;
  notes?: string;
};
