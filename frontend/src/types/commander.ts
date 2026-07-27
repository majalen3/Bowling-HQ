import type { BallItem } from './arsenal';

export type LaneCondition = 'dry' | 'light' | 'medium' | 'heavy' | 'very_heavy';
export type ReleaseStyle = 'controlled' | 'balanced' | 'power';
export type RecommendationRole = 'primary' | 'alternative' | 'backup';

export type CommanderRequestInput = {
  lane_condition: LaneCondition;
  pattern_difficulty: number;
  ball_speed: number;
  release_style: ReleaseStyle;
};

export type BallRecommendation = {
  role: RecommendationRole;
  confidence: number;
  reasoning: string;
  ball: BallItem;
  arsenal_id: string | null;
};

export type CommanderResponse = {
  from_arsenal: boolean;
  recommendations: BallRecommendation[];
};
