import type { ArsenalAddInput, ArsenalItem, BowlingBall } from '../types/arsenal';
import type { CommanderRequestInput, CommanderResponse } from '../types/commander';
import type { ApiConfig } from '../types/env';
import type { GhostBowlerProfile } from '../types/ghostBowler';
import type { LanePattern, LanePatternDetail } from '../types/patterns';
import type { ProgressSnapshot } from '../types/progress';
import type {
  SessionCreateInput,
  SessionProgressItem,
  SessionProgressSnapshot,
} from '../types/sessionProgress';
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

// --- Arsenal DNA ---

export async function fetchBallCatalog(filters?: {
  oil_condition?: string;
  coverstock_type?: string;
}): Promise<BowlingBall[]> {
  const params = new URLSearchParams();
  if (filters?.oil_condition) {
    params.set('oil_condition', filters.oil_condition);
  }
  if (filters?.coverstock_type) {
    params.set('coverstock_type', filters.coverstock_type);
  }
  const query = params.toString();
  const response = await fetch(
    `${apiConfig.baseUrl}/arsenal/catalog${query ? `?${query}` : ''}`,
  );

  if (!response.ok) {
    throw new Error(`Failed to load ball catalog (${response.status})`);
  }

  return (await response.json()) as BowlingBall[];
}

export async function fetchUserArsenal(): Promise<ArsenalItem[]> {
  const response = await fetch(`${apiConfig.baseUrl}/arsenal`);

  if (!response.ok) {
    throw new Error(`Failed to load arsenal (${response.status})`);
  }

  return (await response.json()) as ArsenalItem[];
}

export async function addToArsenal(payload: ArsenalAddInput): Promise<ArsenalItem> {
  const response = await fetch(`${apiConfig.baseUrl}/arsenal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Failed to add ball to arsenal (${response.status})`);
  }

  return (await response.json()) as ArsenalItem;
}

export async function removeFromArsenal(userArsenalId: string): Promise<void> {
  const response = await fetch(`${apiConfig.baseUrl}/arsenal/${userArsenalId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Failed to remove ball from arsenal (${response.status})`);
  }
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

