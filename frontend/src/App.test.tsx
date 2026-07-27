import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { App } from './App';

const originalFetch = global.fetch;

afterEach(() => {
  if (originalFetch) {
    global.fetch = originalFetch;
  } else {
    delete (global as { fetch?: typeof fetch }).fetch;
  }
  window.history.pushState({}, '', '/');
});

function installMockFetch(): jest.Mock {
  const mockFetch = jest.fn().mockImplementation((input: RequestInfo | URL) => {
    const requestUrl = String(input);
    if (requestUrl.endsWith('/analytics/summary')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          overall_average: 195.5,
          high_game: 268,
          total_games: 12,
          total_sessions: 4,
          recent_trend: [],
          per_ball_averages: [],
        }),
      });
    }
    if (requestUrl.endsWith('/sessions/progress')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          total_sessions: 0,
          completed_sessions: 0,
          active_sessions: 0,
          sessions: [],
        }),
      });
    }
    if (requestUrl.endsWith('/arsenal/catalog')) {
      return Promise.resolve({
        ok: true,
        json: async () => [],
      });
    }
    return Promise.resolve({ ok: false, status: 404, json: async () => ({}) });
  });

  Object.defineProperty(global, 'fetch', {
    value: mockFetch,
    configurable: true,
    writable: true,
  });
  return mockFetch;
}

describe('App', () => {
  it('renders the Commander landing page and navigation', async () => {
    installMockFetch();
    render(<App />);

    expect(
      await screen.findByRole('heading', { name: 'Opening Ball Advisor' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Commander' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Sessions' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Arsenal' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Analytics' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Progress' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Dev' })).toBeInTheDocument();
  });

  it('navigates to the Analytics page and shows stats', async () => {
    installMockFetch();
    render(<App />);

    fireEvent.click(screen.getByRole('link', { name: 'Analytics' }));

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Performance Summary' }),
      ).toBeInTheDocument();
    });
    expect(await screen.findByText('195.5')).toBeInTheDocument();
    expect(screen.getByText('268')).toBeInTheDocument();
  });

  it('runs simulator using the selected recommendation ball specs', async () => {
    const mockFetch = jest.fn().mockImplementation((input: RequestInfo | URL) => {
      const requestUrl = String(input);
      if (requestUrl.endsWith('/arsenal/catalog')) {
        return Promise.resolve({
          ok: true,
          json: async () => [
            {
              id: 'ball-1',
              name: 'Solid One',
              brand: 'Storm',
              coverstock: 'solid reactive',
              rg: 2.48,
              differential: 0.05,
              mass_bias: 0.0,
              surface_grit: 2000,
              weight_lbs: 15,
              created_at: '2026-01-01T00:00:00Z',
            },
            {
              id: 'ball-2',
              name: 'Pearl Two',
              brand: 'Motiv',
              coverstock: 'pearl reactive',
              rg: 2.55,
              differential: 0.04,
              mass_bias: 0.0,
              surface_grit: 4000,
              weight_lbs: 15,
              created_at: '2026-01-01T00:00:00Z',
            },
          ],
        });
      }
      if (requestUrl.endsWith('/recommendations/opening-ball')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            pattern_difficulty_score: 4.1,
            pattern_difficulty_label: 'medium',
            breakpoint_board: 9,
            bowler_type: 'tweener',
            session_id: null,
            recommendations: [
              {
                rank: 1,
                ball_id: 'ball-1',
                ball_name: 'Solid One',
                fit_score: 92,
                confidence: 0.8,
                matched_shape: 'arc',
                reasoning: ['good'],
                breakpoint_board: 8.8,
                entry_angle_deg: 5.1,
                strike_probability: 0.67,
              },
              {
                rank: 2,
                ball_id: 'ball-2',
                ball_name: 'Pearl Two',
                fit_score: 88,
                confidence: 0.76,
                matched_shape: 'flip',
                reasoning: ['backup'],
                breakpoint_board: 9.1,
                entry_angle_deg: 5.3,
                strike_probability: 0.64,
              },
            ],
          }),
        });
      }
      if (requestUrl.endsWith('/simulator/run')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            predicted_score: 221,
            confidence_low: 205,
            confidence_high: 236,
            strike_probability: 0.66,
            confidence: 0.79,
            breakpoint_board: 9.2,
            entry_angle_deg: 5.2,
            notes: ['simulated'],
          }),
        });
      }
      return Promise.resolve({ ok: false, status: 404, json: async () => ({}) });
    });
    Object.defineProperty(global, 'fetch', {
      value: mockFetch,
      configurable: true,
      writable: true,
    });

    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: 'Get Recommendation' }));
    expect(await screen.findByRole('heading', { name: 'Ball Selection' })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Simulation ball'), { target: { value: 'ball-2' } });
    fireEvent.click(screen.getByRole('button', { name: 'Run Simulator' }));

    await screen.findByText('Strike probability: 66%');

    const simulatorCall = mockFetch.mock.calls.find((call) =>
      String(call[0]).endsWith('/simulator/run'),
    );
    expect(simulatorCall).toBeDefined();
    const simulatorBody = JSON.parse(String(simulatorCall?.[1]?.body ?? '{}'));
    expect(simulatorBody.ball).toMatchObject({
      name: 'Pearl Two',
      coverstock: 'pearl reactive',
      rg: 2.55,
      differential: 0.04,
      mass_bias: 0,
      surface_grit: 4000,
    });
  });
});
