import { useEffect, useState } from 'react';

import {
  createLineup,
  fetchLineupDetail,
  fetchLineups,
  fetchPatterns,
  recommendLineup,
} from '../services/api';
import type { LanePattern } from '../types/patterns';
import type {
  LineupRecommendation,
  Strategy,
  TournamentLineup,
  TournamentLineupDetail,
} from '../types/tournament';

const STRATEGIES: Strategy[] = ['conservative', 'versatile', 'aggressive', 'defensive'];

export function TournamentPage() {
  const [lineups, setLineups] = useState<TournamentLineup[] | null>(null);
  const [patterns, setPatterns] = useState<LanePattern[] | null>(null);
  const [name, setName] = useState('');
  const [tournamentName, setTournamentName] = useState('');
  const [patternId, setPatternId] = useState('');
  const [strategy, setStrategy] = useState<Strategy>('versatile');
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
    fetchPatterns()
      .then(setPatterns)
      .catch((loadError) =>
        setError(loadError instanceof Error ? loadError.message : 'Failed to load patterns'),
      );
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
        tournament_name: tournamentName.trim() || undefined,
        pattern_id: patternId || undefined,
        strategy,
      });
      setName('');
      setTournamentName('');
      await loadLineups();
      setError(null);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : 'Failed to create lineup');
    } finally {
      setIsBusy(false);
    }
  };

  const onViewLineup = async (lineupId: string): Promise<void> => {
    try {
      setSelectedLineup(await fetchLineupDetail(lineupId));
      setRecommendations(null);
      setError(null);
    } catch (viewError) {
      setError(viewError instanceof Error ? viewError.message : 'Failed to load lineup');
    }
  };

  const onRecommend = async (lineupId: string): Promise<void> => {
    setIsBusy(true);
    try {
      const suggestions = await recommendLineup(lineupId);
      setRecommendations(suggestions);
      setSelectedLineup(await fetchLineupDetail(lineupId));
      setError(null);
    } catch (recommendError) {
      setError(
        recommendError instanceof Error ? recommendError.message : 'Failed to auto-fill lineup',
      );
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="hero">
          <p className="eyebrow">Tournament Bag</p>
          <h1>Lineups</h1>
          <p className="subtext">Build an optimized ball lineup for your next tournament.</p>
        </header>
        {error && <p role="alert">{error}</p>}
        <div className="stack">
          <div className="card">
            <h2>Create lineup</h2>
            <label htmlFor="lineupName">Name</label>
            <input
              id="lineupName"
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
            <label htmlFor="tournamentName">Tournament name</label>
            <input
              id="tournamentName"
              value={tournamentName}
              onChange={(event) => setTournamentName(event.target.value)}
            />
            <label htmlFor="patternSelect">Target pattern</label>
            <select
              id="patternSelect"
              value={patternId}
              onChange={(event) => setPatternId(event.target.value)}
            >
              <option value="">None</option>
              {patterns?.map((pattern) => (
                <option key={pattern.id} value={pattern.id}>
                  {pattern.name}
                </option>
              ))}
            </select>
            <label htmlFor="strategySelect">Strategy</label>
            <select
              id="strategySelect"
              value={strategy}
              onChange={(event) => setStrategy(event.target.value as Strategy)}
            >
              {STRATEGIES.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            <button type="button" onClick={onCreate} disabled={isBusy}>
              Create lineup
            </button>
          </div>

          {!lineups && <p>Loading lineups…</p>}
          {lineups?.length === 0 && <p className="subtext">No lineups yet. Create one above.</p>}
          {lineups?.map((lineup) => (
            <div className="card" key={lineup.id}>
              <p className="eyebrow">{lineup.strategy ?? 'no strategy'}</p>
              <h2>{lineup.name}</h2>
              <p className="subtext">{lineup.tournament_name}</p>
              <button type="button" onClick={() => onViewLineup(lineup.id)}>
                View lineup
              </button>
              <button type="button" onClick={() => onRecommend(lineup.id)} disabled={isBusy}>
                Auto-fill from arsenal
              </button>
            </div>
          ))}

          {selectedLineup && (
            <div className="card">
              <h2>{selectedLineup.name} — Bag</h2>
              <ul>
                {selectedLineup.balls.map((lineupBall) => (
                  <li key={lineupBall.id}>
                    <strong>{lineupBall.role}</strong>: {lineupBall.ball.brand}{' '}
                    {lineupBall.ball.name}
                  </li>
                ))}
                {selectedLineup.balls.length === 0 && (
                  <li>No balls assigned yet. Try auto-fill.</li>
                )}
              </ul>
            </div>
          )}

          {recommendations && (
            <div className="card">
              <h2>Suggested roles</h2>
              <ul>
                {recommendations.map((recommendation) => (
                  <li key={recommendation.user_arsenal_id}>
                    <strong>{recommendation.role}</strong>: {recommendation.ball.brand}{' '}
                    {recommendation.ball.name}
                    <p className="subtext">{recommendation.reasoning}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
