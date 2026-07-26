import { fetchProgressSnapshot } from './api';

const originalFetch = global.fetch;

afterEach(() => {
  if (originalFetch) {
    global.fetch = originalFetch;
  } else {
    delete (global as { fetch?: typeof fetch }).fetch;
  }
});

describe('fetchProgressSnapshot', () => {
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
});
