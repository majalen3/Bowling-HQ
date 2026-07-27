import { useEffect, useState } from 'react';

import { fetchPatternDetail, fetchPatterns } from '../services/api';
import type { LanePattern, LanePatternDetail } from '../types/patterns';

const PATTERN_TYPES = ['house', 'sport', 'challenge', 'pba'];
const DIFFICULTY_LABELS: Record<number, string> = {
  1: 'Easy',
  2: 'Moderate',
  3: 'Hard',
  4: 'Ultra',
};

export function PatternsPage() {
  const [patterns, setPatterns] = useState<LanePattern[] | null>(null);
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selected, setSelected] = useState<LanePatternDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async (): Promise<void> => {
      try {
        setPatterns(
          await fetchPatterns({
            difficulty: difficultyFilter ? Number(difficultyFilter) : undefined,
            pattern_type: typeFilter || undefined,
          }),
        );
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load patterns');
      }
    };
    load();
  }, [difficultyFilter, typeFilter]);

  const onSelect = async (patternId: string): Promise<void> => {
    try {
      setSelected(await fetchPatternDetail(patternId));
      setError(null);
    } catch (selectError) {
      setError(selectError instanceof Error ? selectError.message : 'Failed to load pattern');
    }
  };

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="hero">
          <p className="eyebrow">Pattern Intelligence</p>
          <h1>Lane Patterns</h1>
          <p className="subtext">Browse the pattern library and study recommended balls.</p>
        </header>
        {error && <p role="alert">{error}</p>}
        <div className="stack">
          <div className="card">
            <label htmlFor="difficultyFilter">Difficulty</label>
            <select
              id="difficultyFilter"
              value={difficultyFilter}
              onChange={(event) => setDifficultyFilter(event.target.value)}
            >
              <option value="">All</option>
              {[1, 2, 3, 4].map((level) => (
                <option key={level} value={level}>
                  {level} - {DIFFICULTY_LABELS[level]}
                </option>
              ))}
            </select>
            <label htmlFor="typeFilter">Pattern type</label>
            <select
              id="typeFilter"
              value={typeFilter}
              onChange={(event) => setTypeFilter(event.target.value)}
            >
              <option value="">All</option>
              {PATTERN_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          {!patterns && <p>Loading patterns…</p>}
          {patterns?.map((pattern) => (
            <div className="card" key={pattern.id}>
              <p className="eyebrow">
                {pattern.pattern_type} · Difficulty {pattern.difficulty}/4 ·{' '}
                {DIFFICULTY_LABELS[pattern.difficulty ?? 1]}
              </p>
              <h2>{pattern.name}</h2>
              <p className="subtext">{pattern.description}</p>
              <ul>
                <li>Oil volume: {pattern.oil_volume ?? '—'} mL</li>
                <li>Oil distance: {pattern.oil_distance ?? '—'} ft</li>
                <li>Recommended coverstock: {pattern.recommended_coverstock ?? '—'}</li>
                <li>
                  Recommended hook: {pattern.recommended_hook_min ?? '—'}-
                  {pattern.recommended_hook_max ?? '—'}
                </li>
              </ul>
              <button type="button" onClick={() => onSelect(pattern.id)}>
                View recommended balls
              </button>
            </div>
          ))}

          {selected && (
            <div className="card">
              <h2>Recommended balls for {selected.name}</h2>
              <p className="subtext">{selected.notes}</p>
              <ul>
                {selected.recommended_balls.map((ball) => (
                  <li key={ball.id}>
                    <strong>
                      {ball.brand} {ball.name}
                    </strong>{' '}
                    — {ball.coverstock_type.replace('_', ' ')}, hook {ball.hook_potential}/10
                  </li>
                ))}
                {selected.recommended_balls.length === 0 && <li>No exact matches found.</li>}
              </ul>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
