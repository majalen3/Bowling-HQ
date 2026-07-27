import { useState } from 'react';

import {
  analyzePattern,
  getCommanderRecommendation,
  getOpeningBallRecommendation,
  runBallSimulator,
} from '../services/api';
import type { CommanderResponse } from '../types/commander';
import type {
  BowlerInput,
  PatternInput,
  RecommendationResponse,
} from '../types/recommendations';
import type { PatternAnalysisResponse } from '../types/patterns';
import type { SimulatorResponse } from '../types/simulator';

const RANK_LABELS: Record<number, string> = {
  1: 'gold',
  2: 'silver',
  3: 'bronze',
};

export function CommanderPage() {
  const [pattern, setPattern] = useState<PatternInput>({
    name: 'House Shot',
    length_ft: 40,
    volume_ml: 24,
    asymmetry_index: 0.0,
    front_oil_pct: 0.34,
    mid_oil_pct: 0.33,
    backend_oil_pct: 0.33,
    lane_surface: 'synthetic',
  });
  const [bowler, setBowler] = useState<BowlerInput>({
    average: 190,
    speed_mph: 17,
    rev_rate: 350,
    axis_rotation_deg: 45,
    axis_tilt_deg: 15,
    consistency: 0.75,
  });
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [patternResult, setPatternResult] = useState<PatternAnalysisResponse | null>(null);
  const [simulation, setSimulation] = useState<SimulatorResponse | null>(null);
  const [orchestration, setOrchestration] = useState<CommanderResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updatePattern = (key: keyof PatternInput, value: string): void => {
    setPattern((prev) => ({
      ...prev,
      [key]: key === 'name' || key === 'lane_surface' ? value : Number(value),
    }));
  };

  const updateBowler = (key: keyof BowlerInput, value: string): void => {
    setBowler((prev) => ({ ...prev, [key]: Number(value) }));
  };

  const onSubmit = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getOpeningBallRecommendation({
        pattern,
        bowler,
        top_n: 3,
      });
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

  const onAnalyzePattern = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      setPatternResult(await analyzePattern({ pattern }));
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Failed to analyze pattern',
      );
    } finally {
      setIsLoading(false);
    }
  };

  const onRunSimulation = async (): Promise<void> => {
    if (!result?.recommendations[0]) {
      setError('Get recommendations first to simulate the top ball.');
      return;
    }
    const topBall = result.recommendations[0];
    setIsLoading(true);
    setError(null);
    try {
      setSimulation(
        await runBallSimulator({
          pattern,
          bowler,
          ball: {
            name: topBall.ball_name,
            coverstock: 'solid reactive',
            rg: 2.5,
            differential: 0.045,
            mass_bias: 0,
            surface_grit: 3000,
          },
        }),
      );
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Failed to run simulator',
      );
    } finally {
      setIsLoading(false);
    }
  };

  const onOrchestrate = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      setOrchestration(
        await getCommanderRecommendation({
          pattern,
          bowler,
          top_n: 3,
        }),
      );
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Failed to run commander orchestration',
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="stack">
      <header className="hero">
        <p className="eyebrow">Commander AI</p>
        <h1>Opening Ball Advisor</h1>
        <p className="subtext">
          Physics-driven recommendations with Ghost Bowler and simulator signals.
        </p>
      </header>

      {error && <p role="alert">{error}</p>}

      <section className="card">
        <h2>Oil Pattern</h2>
        <div className="form-group">
          <label htmlFor="patternName">Pattern Name</label>
          <input
            id="patternName"
            value={pattern.name ?? ''}
            onChange={(event) => updatePattern('name', event.target.value)}
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="length">Length (ft)</label>
            <input
              id="length"
              type="number"
              value={pattern.length_ft}
              onChange={(event) => updatePattern('length_ft', event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="volume">Volume (mL)</label>
            <input
              id="volume"
              type="number"
              value={pattern.volume_ml}
              onChange={(event) => updatePattern('volume_ml', event.target.value)}
            />
          </div>
        </div>
      </section>

      <section className="card">
        <h2>Bowler Profile</h2>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="average">Average</label>
            <input
              id="average"
              type="number"
              value={bowler.average}
              onChange={(event) => updateBowler('average', event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="speed">Speed (mph)</label>
            <input
              id="speed"
              type="number"
              value={bowler.speed_mph}
              onChange={(event) => updateBowler('speed_mph', event.target.value)}
            />
          </div>
        </div>
        <button type="button" onClick={onSubmit} disabled={isLoading}>
          {isLoading ? 'Working…' : 'Get Recommendation'}
        </button>{' '}
        <button type="button" onClick={onAnalyzePattern} disabled={isLoading}>
          Analyze Pattern
        </button>{' '}
        <button type="button" onClick={onRunSimulation} disabled={isLoading}>
          Run Simulator
        </button>{' '}
        <button type="button" onClick={onOrchestrate} disabled={isLoading}>
          Run Commander Orchestration
        </button>
      </section>

      {patternResult && (
        <section className="card">
          <h2>Pattern Intelligence</h2>
          <p>
            Difficulty: <strong>{patternResult.difficulty_score}</strong> ({patternResult.difficulty_label})
          </p>
          <p>Breakpoint board: {patternResult.breakpoint_board}</p>
          <p>Transition risk: {patternResult.transition_risk}</p>
        </section>
      )}

      {simulation && (
        <section className="card">
          <h2>Ball Simulator</h2>
          <p>
            Predicted score: <strong>{simulation.predicted_score}</strong> ({simulation.confidence_low}-
            {simulation.confidence_high})
          </p>
          <p>Strike probability: {Math.round(simulation.strike_probability * 100)}%</p>
          <p>Confidence: {Math.round(simulation.confidence * 100)}%</p>
        </section>
      )}

      {orchestration && (
        <section className="card">
          <h2>Ghost Bowler</h2>
          <p>
            Baseline average: <strong>{orchestration.ghost_bowler.overall.average_score}</strong> (
            {orchestration.ghost_bowler.total_games} games)
          </p>
          <p>Commander confidence: {Math.round(orchestration.confidence * 100)}%</p>
          <ul>
            {orchestration.rationale.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </section>
      )}

      {result && (
        <section className="card">
          <h2>Recommendations</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-label">Pattern Difficulty</span>
              <span className="stat-value">{result.pattern_difficulty_score}</span>
              <span className="subtext">{result.pattern_difficulty_label}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Rule of 31 Breakpoint</span>
              <span className="stat-value">{result.breakpoint_board}</span>
              <span className="subtext">board</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Bowler Type</span>
              <span className="stat-value stat-type">{result.bowler_type.replace('_', ' ')}</span>
            </div>
          </div>

          {result.recommendations.map((rec) => (
            <article className="ball-card" key={rec.rank}>
              <div className="ball-card-head">
                <span className={`recommendation-rank rank-${RANK_LABELS[rec.rank] ?? 'other'}`}>
                  #{rec.rank}
                </span>
                <strong>{rec.ball_name}</strong>
              </div>
              <div className="fit-score-bar">
                <div className="fit-score-fill" style={{ width: `${rec.fit_score}%` }} />
              </div>
              <p className="subtext">
                Fit {rec.fit_score}/100 · Confidence {Math.round(rec.confidence * 100)}% · Strike{' '}
                {Math.round(rec.strike_probability * 100)}%
              </p>
              <ul>
                {rec.reasoning.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </article>
          ))}
        </section>
      )}
    </section>
  );
}
