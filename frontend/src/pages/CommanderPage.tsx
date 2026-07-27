import { useState } from 'react';

import { fetchCommanderRecommendation } from '../services/api';
import type {
  CommanderResponse,
  LaneCondition,
  ReleaseStyle,
} from '../types/commander';

const LANE_CONDITIONS: LaneCondition[] = ['dry', 'light', 'medium', 'heavy', 'very_heavy'];
const RELEASE_STYLES: ReleaseStyle[] = ['controlled', 'balanced', 'power'];

const ROLE_LABELS: Record<string, string> = {
  primary: 'Primary',
  alternative: 'Alternative',
  backup: 'Backup',
};

export function CommanderPage() {
  const [laneCondition, setLaneCondition] = useState<LaneCondition>('medium');
  const [patternDifficulty, setPatternDifficulty] = useState(2);
  const [ballSpeed, setBallSpeed] = useState(16);
  const [releaseStyle, setReleaseStyle] = useState<ReleaseStyle>('balanced');
  const [result, setResult] = useState<CommanderResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await fetchCommanderRecommendation({
        lane_condition: laneCondition,
        pattern_difficulty: patternDifficulty,
        ball_speed: ballSpeed,
        release_style: releaseStyle,
      });
      setResult(response);
      setError(null);
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : 'Failed to get recommendation',
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="hero">
          <p className="eyebrow">Commander AI</p>
          <h1>Ball Recommendation</h1>
          <p className="subtext">Tell us the lane conditions and we'll pick your best ball.</p>
        </header>
        {error && <p role="alert">{error}</p>}
        <div className="stack">
          <div className="card">
            <label htmlFor="laneCondition">Lane condition</label>
            <select
              id="laneCondition"
              value={laneCondition}
              onChange={(event) => setLaneCondition(event.target.value as LaneCondition)}
            >
              {LANE_CONDITIONS.map((condition) => (
                <option key={condition} value={condition}>
                  {condition.replace('_', ' ')}
                </option>
              ))}
            </select>

            <label htmlFor="patternDifficulty">Pattern difficulty (1-4)</label>
            <input
              id="patternDifficulty"
              type="number"
              min={1}
              max={4}
              value={patternDifficulty}
              onChange={(event) => setPatternDifficulty(Number(event.target.value))}
            />

            <label htmlFor="ballSpeed">Ball speed (mph)</label>
            <input
              id="ballSpeed"
              type="number"
              min={10}
              max={22}
              value={ballSpeed}
              onChange={(event) => setBallSpeed(Number(event.target.value))}
            />

            <label htmlFor="releaseStyle">Release style</label>
            <select
              id="releaseStyle"
              value={releaseStyle}
              onChange={(event) => setReleaseStyle(event.target.value as ReleaseStyle)}
            >
              {RELEASE_STYLES.map((style) => (
                <option key={style} value={style}>
                  {style}
                </option>
              ))}
            </select>

            <button type="button" onClick={onSubmit} disabled={isLoading}>
              Get recommendation
            </button>
          </div>

          {result && (
            <div className="stack">
              {!result.from_arsenal && (
                <p className="subtext">
                  Your arsenal is empty — showing the top matches from the catalog instead.
                </p>
              )}
              {result.recommendations.map((recommendation) => (
                <div
                  className="card"
                  key={`${recommendation.role}-${recommendation.arsenal_id ?? recommendation.ball.id}`}
                >
                  <p className="eyebrow">
                    {ROLE_LABELS[recommendation.role] ?? recommendation.role} · Confidence{' '}
                    {recommendation.confidence}%
                  </p>
                  <h2>
                    {recommendation.ball.brand} {recommendation.ball.name}
                  </h2>
                  <p className="subtext">{recommendation.reasoning}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
