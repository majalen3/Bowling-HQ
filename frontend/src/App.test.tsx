import { render, screen } from '@testing-library/react';

import { App } from './App';

describe('App', () => {
  it('renders the progress dashboard heading', async () => {
    jest.spyOn(global, 'fetch').mockResolvedValue({
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
    } as Response);

    render(<App />);

    expect(await screen.findByRole('heading', { name: 'Bowling-HQ Progress' })).toBeInTheDocument();
  });
});
