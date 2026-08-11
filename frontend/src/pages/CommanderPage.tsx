import { useState } from 'react';

import { fetchCommanderRecommendation } from '../services/api';
import type {
  CommanderRequestInput,
  CommanderResponse,
  LaneCondition,
  ReleaseStyle,
} from '../types/commander';

const ROLE_LABEL: Record<string, string> = {
  primary: 'Primary',
  alternative: 'Alternative',
  backup: 'Backup',
};

const ROLE_CLASS: Record<string, string> = {
  primary: 'rank-gold',
  alternative: 'rank-silver',
  backup: 'rank-bronze',
};

const DIFFICULTY_LABELS: Record<number, string> = {
  1: 'Easy (house shot)',
  2: 'Medium',
  3: 'Hard (sport)',
  4: 'Very hard (PBA)',
};

export function CommanderPage() {
  const [form, setForm] = useState<CommanderRequestInput>({
    lane_condition: 'medium',
    pattern_difficulty: 2,
    ball_speed: 17,
    release_style: 'balanced',
  });
  const [result, setResult] = useState<CommanderResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetchCommanderRecommendation(form);
      setResult(response);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Failed to get recommendation',
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="stack">
      <header className="hero">
        <p className="eyebrow">Auto Director</p>
        <h1>Commander AI</h1>
        <p className="subtext">
          Tell Commander what you're facing and it picks the right ball from
          your arsenal.
        </p>
      </header>

      {error && <p role="alert">{error}</p>}

      <section className="card">
        <h2>Lane Conditions</h2>

        <div className="form-group">
          <label htmlFor="laneCondition">Oil Condition</label>
          <select
            id="laneCondition"
            value={form.lane_condition}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                lane_condition: event.target.value as LaneCondition,
              }))
            }
          >
            <option value="dry">Dry</option>
            <option value="light">Light</option>
            <option value="medium">Medium</option>
            <option value="heavy">Heavy</option>
            <option value="very_heavy">Very Heavy</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="difficulty">
            Pattern Difficulty —{' '}
            <span className="subtext">
              {DIFFICULTY_LABELS[form.pattern_difficulty]}
            </span>
          </label>
          <input
            id="difficulty"
            type="range"
            min={1}
            max={4}
            step={1}
            value={form.pattern_difficulty}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                pattern_difficulty: Number(event.target.value),
              }))
            }
            className="range-input"
          />
          <div className="range-ticks">
            {[1, 2, 3, 4].map((n) => (
              <span
                key={n}
                className={
                  form.pattern_difficulty === n
                    ? 'range-tick range-tick-active'
                    : 'range-tick'
                }
              >
                {n}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="card">
        <h2>Your Game</h2>

        <div className="form-group">
          <label htmlFor="ballSpeed">Ball Speed (mph)</label>
          <input
            id="ballSpeed"
            type="number"
            min={10}
            max={25}
            step={0.5}
            value={form.ball_speed}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                ball_speed: Number(event.target.value),
              }))
            }
          />
        </div>

        <div className="form-group">
          <label htmlFor="releaseStyle">Release Style</label>
          <select
            id="releaseStyle"
            value={form.release_style}
            onChange={(event) =>
              setForm((prev) => ({
                ...prev,
                release_style: event.target.value as ReleaseStyle,
              }))
            }
          >
            <option value="controlled">Controlled (straighter)</option>
            <option value="balanced">Balanced (medium hook)</option>
            <option value="power">Power (strong hook)</option>
          </select>
        </div>

        <button type="button" onClick={onSubmit} disabled={isLoading}>
          {isLoading ? 'Analyzing…' : '⚡ Get Ball Recommendation'}
        </button>
      </section>

      {result && (
        <section className="card">
          <h2>
            Recommendations{' '}
            <span className="subtext">
              {result.from_arsenal ? 'from your arsenal' : 'from catalog'}
            </span>
          </h2>

          {result.recommendations.length === 0 && (
            <p className="subtext">
              No recommendations returned. Add balls to your arsenal and try
              again.
            </p>
          )}

          {result.recommendations.map((rec) => (
            <article className="ball-card" key={rec.role}>
              <div className="ball-card-head">
                <span
                  className={`recommendation-rank ${ROLE_CLASS[rec.role] ?? 'rank-other'}`}
                >
                  {ROLE_LABEL[rec.role] ?? rec.role}
                </span>
                <strong>{rec.ball.name}</strong>
              </div>
              <p className="subtext">{rec.ball.brand} · {rec.ball.coverstock}</p>
              <div className="fit-score-bar">
                <div
                  className="fit-score-fill"
                  style={{ width: `${rec.confidence}%` }}
                />
              </div>
              <p className="subtext">Confidence {rec.confidence}/100</p>
              <p className="subtext">{rec.reasoning}</p>
            </article>
          ))}

          {!result.from_arsenal && (
            <p className="subtext" style={{ marginTop: '0.5rem' }}>
              💡 Add your own balls in Arsenal to get recommendations from your
              bag.
            </p>
          )}
        </section>
      )}
    </section>
  );
}
