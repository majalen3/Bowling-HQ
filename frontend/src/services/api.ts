import type { ApiConfig } from '../types/env';
import type { ProgressSnapshot } from '../types/progress';
import type {
  SessionCreateInput,
  SessionProgressItem,
  SessionProgressSnapshot,
} from '../types/sessionProgress';
import type {
  FramesResponse,
  GamesResponse,
  ScoreImportResult,
} from '../types/games';
import type {
  ArsenalResponse,
  BallItem,
  CreateAndAddBallRequest,
  UserArsenalBall,
} from '../types/arsenal';
import type {
  RecommendationRequest,
  RecommendationResponse,
} from '../types/recommendations';
import type { AnalyticsSummary } from '../types/analytics';
import type {
  Token,
  UserCreate,
  UserLogin,
  UserResponse,
} from '../types/auth';
import type { CommanderRequestInput, CommanderResponse } from '../types/commander';
import type { GhostBowlerProfile } from '../types/ghostBowler';
import type { LanePattern, LanePatternDetail } from '../types/patterns';
import type {
  LineupBall,
  LineupBallAddInput,
  LineupCreateInput,
  LineupRecommendation,
  TournamentLineup,
  TournamentLineupDetail,
} from '../types/tournament';

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

export async function addGameFromThrows(
  sessionId: string,
  throws: number[],
): Promise<FramesResponse> {
  const response = await fetch(
    `${apiConfig.baseUrl}/sessions/${sessionId}/games/from-throws`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ throws }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to add game from throws (${response.status})`);
  }

  return (await response.json()) as FramesResponse;
}

export async function fetchGameFrames(
  sessionId: string,
  gameId: string,
): Promise<FramesResponse> {
  const response = await fetch(
    `${apiConfig.baseUrl}/sessions/${sessionId}/games/${gameId}/frames`,
  );

  if (!response.ok) {
    throw new Error(`Failed to load frames (${response.status})`);
  }

  return (await response.json()) as FramesResponse;
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

// --- Arsenal DNA ---

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

// --- Commander AI ---

export async function fetchCommanderRecommendation(
  payload: CommanderRequestInput,
): Promise<CommanderResponse> {
  const response = await fetch(`${apiConfig.baseUrl}/commander/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch recommendation (${response.status})`);
  }

  return (await response.json()) as CommanderResponse;
}

// --- Pattern Intelligence ---

export async function fetchPatterns(filters?: {
  difficulty?: number;
  pattern_type?: string;
}): Promise<LanePattern[]> {
  const params = new URLSearchParams();
  if (filters?.difficulty !== undefined) {
    params.set('difficulty', String(filters.difficulty));
  }
  if (filters?.pattern_type) {
    params.set('pattern_type', filters.pattern_type);
  }
  const query = params.toString();
  const response = await fetch(
    `${apiConfig.baseUrl}/patterns${query ? `?${query}` : ''}`,
  );

  if (!response.ok) {
    throw new Error(`Failed to load patterns (${response.status})`);
  }

  return (await response.json()) as LanePattern[];
}

export async function fetchPatternDetail(patternId: string): Promise<LanePatternDetail> {
  const response = await fetch(`${apiConfig.baseUrl}/patterns/${patternId}`);

  if (!response.ok) {
    throw new Error(`Failed to load pattern detail (${response.status})`);
  }

  return (await response.json()) as LanePatternDetail;
}

// --- Tournament Bag ---

export async function fetchLineups(): Promise<TournamentLineup[]> {
  const response = await fetch(`${apiConfig.baseUrl}/tournament/lineups`);

  if (!response.ok) {
    throw new Error(`Failed to load lineups (${response.status})`);
  }

  return (await response.json()) as TournamentLineup[];
}

export async function createLineup(
  payload: LineupCreateInput,
): Promise<TournamentLineup> {
  const response = await fetch(`${apiConfig.baseUrl}/tournament/lineups`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to create lineup (${response.status})`);
  }

  return (await response.json()) as TournamentLineup;
}

export async function fetchLineupDetail(
  lineupId: string,
): Promise<TournamentLineupDetail> {
  const response = await fetch(`${apiConfig.baseUrl}/tournament/lineups/${lineupId}`);

  if (!response.ok) {
    throw new Error(`Failed to load lineup (${response.status})`);
  }

  return (await response.json()) as TournamentLineupDetail;
}

export async function recommendLineup(
  lineupId: string,
): Promise<LineupRecommendation[]> {
  const response = await fetch(
    `${apiConfig.baseUrl}/tournament/lineups/${lineupId}/recommend`,
    { method: 'POST' },
  );

  if (!response.ok) {
    throw new Error(`Failed to auto-fill lineup (${response.status})`);
  }

  return (await response.json()) as LineupRecommendation[];
}

export async function addLineupBall(
  lineupId: string,
  payload: LineupBallAddInput,
): Promise<LineupBall> {
  const response = await fetch(
    `${apiConfig.baseUrl}/tournament/lineups/${lineupId}/balls`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to add ball to lineup (${response.status})`);
  }

  return (await response.json()) as LineupBall;
}

export async function removeLineupBall(
  lineupId: string,
  lineupBallId: string,
): Promise<void> {
  const response = await fetch(
    `${apiConfig.baseUrl}/tournament/lineups/${lineupId}/balls/${lineupBallId}`,
    { method: 'DELETE' },
  );

  if (!response.ok) {
    throw new Error(`Failed to remove ball from lineup (${response.status})`);
  }
}

// --- Ghost Bowler ---

export async function fetchGhostBowlerProfile(): Promise<GhostBowlerProfile> {
  const response = await fetch(`${apiConfig.baseUrl}/ghost-bowler/profile`);

  if (!response.ok) {
    throw new Error(`Failed to load ghost bowler profile (${response.status})`);
  }

  return (await response.json()) as GhostBowlerProfile;
}

// --- Recommendations (physics-based) ---

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

// --- Analytics ---

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const response = await fetch(`${apiConfig.baseUrl}/analytics/summary`);

  if (!response.ok) {
    throw new Error(`Failed to load analytics (${response.status})`);
  }

  return (await response.json()) as AnalyticsSummary;
}

// --- Auth ---

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
