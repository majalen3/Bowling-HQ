import { useEffect, useState } from 'react';

import { fetchGhostBowlerProfile } from '../services/api';
import type { GhostBowlerProfile } from '../types/ghostBowler';

const TREND_LABELS: Record<string, string> = {
  improving: '📈 Improving',
  consistent: '➡️ Consistent',
  declining: '📉 Declining',
};

const TIER_LABELS: Record<string, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
  expert: 'Expert',
};

export function GhostBowlerPage() {
  const [profile, setProfile] = useState<GhostBowlerProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    fetchGhostBowlerProfile()
      .then((data) => {
        if (isActive) {
          setProfile(data);
        }
      })
      .catch((loadError) => {
        if (isActive) {
          setError(loadError instanceof Error ? loadError.message : 'Failed to load profile');
        }
      });
    return () => {
      isActive = false;
    };
  }, []);

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="hero">
          <p className="eyebrow">Ghost Bowler</p>
          <h1>Performance Profile</h1>
          <p className="subtext">Your bowling history, analyzed.</p>
        </header>
        {error && <p role="alert">{error}</p>}
        {!profile && !error && <p>Loading profile…</p>}
        {profile && (
          <div className="stack">
            <div className="card">
              <p className="eyebrow">Performance tier</p>
              <h2>{TIER_LABELS[profile.performance_tier]}</h2>
              <p className="subtext">{TREND_LABELS[profile.trend]}</p>
            </div>

            <div className="card">
              <h2>Scoring stats</h2>
              <ul>
                <li>Average score: {profile.average_score}</li>
                <li>High game: {profile.high_game}</li>
                <li>Total games: {profile.total_games}</li>
                <li>Total sessions: {profile.total_sessions}</li>
                <li>Predicted next game: {profile.predicted_next_game}</li>
                <li>Consistency score: {profile.consistency_score}/100</li>
              </ul>
            </div>

            <div className="card">
              <h2>Sessions by type</h2>
              <ul>
                {profile.sessions_by_type.map((entry) => (
                  <li key={entry.session_type}>
                    {entry.session_type}: {entry.count}
                  </li>
                ))}
                {profile.sessions_by_type.length === 0 && <li>No sessions recorded yet.</li>}
              </ul>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
