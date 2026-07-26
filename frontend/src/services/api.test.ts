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

import {
  addBallToArsenal,
  addGamesToSession,
  fetchAnalyticsSummary,
  fetchArsenal,
  fetchBallCatalog,
  fetchSessionGames,
  getOpeningBallRecommendation,
  importScores,
  loginUser,
  registerUser,
  removeBallFromArsenal,
} from './api';

function mockFetch(response: unknown, ok = true, status = 200): jest.Mock {
  const fn = jest.fn().mockResolvedValue({
    ok,
    status,
    json: async () => response,
  });
  Object.defineProperty(global, 'fetch', {
    value: fn,
    configurable: true,
    writable: true,
  });
  return fn;
}

describe('games API helpers', () => {
  it('fetches session games', async () => {
    const payload = {
      session_id: 's1',
      games: [],
      count: 0,
      average: 0,
    };
    mockFetch(payload);
    await expect(fetchSessionGames('s1')).resolves.toEqual(payload);
  });

  it('adds games to a session', async () => {
    const payload = {
      session_id: 's1',
      games: [],
      count: 1,
      average: 200,
    };
    const fetchMock = mockFetch(payload);
    await expect(addGamesToSession('s1', [200])).resolves.toEqual(payload);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/sessions/s1/games'),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('imports scores', async () => {
    const payload = {
      session_id: 's1',
      games_imported: 2,
      scores: [180, 200],
      errors: [],
    };
    mockFetch(payload);
    await expect(importScores('s1', 'Score\n180\n200', 'generic')).resolves.toEqual(
      payload,
    );
  });

  it('throws when games request fails', async () => {
    mockFetch(null, false, 500);
    await expect(fetchSessionGames('s1')).rejects.toThrow(
      'Failed to load games (500)',
    );
  });
});

describe('arsenal API helpers', () => {
  it('fetches arsenal', async () => {
    const payload = { user_id: 'u1', balls: [], count: 0 };
    mockFetch(payload);
    await expect(fetchArsenal()).resolves.toEqual(payload);
  });

  it('adds a ball', async () => {
    const payload = {
      id: 'a1',
      ball: {
        id: 'b1',
        name: 'Test',
        brand: 'B',
        coverstock: 'solid reactive',
        rg: 2.48,
        differential: 0.05,
        mass_bias: 0,
        surface_grit: 3000,
        weight_lbs: 15,
        created_at: '2026-01-01T00:00:00Z',
      },
      notes: null,
      added_at: '2026-01-01T00:00:00Z',
    };
    mockFetch(payload);
    await expect(
      addBallToArsenal({
        name: 'Test',
        brand: 'B',
        coverstock: 'solid reactive',
        rg: 2.48,
        differential: 0.05,
      }),
    ).resolves.toEqual(payload);
  });

  it('removes a ball', async () => {
    const fetchMock = mockFetch({ deleted: true });
    await expect(removeBallFromArsenal('a1')).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/arsenal/a1'),
      expect.objectContaining({ method: 'DELETE' }),
    );
  });

  it('fetches the catalog', async () => {
    mockFetch([]);
    await expect(fetchBallCatalog()).resolves.toEqual([]);
  });
});

describe('recommendation and analytics helpers', () => {
  it('posts a recommendation request', async () => {
    const payload = {
      pattern_difficulty_score: 5,
      pattern_difficulty_label: 'moderate',
      breakpoint_board: 9,
      recommendations: [],
      bowler_type: 'tweener',
      session_id: null,
    };
    mockFetch(payload);
    await expect(
      getOpeningBallRecommendation({
        pattern: {
          name: 'P',
          length_ft: 40,
          volume_ml: 24,
          asymmetry_index: 0,
          front_oil_pct: 0.34,
          mid_oil_pct: 0.33,
          backend_oil_pct: 0.33,
          lane_surface: 'synthetic',
        },
        bowler: {
          average: 190,
          speed_mph: 17,
          rev_rate: 350,
          axis_rotation_deg: 45,
          axis_tilt_deg: 15,
          consistency: 0.75,
        },
        top_n: 3,
      }),
    ).resolves.toEqual(payload);
  });

  it('fetches analytics summary', async () => {
    const payload = {
      overall_average: 0,
      high_game: 0,
      total_games: 0,
      total_sessions: 0,
      recent_trend: [],
      per_ball_averages: [],
    };
    mockFetch(payload);
    await expect(fetchAnalyticsSummary()).resolves.toEqual(payload);
  });
});

describe('auth API helpers', () => {
  it('registers a user', async () => {
    const payload = {
      id: 'u1',
      email: 'a@b.com',
      display_name: 'A',
      created_at: '2026-01-01T00:00:00Z',
    };
    mockFetch(payload);
    await expect(
      registerUser({
        email: 'a@b.com',
        display_name: 'A',
        password: 'supersecret',
      }),
    ).resolves.toEqual(payload);
  });

  it('logs in a user', async () => {
    const payload = { access_token: 'token', token_type: 'bearer' };
    mockFetch(payload);
    await expect(
      loginUser({ email: 'a@b.com', password: 'supersecret' }),
    ).resolves.toEqual(payload);
  });

  it('throws on failed login', async () => {
    mockFetch(null, false, 401);
    await expect(
      loginUser({ email: 'a@b.com', password: 'bad' }),
    ).rejects.toThrow('Failed to login (401)');
  });
});
