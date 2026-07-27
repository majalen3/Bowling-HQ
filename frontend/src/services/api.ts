import type { ApiConfig } from '../types/env';
import type { ProgressSnapshot } from '../types/progress';
import type {
  SessionCreateInput,
  SessionProgressItem,
  SessionProgressSnapshot,
} from '../types/sessionProgress';
import type {
  GamesResponse,
  ScoreImportResult,
} from '../types/games';
import type {
  ArsenalFitRequest,
  ArsenalFitResponse,
  ArsenalResponse,
  BallItem,
  CreateAndAddBallRequest,
  UserArsenalBall,
} from '../types/arsenal';
import type {
  GhostBowlerBaselineResponse,
  GhostBowlerCompareResponse,
} from '../types/ghostBowler';
import type {
  PatternAnalysisRequest,
  PatternAnalysisResponse,
} from '../types/patterns';
import type {
  RecommendationRequest,
  RecommendationResponse,
} from '../types/recommendations';
import type { SimulatorRequest, SimulatorResponse } from '../types/simulator';
import type { AnalyticsSummary } from '../types/analytics';
import type { CommanderRequest, CommanderResponse } from '../types/commander';
import type {
  Token,
  UserCreate,
  UserLogin,
  UserResponse,
} from '../types/auth';

const runtimeEnv = typeof process !== 'undefined' ? process.env : undefined;

export const apiConfig: ApiConfig = {
  baseUrl: runtimeEnv?.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  appName: runtimeEnv?.VITE_APP_NAME ?? 'Bowling-HQ',
};

export async function fetchProgressSnapshot(): Promise<ProgressSnapshot> {
  const response = await fetch(`${apiConfig.baseUrl}/progress`);

  if (!response.ok) {
    throw new Error(`Failed to load progress snapshot (${response.status})`);
  }

  return (await response.json()) as ProgressSnapshot;
}

export async function fetchSessionProgress(): Promise<SessionProgressSnapshot> {
  const response = await fetch(`${apiConfig.baseUrl}/sessions/progress`);

  if (!response.ok) {
    throw new Error(`Failed to load session progress (${response.status})`);
  }

  return (await response.json()) as SessionProgressSnapshot;
}

export async function createSession(
  payload: SessionCreateInput,
): Promise<SessionProgressItem> {
  const response = await fetch(`${apiConfig.baseUrl}/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to start session (${response.status})`);
  }

  return (await response.json()) as SessionProgressItem;
}

export async function completeSession(
  sessionId: string,
): Promise<SessionProgressItem> {
  const response = await fetch(
    `${apiConfig.baseUrl}/sessions/${sessionId}/complete`,
    {
      method: 'POST',
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to complete session (${response.status})`);
  }

  return (await response.json()) as SessionProgressItem;
}

export async function fetchSessionGames(
  sessionId: string,
): Promise<GamesResponse> {
  const response = await fetch(
    `${apiConfig.baseUrl}/sessions/${sessionId}/games`,
  );

  if (!response.ok) {
    throw new Error(`Failed to load games (${response.status})`);
  }

  return (await response.json()) as GamesResponse;
}

export async function addGamesToSession(
  sessionId: string,
  scores: number[],
): Promise<GamesResponse> {
  const response = await fetch(
    `${apiConfig.baseUrl}/sessions/${sessionId}/games`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ scores }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to add games (${response.status})`);
  }

  return (await response.json()) as GamesResponse;
}

export async function importScores(
  sessionId: string,
  csvText: string,
  source: string,
): Promise<ScoreImportResult> {
  const response = await fetch(
    `${apiConfig.baseUrl}/sessions/${sessionId}/import-scores`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ csv_text: csvText, source }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to import scores (${response.status})`);
  }

  return (await response.json()) as ScoreImportResult;
}

export async function fetchArsenal(): Promise<ArsenalResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/arsenal`);

  if (!response.ok) {
    throw new Error(`Failed to load arsenal (${response.status})`);
  }

  return (await response.json()) as ArsenalResponse;
}

export async function addBallToArsenal(
  payload: CreateAndAddBallRequest,
): Promise<UserArsenalBall> {
  const response = await fetch(`${apiConfig.baseUrl}/arsenal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to add ball (${response.status})`);
  }

  return (await response.json()) as UserArsenalBall;
}

export async function removeBallFromArsenal(
  arsenalId: string,
): Promise<void> {
  const response = await fetch(
    `${apiConfig.baseUrl}/arsenal/${arsenalId}`,
    {
      method: 'DELETE',
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to remove ball (${response.status})`);
  }
}

export async function fetchBallCatalog(): Promise<BallItem[]> {
  const response = await fetch(`${apiConfig.baseUrl}/arsenal/catalog`);

  if (!response.ok) {
    throw new Error(`Failed to load catalog (${response.status})`);
  }

  return (await response.json()) as BallItem[];
}

export async function getOpeningBallRecommendation(
  payload: RecommendationRequest,
): Promise<RecommendationResponse> {
  const response = await fetch(
    `${apiConfig.baseUrl}/recommendations/opening-ball`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to get recommendation (${response.status})`);
  }

  return (await response.json()) as RecommendationResponse;
}

export async function fetchGhostBowlerBaseline(): Promise<GhostBowlerBaselineResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/ghost-bowler`);
  if (!response.ok) {
    throw new Error(`Failed to load ghost bowler baseline (${response.status})`);
  }
  return (await response.json()) as GhostBowlerBaselineResponse;
}

export async function compareGhostBowlerBaseline(
  currentAverage: number,
  conditionFamily = 'overall',
): Promise<GhostBowlerCompareResponse> {
  const params = new URLSearchParams({
    current_average: String(currentAverage),
    condition_family: conditionFamily,
  });
  const response = await fetch(
    `${apiConfig.baseUrl}/ghost-bowler/compare?${params.toString()}`,
  );
  if (!response.ok) {
    throw new Error(`Failed to compare ghost baseline (${response.status})`);
  }
  return (await response.json()) as GhostBowlerCompareResponse;
}

export async function analyzePattern(
  payload: PatternAnalysisRequest,
): Promise<PatternAnalysisResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/patterns/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to analyze pattern (${response.status})`);
  }

  return (await response.json()) as PatternAnalysisResponse;
}

export async function runBallSimulator(
  payload: SimulatorRequest,
): Promise<SimulatorResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/simulator/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to run simulator (${response.status})`);
  }

  return (await response.json()) as SimulatorResponse;
}

export async function getArsenalFit(
  payload: ArsenalFitRequest,
): Promise<ArsenalFitResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/arsenal/fit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Failed to score arsenal fit (${response.status})`);
  }
  return (await response.json()) as ArsenalFitResponse;
}

export async function getCommanderRecommendation(
  payload: CommanderRequest,
): Promise<CommanderResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/commander/recommendation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Failed to get commander recommendation (${response.status})`);
  }
  return (await response.json()) as CommanderResponse;
}

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const response = await fetch(`${apiConfig.baseUrl}/analytics/summary`);

  if (!response.ok) {
    throw new Error(`Failed to load analytics (${response.status})`);
  }

  return (await response.json()) as AnalyticsSummary;
}

export async function registerUser(
  payload: UserCreate,
): Promise<UserResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to register (${response.status})`);
  }

  return (await response.json()) as UserResponse;
}

export async function loginUser(payload: UserLogin): Promise<Token> {
  const response = await fetch(`${apiConfig.baseUrl}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to login (${response.status})`);
  }

  return (await response.json()) as Token;
}
