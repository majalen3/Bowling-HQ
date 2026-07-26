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

export function ProgressPage() {
  const [progress, setProgress] = useState<ProgressSnapshot | null>(null);
  const [sessionProgress, setSessionProgress] = useState<SessionProgressSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionType, setSessionType] = useState('practice');
  const [locationName, setLocationName] = useState('');
  const [isSaving, setIsSaving] = useState(false);

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

  return (
    <main>
      <section>
        <p>Delivery control center</p>
        <h1>Bowling-HQ Progress</h1>
        {error && <p role="alert">{error}</p>}
        {!progress && !error && <p>Loading progress…</p>}
        {progress && groupedItems && (
          <>
            <p>{progress.finished_target}</p>
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
            {(Object.keys(BOARD_LABELS) as BoardStatus[]).map((status) => (
              <div key={status}>
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
              </div>
            ))}
          </>
        )}
      </section>
    </main>
  );
}
