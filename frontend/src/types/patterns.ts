import type { PatternInput } from './recommendations';

export type PatternAnalysisRequest = {
  pattern: PatternInput;
};

export type PatternAnalysisResponse = {
  pattern_name: string;
  difficulty_score: number;
  difficulty_label: string;
  breakpoint_board: number;
  transition_risk: string;
  transition_rate: number;
  guidance: string[];
};
