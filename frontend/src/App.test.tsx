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
});
