import { useEffect, useState } from 'react';

import {
  addGameFromThrows,
  addGamesToSession,
  createSession,
  completeSession,
  fetchSessionGames,
  fetchSessionProgress,
  importScores,
} from '../services/api';
import type { FramesResponse, GamesResponse } from '../types/games';
import type { SessionProgressSnapshot } from '../types/sessionProgress';

export function SessionsPage() {
  const [snapshot, setSnapshot] = useState<SessionProgressSnapshot | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [sessionType, setSessionType] = useState('practice');
  const [locationName, setLocationName] = useState('');
  const [scoreInputs, setScoreInputs] = useState<Record<string, string>>({});
  const [throwInputs, setThrowInputs] = useState<Record<string, string>>({});
  const [entryMode, setEntryMode] = useState<Record<string, 'quick' | 'throws'>>({});
  const [gamesBySession, setGamesBySession] = useState<
    Record<string, GamesResponse>
  >({});
  const [framesByGame, setFramesByGame] = useState<
    Record<string, FramesResponse>
  >({});
  const [csvText, setCsvText] = useState<Record<string, string>>({});
  const [csvSource, setCsvSource] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  const loadGames = async (sessionId: string): Promise<void> => {
    try {
      const data = await fetchSessionGames(sessionId);
      setGamesBySession((prev) => ({ ...prev, [sessionId]: data }));
    } catch {
      // Games may not exist yet; ignore.
    }
  };

  const loadSnapshot = async (): Promise<void> => {
    try {
      const data = await fetchSessionProgress();
      setSnapshot(data);
      setError(null);
      // Auto-load games for every session when the snapshot refreshes.
      await Promise.all(data.sessions.map((s) => loadGames(s.id)));
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : 'Failed to load sessions',
      );
    }
  };

  useEffect(() => {
    loadSnapshot();
  }, []);

  const onStartSession = async (): Promise<void> => {
    if (!sessionType.trim()) {
      setError('Session type is required');
      return;
    }
    setBusy(true);
    try {
      await createSession({
        session_type: sessionType.trim(),
        location_name: locationName.trim() || undefined,
      });
      setLocationName('');
      await loadSnapshot();
      setError(null);
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Failed to start session',
      );
    } finally {
      setBusy(false);
    }
  };

  const onAddScores = async (sessionId: string): Promise<void> => {
    const raw = scoreInputs[sessionId] ?? '';
    const scores = raw
      .split(',')
      .map((token) => token.trim())
      .filter((token) => token.length > 0)
      .map((token) => Number(token));
    if (scores.length === 0 || scores.some((score) => Number.isNaN(score))) {
      setError('Enter comma-separated scores (0-300)');
      return;
    }
    if (scores.some((score) => score < 0 || score > 300)) {
      setError('Scores must be between 0 and 300');
      return;
    }
    setBusy(true);
    try {
      const response = await addGamesToSession(sessionId, scores);
      setGamesBySession((prev) => ({ ...prev, [sessionId]: response }));
      setScoreInputs((prev) => ({ ...prev, [sessionId]: '' }));
      setError(null);
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Failed to add scores',
      );
    } finally {
      setBusy(false);
    }
  };

  const onAddFromThrows = async (sessionId: string): Promise<void> => {
    const raw = throwInputs[sessionId] ?? '';
    const throws = raw
      .split(/[\s,]+/)
      .filter((t) => t.length > 0)
      .map((t) => Number(t));
    if (
      throws.length < 12 ||
      throws.length > 21 ||
      throws.some((t) => Number.isNaN(t) || t < 0 || t > 10)
    ) {
      setError(
        'Enter 12–21 throw values (0-10 each), space or comma separated. ' +
          'Example: 10 10 10 10 10 10 10 10 10 10 10 10 (perfect game)',
      );
      return;
    }
    setBusy(true);
    try {
      const framesResp = await addGameFromThrows(sessionId, throws);
      setFramesByGame((prev) => ({
        ...prev,
        [framesResp.game_id]: framesResp,
      }));
      setThrowInputs((prev) => ({ ...prev, [sessionId]: '' }));
      await loadGames(sessionId);
      setError(null);
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Failed to add game from throws',
      );
    } finally {
      setBusy(false);
    }
  };

  const onImport = async (sessionId: string): Promise<void> => {
    const text = csvText[sessionId] ?? '';
    if (!text.trim()) {
      setError('Paste CSV data to import');
      return;
    }
    setBusy(true);
    try {
      await importScores(
        sessionId,
        text,
        csvSource[sessionId] ?? 'generic',
      );
      setCsvText((prev) => ({ ...prev, [sessionId]: '' }));
      await loadGames(sessionId);
      setError(null);
    } catch (importError) {
      setError(
        importError instanceof Error
          ? importError.message
          : 'Failed to import scores',
      );
    } finally {
      setBusy(false);
    }
  };

  const onComplete = async (sessionId: string): Promise<void> => {
    setBusy(true);
    try {
      await completeSession(sessionId);
      await loadSnapshot();
    } catch (completeError) {
      setError(
        completeError instanceof Error
          ? completeError.message
          : 'Failed to complete session',
      );
    } finally {
      setBusy(false);
    }
  };

  const getMode = (sessionId: string): 'quick' | 'throws' =>
    entryMode[sessionId] ?? 'quick';

  return (
    <section className="stack">
      <header className="hero">
        <p className="eyebrow">Sessions</p>
        <h1>Practice &amp; League Sessions</h1>
        <p className="subtext">
          Track games, enter scores, and import from LaneTrax or LaneTalk.
        </p>
      </header>

      {error && <p role="alert">{error}</p>}

      <section className="card">
        <h2>Start a Session</h2>
        <div className="form-group">
          <label htmlFor="sessionType">Session Type</label>
          <input
            id="sessionType"
            value={sessionType}
            onChange={(event) => setSessionType(event.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="locationName">Location</label>
          <input
            id="locationName"
            value={locationName}
            onChange={(event) => setLocationName(event.target.value)}
          />
        </div>
        <button type="button" onClick={onStartSession} disabled={busy}>
          Start session
        </button>
      </section>

      {snapshot?.sessions.map((session) => {
        const games = gamesBySession[session.id];
        const mode = getMode(session.id);
        return (
          <section className="card" key={session.id}>
            <div className="ball-card-head">
              <strong>{session.session_type}</strong>
              <span className="subtext">
                {session.completed_at ? 'Completed' : 'Active'}
              </span>
            </div>
            {session.location_name && (
              <p className="subtext">@ {session.location_name}</p>
            )}

            {games && games.count > 0 && (
              <div>
                <p className="subtext">
                  {games.count} games · average {games.average}
                </p>
                <ul>
                  {games.games.map((game) => {
                    const frames = framesByGame[game.id];
                    return (
                      <li key={game.id}>
                        Game {game.game_number}: {game.score}
                        {frames && frames.frames.length > 0 && (
                          <span className="subtext">
                            {' '}
                            (
                            {frames.frames
                              .map((f) =>
                                f.is_strike
                                  ? 'X'
                                  : f.is_spare
                                    ? `${f.ball1}/`
                                    : `${f.ball1}-${f.ball2 ?? 0}`,
                              )
                              .join(' ')}
                            )
                          </span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}

            {!session.completed_at && (
              <>
                <div className="form-group">
                  <label>Score entry mode</label>
                  <div>
                    <button
                      type="button"
                      onClick={() =>
                        setEntryMode((prev) => ({
                          ...prev,
                          [session.id]: 'quick',
                        }))
                      }
                      disabled={mode === 'quick'}
                    >
                      Quick score
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        setEntryMode((prev) => ({
                          ...prev,
                          [session.id]: 'throws',
                        }))
                      }
                      disabled={mode === 'throws'}
                    >
                      Frame-by-frame throws
                    </button>
                  </div>
                </div>

                {mode === 'quick' && (
                  <>
                    <div className="form-group">
                      <label htmlFor={`scores-${session.id}`}>
                        Game scores (comma separated, up to 5)
                      </label>
                      <input
                        id={`scores-${session.id}`}
                        placeholder="180, 200, 215"
                        value={scoreInputs[session.id] ?? ''}
                        onChange={(event) =>
                          setScoreInputs((prev) => ({
                            ...prev,
                            [session.id]: event.target.value,
                          }))
                        }
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => onAddScores(session.id)}
                      disabled={busy}
                    >
                      Add Scores
                    </button>
                  </>
                )}

                {mode === 'throws' && (
                  <>
                    <div className="form-group">
                      <label htmlFor={`throws-${session.id}`}>
                        Throws (12–21 values 0-10, space or comma separated)
                      </label>
                      <input
                        id={`throws-${session.id}`}
                        placeholder="10 10 10 10 10 10 10 10 10 10 10 10"
                        value={throwInputs[session.id] ?? ''}
                        onChange={(event) =>
                          setThrowInputs((prev) => ({
                            ...prev,
                            [session.id]: event.target.value,
                          }))
                        }
                      />
                    </div>
                    <button
                      type="button"
                      onClick={() => onAddFromThrows(session.id)}
                      disabled={busy}
                    >
                      Add Game from Throws
                    </button>
                  </>
                )}

                <div className="form-group">
                  <label htmlFor={`csv-${session.id}`}>
                    Import from LaneTrax / LaneTalk
                  </label>
                  <textarea
                    id={`csv-${session.id}`}
                    rows={4}
                    placeholder="Paste CSV export here"
                    value={csvText[session.id] ?? ''}
                    onChange={(event) =>
                      setCsvText((prev) => ({
                        ...prev,
                        [session.id]: event.target.value,
                      }))
                    }
                  />
                </div>
                <div className="form-group">
                  <label htmlFor={`source-${session.id}`}>Source</label>
                  <select
                    id={`source-${session.id}`}
                    value={csvSource[session.id] ?? 'generic'}
                    onChange={(event) =>
                      setCsvSource((prev) => ({
                        ...prev,
                        [session.id]: event.target.value,
                      }))
                    }
                  >
                    <option value="generic">Generic</option>
                    <option value="lanetrak">LaneTrax</option>
                    <option value="lanetalk">LaneTalk</option>
                  </select>
                </div>
                <button
                  type="button"
                  onClick={() => onImport(session.id)}
                  disabled={busy}
                >
                  Import
                </button>

                <button
                  type="button"
                  onClick={() => onComplete(session.id)}
                  disabled={busy}
                >
                  Mark complete
                </button>
              </>
            )}
          </section>
        );
      })}
    </section>
  );
}
