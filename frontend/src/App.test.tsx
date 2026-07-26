import { render, screen } from '@testing-library/react';

import { App } from './App';

describe('App', () => {
  it('renders the progress dashboard heading', async () => {
    Object.defineProperty(global, 'fetch', {
      value: jest.fn().mockResolvedValue({
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
        ],
      }),
      }),
      configurable: true,
      writable: true,
    });

    render(<App />);

    expect(await screen.findByRole('heading', { name: 'Bowling-HQ Progress' })).toBeInTheDocument();
  });
});
