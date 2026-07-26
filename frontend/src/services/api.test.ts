import {
  completeSession,
  createSession,
  fetchProgressSnapshot,
  fetchSessionProgress,
} from './api';

const originalFetch = global.fetch;

afterEach(() => {
  if (originalFetch) {
    global.fetch = originalFetch;
  } else {
    delete (global as { fetch?: typeof fetch }).fetch;
  }
});

describe('progress API helpers', () => {
  it('returns parsed progress data for successful responses', async () => {
    const snapshot = {
      finished_target: 'Ship MVP',
      scope_lock: ['Progress board visibility'],
      release_gate: ['make test passes'],
      board: [],
    };

    Object.defineProperty(global, 'fetch', {
      value: jest.fn().mockResolvedValue({
        ok: true,
        json: async () => snapshot,
      }),
      configurable: true,
      writable: true,
    });

    await expect(fetchProgressSnapshot()).resolves.toEqual(snapshot);
  });

  it('throws a descriptive error for non-ok responses', async () => {
    Object.defineProperty(global, 'fetch', {
      value: jest.fn().mockResolvedValue({
        ok: false,
        status: 503,
      }),
      configurable: true,
      writable: true,
    });

    await expect(fetchProgressSnapshot()).rejects.toThrow(
      'Failed to load progress snapshot (503)',
    );
  });

  it('returns parsed session progress', async () => {
    const snapshot = {
      total_sessions: 1,
      completed_sessions: 0,
      active_sessions: 1,
      sessions: [],
    };
    Object.defineProperty(global, 'fetch', {
      value: jest.fn().mockResolvedValue({
        ok: true,
        json: async () => snapshot,
      }),
      configurable: true,
      writable: true,
    });

    await expect(fetchSessionProgress()).resolves.toEqual(snapshot);
  });

  it('posts to create a session', async () => {
    const created = {
      id: 'session-1',
      session_type: 'practice',
      location_name: null,
      started_at: '2026-01-01T00:00:00Z',
      completed_at: null,
    };
    Object.defineProperty(global, 'fetch', {
      value: jest.fn().mockResolvedValue({
        ok: true,
        json: async () => created,
      }),
      configurable: true,
      writable: true,
    });

    await expect(
      createSession({ session_type: 'practice' }),
    ).resolves.toEqual(created);
  });

  it('posts to complete a session', async () => {
    const completed = {
      id: 'session-1',
      session_type: 'practice',
      location_name: null,
      started_at: '2026-01-01T00:00:00Z',
      completed_at: '2026-01-01T00:10:00Z',
    };
    Object.defineProperty(global, 'fetch', {
      value: jest.fn().mockResolvedValue({
        ok: true,
        json: async () => completed,
      }),
      configurable: true,
      writable: true,
    });

    await expect(completeSession('session-1')).resolves.toEqual(completed);
  });
});
