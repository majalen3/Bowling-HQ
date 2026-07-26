import { Link } from 'react-router-dom';

const QUICK_ACTIONS = [
  {
    to: '/sessions',
    title: 'Log Session Scores',
    description: 'Start a session, add games, and track completion.',
  },
  {
    to: '/arsenal',
    title: 'Manage Arsenal',
    description: 'Add your bowling balls and keep your bag current.',
  },
  {
    to: '/commander',
    title: 'Get Ball Recommendation',
    description: 'Run Commander AI for your next opening-ball call.',
  },
  {
    to: '/analytics',
    title: 'Review Performance',
    description: 'See your averages, highs, and recent trend lines.',
  },
  {
    to: '/auth',
    title: 'Sign In / Register',
    description: 'Save your progress with your own account.',
  },
] as const;

export function HomePage() {
  return (
    <section className="stack">
      <header className="hero">
        <p className="eyebrow">Bowling-HQ</p>
        <h1>Tap a workflow and start bowling smarter</h1>
        <p className="subtext">
          Everything below is clickable so you can jump straight into scoring,
          recommendations, and analytics.
        </p>
      </header>

      <section className="card">
        <h2>Quick Start</h2>
        <ol className="quick-steps">
          <li>
            <Link to="/auth">Sign in or create your account</Link>
          </li>
          <li>
            <Link to="/arsenal">Add your current bowling balls</Link>
          </li>
          <li>
            <Link to="/sessions">Start a session and log scores</Link>
          </li>
        </ol>
      </section>

      <section className="quick-actions">
        {QUICK_ACTIONS.map((action) => (
          <Link key={action.to} to={action.to} className="quick-action-card">
            <strong>{action.title}</strong>
            <span className="subtext">{action.description}</span>
          </Link>
        ))}
      </section>
    </section>
  );
}
