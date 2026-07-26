import { useEffect, useMemo, useState } from 'react';

import {
  completeSession,
  createSession,
  fetchProgressSnapshot,
  fetchSessionProgress,
} from '../services/api';
import type { BoardStatus, ProgressSnapshot } from '../types/progress';
import type { SessionProgressSnapshot } from '../types/sessionProgress';

const BOARD_LABELS: Record<BoardStatus, string> = {
  backlog: 'Backlog',
  in_progress: 'In Progress',
  done: 'Done',
};

type LaneCondition = 'dry' | 'medium' | 'heavy';
type ReleaseStyle = 'controlled' | 'balanced' | 'power';

type ArsenalBall = {
  id: string;
  name: string;
  laneStrength: LaneCondition;
  releaseStyle: ReleaseStyle;
  speedRange: [number, number];
  notes: string;
};

const ARSENAL_BALLS: ArsenalBall[] = [
  {
    id: 'phaze-ii',
    name: 'Storm Phaze II',
    laneStrength: 'dry',
    releaseStyle: 'controlled',
    speedRange: [14, 17],
    notes: 'Smooth read and reliable continuation for lighter friction.',
  },
  {
    id: 'iq-tour',
    name: 'Storm IQ Tour',
    laneStrength: 'medium',
    releaseStyle: 'balanced',
    speedRange: [14, 18],
    notes: 'Benchmark look for blended house conditions.',
  },
  {
    id: 'zen-gold-label',
    name: '900 Global Zen Gold Label',
    laneStrength: 'heavy',
    releaseStyle: 'power',
    speedRange: [15, 19],
    notes: 'Stronger move for fresh or tighter volumes.',
  },
];

export function ProgressPage() {
  const [progress, setProgress] = useState<ProgressSnapshot | null>(null);
  const [sessionProgress, setSessionProgress] = useState<SessionProgressSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionType, setSessionType] = useState('practice');
  const [locationName, setLocationName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [laneCondition, setLaneCondition] = useState<LaneCondition>('medium');
  const [releaseStyle, setReleaseStyle] = useState<ReleaseStyle>('balanced');
  const [ballSpeed, setBallSpeed] = useState(16);
  const [selectedBallId, setSelectedBallId] = useState(ARSENAL_BALLS[1].id);

  useEffect(() => {
    let isActive = true;

    const load = async (): Promise<void> => {
      try {
        const [snapshot, sessionsSnapshot] = await Promise.all([
          fetchProgressSnapshot(),
          fetchSessionProgress(),
        ]);
        if (isActive) {
          setProgress(snapshot);
          setSessionProgress(sessionsSnapshot);
          setError(null);
        }
      } catch (loadError) {
        if (isActive) {
          setError(loadError instanceof Error ? loadError.message : 'Failed to load progress');
        }
      }
    };

    load();

    return () => {
      isActive = false;
    };
  }, []);

  const refreshSnapshots = async (): Promise<void> => {
    const [snapshot, sessionsSnapshot] = await Promise.all([
      fetchProgressSnapshot(),
      fetchSessionProgress(),
    ]);
    setProgress(snapshot);
    setSessionProgress(sessionsSnapshot);
  };

  const onStartSession = async (): Promise<void> => {
    if (!sessionType.trim()) {
      setError('Session type is required');
      return;
    }
    setIsSaving(true);
    try {
      await createSession({
        session_type: sessionType.trim(),
        location_name: locationName.trim() || undefined,
      });
      setLocationName('');
      await refreshSnapshots();
      setError(null);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to start session');
    } finally {
      setIsSaving(false);
    }
  };

  const onCompleteSession = async (sessionId: string): Promise<void> => {
    setIsSaving(true);
    try {
      await completeSession(sessionId);
      await refreshSnapshots();
      setError(null);
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Failed to complete session',
      );
    } finally {
      setIsSaving(false);
    }
  };

  const groupedItems = useMemo(() => {
    if (!progress) {
      return null;
    }

    return {
      backlog: progress.board.filter((item) => item.status === 'backlog'),
      in_progress: progress.board.filter((item) => item.status === 'in_progress'),
      done: progress.board.filter((item) => item.status === 'done'),
    };
  }, [progress]);

  const selectedBall = useMemo(
    () => ARSENAL_BALLS.find((ball) => ball.id === selectedBallId) ?? ARSENAL_BALLS[0],
    [selectedBallId],
  );

  const arsenalRecommendation = useMemo(() => {
    let fitScore = 60;

    fitScore += selectedBall.laneStrength === laneCondition ? 25 : -15;
    fitScore += selectedBall.releaseStyle === releaseStyle ? 10 : -5;
    fitScore +=
      ballSpeed >= selectedBall.speedRange[0] && ballSpeed <= selectedBall.speedRange[1]
        ? 10
        : -10;

    const boundedScore = Math.max(1, Math.min(99, fitScore));
    const recommendation =
      boundedScore >= 80
        ? 'Go-to option for this look.'
        : boundedScore >= 60
          ? 'Playable choice with minor adjustments.'
          : 'Consider switching balls for stronger shape match.';

    return {
      score: boundedScore,
      recommendation,
    };
  }, [ballSpeed, laneCondition, releaseStyle, selectedBall]);

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="hero">
          <p className="eyebrow">iPhone simulator</p>
          <h1>Bowling-HQ Progress</h1>
          <p className="subtext">Delivery control center and arsenal workflow.</p>
        </header>
        {error && <p role="alert">{error}</p>}
        {!progress && !error && <p>Loading progress…</p>}
        {progress && groupedItems && (
          <div className="stack">
            <section className="card">
              <p className="subtext">{progress.finished_target}</p>
              <h2>MVP Scope Lock</h2>
              <ul>
                {progress.scope_lock.map((scopeItem) => (
                  <li key={scopeItem}>{scopeItem}</li>
                ))}
              </ul>
              <h2>Release Gates</h2>
              <ul>
                {progress.release_gate.map((gate) => (
                  <li key={gate}>{gate}</li>
                ))}
              </ul>
            </section>

            <section className="card">
              <h2>Slice 1: Session Progress Workflow</h2>
              <p>
                Sessions: {sessionProgress?.total_sessions ?? 0} total /{' '}
                {sessionProgress?.completed_sessions ?? 0} completed /{' '}
                {sessionProgress?.active_sessions ?? 0} active
              </p>
              <label htmlFor="sessionType">Session Type</label>
              <input
                id="sessionType"
                value={sessionType}
                onChange={(event) => setSessionType(event.target.value)}
              />
              <label htmlFor="locationName">Location</label>
              <input
                id="locationName"
                value={locationName}
                onChange={(event) => setLocationName(event.target.value)}
              />
              <button type="button" onClick={onStartSession} disabled={isSaving}>
                Start session
              </button>
              <ul>
                {sessionProgress?.sessions.map((session) => (
                  <li key={session.id}>
                    <strong>{session.session_type}</strong>
                    {session.location_name ? ` @ ${session.location_name}` : ''}
                    {session.completed_at ? (
                      ' (completed)'
                    ) : (
                      <button
                        type="button"
                        onClick={() => onCompleteSession(session.id)}
                        disabled={isSaving}
                      >
                        Mark complete
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            </section>

            <section className="card">
              <h2>Arsenal Simulator</h2>
              <label htmlFor="laneCondition">Lane Condition</label>
              <select
                id="laneCondition"
                value={laneCondition}
                onChange={(event) => setLaneCondition(event.target.value as LaneCondition)}
              >
                <option value="dry">Dry</option>
                <option value="medium">Medium</option>
                <option value="heavy">Heavy</option>
              </select>
              <label htmlFor="releaseStyle">Release Style</label>
              <select
                id="releaseStyle"
                value={releaseStyle}
                onChange={(event) => setReleaseStyle(event.target.value as ReleaseStyle)}
              >
                <option value="controlled">Controlled</option>
                <option value="balanced">Balanced</option>
                <option value="power">Power</option>
              </select>
              <label htmlFor="ballSpeed">Ball Speed (mph)</label>
              <input
                id="ballSpeed"
                type="number"
                min={10}
                max={22}
                value={ballSpeed}
                onChange={(event) => setBallSpeed(Number(event.target.value))}
              />
              <label htmlFor="ballSelect">Ball</label>
              <select
                id="ballSelect"
                value={selectedBallId}
                onChange={(event) => setSelectedBallId(event.target.value)}
              >
                {ARSENAL_BALLS.map((ball) => (
                  <option key={ball.id} value={ball.id}>
                    {ball.name}
                  </option>
                ))}
              </select>
              <p>
                <strong>Fit Score:</strong> {arsenalRecommendation.score}/100
              </p>
              <p>{arsenalRecommendation.recommendation}</p>
              <p className="subtext">{selectedBall.notes}</p>
            </section>

            {(Object.keys(BOARD_LABELS) as BoardStatus[]).map((status) => (
              <section className="card" key={status}>
                <h2>{BOARD_LABELS[status]}</h2>
                <ul>
                  {groupedItems[status].map((item) => (
                    <li key={item.id}>
                      <strong>
                        {item.id}: {item.title}
                      </strong>
                      <ul>
                        {item.done_criteria.map((criterion) => (
                          <li key={criterion}>{criterion}</li>
                        ))}
                      </ul>
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
