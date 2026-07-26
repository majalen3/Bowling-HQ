import { useEffect, useState } from 'react';

import { fetchAnalyticsSummary } from '../services/api';
import type { AnalyticsSummary } from '../types/analytics';

export function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async (): Promise<void> => {
      try {
        const data = await fetchAnalyticsSummary();
        if (active) {
          setSummary(data);
          setError(null);
        }
      } catch (loadError) {
        if (active) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Failed to load analytics',
          );
        }
      }
    };
    load();
    return () => {
      active = false;
    };
  }, []);

  const formatDate = (iso: string): string => {
    const date = new Date(iso);
    return Number.isNaN(date.getTime())
      ? iso
      : date.toLocaleDateString();
  };

  return (
    <section className="stack">
      <header className="hero">
        <p className="eyebrow">Analytics</p>
        <h1>Performance Summary</h1>
        <p className="subtext">Scoring trends across your sessions.</p>
      </header>

      {error && <p role="alert">{error}</p>}
      {!summary && !error && <p>Loading analytics…</p>}

      {summary && (
        <>
          <section className="stats-grid">
            <div className="stat-card">
              <span className="stat-label">Overall Average</span>
              <span className="stat-value">{summary.overall_average}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">High Game</span>
              <span className="stat-value">{summary.high_game}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Total Games</span>
              <span className="stat-value">{summary.total_games}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Total Sessions</span>
              <span className="stat-value">{summary.total_sessions}</span>
            </div>
          </section>

          <section className="card">
            <h2>Recent Sessions</h2>
            {summary.recent_trend.length === 0 ? (
              <p className="subtext">No sessions recorded yet.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Location</th>
                    <th>Games</th>
                    <th>Avg</th>
                    <th>High</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.recent_trend.map((point) => (
                    <tr key={point.session_id}>
                      <td>{formatDate(point.date)}</td>
                      <td>{point.location_name ?? '—'}</td>
                      <td>{point.game_count}</td>
                      <td>{point.average}</td>
                      <td>{point.high_game}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          {summary.per_ball_averages.length > 0 && (
            <section className="card">
              <h2>Per-Ball Averages</h2>
              <ul>
                {summary.per_ball_averages.map((ball) => (
                  <li key={ball.ball_id}>
                    <strong>{ball.ball_name}</strong>: {ball.average} avg
                    over {ball.game_count} games
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </section>
  );
}
