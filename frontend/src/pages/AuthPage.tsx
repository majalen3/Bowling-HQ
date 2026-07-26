import { useState } from 'react';

import { loginUser, registerUser } from '../services/api';

type Mode = 'login' | 'register';

export function AuthPage() {
  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async (): Promise<void> => {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      if (mode === 'register') {
        const user = await registerUser({
          email,
          display_name: displayName,
          password,
        });
        setMessage(`Registered ${user.email}. You can now log in.`);
        setMode('login');
      } else {
        const token = await loginUser({ email, password });
        window.localStorage.setItem('bowling_hq_token', token.access_token);
        setMessage('Logged in successfully.');
      }
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Authentication failed',
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="stack">
      <header className="hero">
        <p className="eyebrow">Account</p>
        <h1>{mode === 'login' ? 'Log In' : 'Create Account'}</h1>
        <p className="subtext">
          Access your personal arsenal and analytics.
        </p>
      </header>

      {error && <p role="alert">{error}</p>}
      {message && <p className="success-note">{message}</p>}

      <section className="card">
        <div className="form-group">
          <label htmlFor="authEmail">Email</label>
          <input
            id="authEmail"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        {mode === 'register' && (
          <div className="form-group">
            <label htmlFor="authName">Display Name</label>
            <input
              id="authName"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
            />
          </div>
        )}
        <div className="form-group">
          <label htmlFor="authPassword">Password</label>
          <input
            id="authPassword"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        <button type="button" onClick={onSubmit} disabled={busy}>
          {mode === 'login' ? 'Log In' : 'Register'}
        </button>
        <button
          type="button"
          className="link-button"
          onClick={() =>
            setMode((prev) => (prev === 'login' ? 'register' : 'login'))
          }
        >
          {mode === 'login'
            ? 'Need an account? Register'
            : 'Have an account? Log in'}
        </button>
      </section>
    </section>
  );
}
