import type { ApiConfig } from '../types/env';
import type { ProgressSnapshot } from '../types/progress';
import type {
  SessionCreateInput,
  SessionProgressItem,
  SessionProgressSnapshot,
} from '../types/sessionProgress';

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
