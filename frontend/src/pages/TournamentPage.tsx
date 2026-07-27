import { useEffect, useState } from 'react';

import {
  createLineup,
  fetchLineupDetail,
  fetchLineups,
  recommendLineup,
} from '../services/api';
import type {
  LineupRecommendation,
  TournamentLineup,
  TournamentLineupDetail,
} from '../types/tournament';

export function TournamentPage() {
  const [lineups, setLineups] = useState<TournamentLineup[] | null>(null);
  const [name, setName] = useState('');
  const [patternName, setPatternName] = useState('');
  const [selectedLineup, setSelectedLineup] = useState<TournamentLineupDetail | null>(null);
  const [recommendations, setRecommendations] = useState<LineupRecommendation[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  const loadLineups = async (): Promise<void> => {
    try {
      setLineups(await fetchLineups());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load lineups');
    }
  };

  useEffect(() => {
    loadLineups();
  }, []);

  const onCreate = async (): Promise<void> => {
    if (!name.trim()) {
      setError('Lineup name is required');
      return;
    }
    setIsBusy(true);
    try {
      await createLineup({
        name: name.trim(),
        pattern_name: patternName.trim() || undefined,
      });
      setName('');
      setPatternName('');
      setError(null);
      await loadLineups();
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : 'Failed to create lineup');
    } finally {
      setIsBusy(false);
    }
  };

  const onSelect = async (lineupId: string): Promise<void> => {
    try {
      setSelectedLineup(await fetchLineupDetail(lineupId));
      setRecommendations(null);
      setError(null);
    } catch (selectError) {
      setError(selectError instanceof Error ? selectError.message : 'Failed to load lineup');
    }
  };

  const onRecommend = async (): Promise<void> => {
    if (!selectedLineup) return;
    setIsBusy(true);
    try {
      setRecommendations(await recommendLineup(selectedLineup.id));
      setError(null);
    } catch (recError) {
      setError(recError instanceof Error ? recError.message : 'Failed to get recommendations');
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="hero">
          <p className="eyebrow">Tournament Bag</p>
          <h1>Tournament Lineups</h1>
          <p className="subtext">
            Build strategic ball lineups for tournament play.
          </p>
        </header>
        {error && <p role="alert">{error}</p>}
        <div className="stack">
          <div className="card">
            <h2>Create Lineup</h2>
            <label htmlFor="lineupName">Lineup name</label>
            <input
              id="lineupName"
              type="text"
              value={name}
              placeholder="My Tournament Lineup"
              onChange={(event) => setName(event.target.value)}
            />
            <label htmlFor="patternName">Pattern name (optional)</label>
            <input
              id="patternName"
              type="text"
              value={patternName}
              placeholder="e.g. House Shot"
              onChange={(event) => setPatternName(event.target.value)}
            />
            <button type="button" onClick={onCreate} disabled={isBusy}>
              {isBusy ? 'Creating…' : 'Create Lineup'}
            </button>
          </div>

          {!lineups && <p>Loading lineups…</p>}
          {lineups?.map((lineup) => (
            <div className="card" key={lineup.id}>
              <h2>{lineup.name}</h2>
              {lineup.pattern_name && (
                <p className="subtext">Pattern: {lineup.pattern_name}</p>
              )}
              <p className="subtext">
                Created {new Date(lineup.created_at).toLocaleDateString()}
              </p>
              <button type="button" onClick={() => onSelect(lineup.id)}>
                View lineup
              </button>
            </div>
          ))}

          {selectedLineup && (
            <div className="card">
              <h2>{selectedLineup.name}</h2>
              {selectedLineup.balls.length > 0 ? (
                <ul>
                  {selectedLineup.balls.map((lb) => (
                    <li key={lb.id}>
                      Slot {lb.slot_order}:{' '}
                      <strong>
                        {lb.ball.brand} {lb.ball.name}
                      </strong>
                      {lb.rationale && ` — ${lb.rationale}`}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No balls assigned yet.</p>
              )}
              <button type="button" onClick={onRecommend} disabled={isBusy}>
                {isBusy ? 'Computing…' : 'Auto-recommend balls from arsenal'}
              </button>
            </div>
          )}

          {recommendations && recommendations.length > 0 && (
            <div className="card">
              <h2>Recommended Lineup</h2>
              <ul>
                {recommendations.map((rec) => (
                  <li key={rec.slot_order}>
                    <strong>Slot {rec.slot_order} — {rec.role}</strong>:{' '}
                    {rec.ball.brand} {rec.ball.name}
                    <br />
                    <span className="subtext">{rec.reasoning}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {recommendations?.length === 0 && (
            <p className="subtext">
              Add balls to your arsenal first to get lineup recommendations.
            </p>
          )}
        </div>
      </section>
    </main>
  );
}
