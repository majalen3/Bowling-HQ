import { render, screen } from '@testing-library/react';

import { App } from './App';

describe('App', () => {
  it('renders the project heading', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Bowling-HQ' })).toBeInTheDocument();
  });
});
