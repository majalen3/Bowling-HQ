import type { RecommendationRequest, RecommendationResponse } from './recommendations';
import type { GhostBowlerBaselineResponse } from './ghostBowler';
import type { PatternAnalysisResponse } from './patterns';
import type { SimulatorResponse } from './simulator';

export type CommanderRequest = RecommendationRequest;

export type CommanderResponse = {
  ghost_bowler: GhostBowlerBaselineResponse;
  pattern_analysis: PatternAnalysisResponse;
  opening_ball: RecommendationResponse;
  top_ball_simulation: SimulatorResponse | null;
  confidence: number;
  rationale: string[];
};
