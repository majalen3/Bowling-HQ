import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { App } from './App';

const originalFetch = global.fetch;

afterEach(() => {
  if (originalFetch) {
    global.fetch = originalFetch;
  } else {
    delete (global as { fetch?: typeof fetch }).fetch;
  }
});

describe('App', () => {
  it('renders dashboard and runs session workflow', async () => {
    const sessions = [
      {
        id: 'session-1',
        session_type: 'practice',
        location_name: 'House Shot',
        started_at: '2026-01-01T00:00:00Z',
        completed_at: null,
      },
    ];
    const fetchMock = jest.fn().mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const requestUrl = String(input);
      if (requestUrl.endsWith('/sessions/progress')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            total_sessions: sessions.length,
            completed_sessions: sessions.filter((session) => session.completed_at).length,
            active_sessions: sessions.filter((session) => !session.completed_at).length,
            sessions,
          }),
        });
      }
      if (requestUrl.endsWith('/progress')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            finished_target: 'Ship MVP',
            scope_lock: ['Progress board visibility'],
            release_gate: ['make test passes'],
            board: [
              {
                id: 'MVP-001',
                title: 'Define target',
                status: 'done',
                done_criteria: ['Scope locked'],
              },
              {
                id: 'MVP-004',
                title: 'Complete vertical slices',
                status: 'in_progress',
                done_criteria: ['Slice 1 sessions completed: 0/1'],
              },
            ],
          }),
        });
      }
      if (requestUrl.endsWith('/sessions') && init?.method === 'POST') {
        sessions.push({
          id: 'session-2',
          session_type: 'league',
          location_name: null,
          started_at: '2026-01-01T01:00:00Z',
          completed_at: null,
        });
        return Promise.resolve({
          ok: true,
          json: async () => sessions[1],
        });
      }
      if (requestUrl.includes('/sessions/session-1/complete')) {
        sessions[0].completed_at = '2026-01-01T00:10:00Z';
        return Promise.resolve({
          ok: true,
          json: async () => sessions[0],
        });
      }
      return Promise.resolve({
        ok: false,
        status: 404,
      });
    });

    Object.defineProperty(global, 'fetch', {
      value: fetchMock,
      configurable: true,
      writable: true,
    });

    render(<App />);

    expect(await screen.findByRole('heading', { name: 'Bowling-HQ Progress' })).toBeInTheDocument();
    expect(await screen.findByText('Sessions: 1 total / 0 completed / 1 active')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Session Type'), {
      target: { value: 'league' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Start session' }));
    await screen.findByText('Sessions: 2 total / 0 completed / 2 active');

    fireEvent.click(screen.getByRole('button', { name: 'Mark complete' }));
    await waitFor(() => {
      expect(
        screen.getByText('Sessions: 2 total / 1 completed / 1 active'),
      ).toBeInTheDocument();
    });
  });
});
