import { useEffect, useState } from 'react';

import { fetchPatternDetail, fetchPatterns } from '../services/api';
import type { LanePattern, LanePatternDetail } from '../types/patterns';

export function PatternsPage() {
  const [patterns, setPatterns] = useState<LanePattern[] | null>(null);
  const [selected, setSelected] = useState<LanePatternDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async (): Promise<void> => {
      try {
        setPatterns(await fetchPatterns());
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : 'Failed to load patterns');
      }
    };
    load();
  }, []);

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
          {!patterns && <p>Loading patterns…</p>}
          {patterns?.map((pattern) => (
            <div className="card" key={pattern.id}>
              <h2>{pattern.name}</h2>
              <ul>
                <li>Length: {pattern.length_ft} ft</li>
                <li>Volume: {pattern.volume_ml} mL</li>
                <li>Asymmetry index: {pattern.asymmetry_index.toFixed(3)}</li>
                <li>
                  Oil distribution: {Math.round(pattern.front_oil_pct * 100)}% /&nbsp;
                  {Math.round(pattern.mid_oil_pct * 100)}% /&nbsp;
                  {Math.round(pattern.backend_oil_pct * 100)}%
                  (front / mid / back)
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
              <ul>
                {selected.recommended_balls.map((ball) => (
                  <li key={ball.id}>
                    <strong>
                      {ball.brand} {ball.name}
                    </strong>{' '}
                    — {ball.coverstock}, diff {ball.differential.toFixed(3)},
                    grit {ball.surface_grit}
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
