import { useEffect, useMemo, useState } from 'react';

import { fetchProgressSnapshot } from '../services/api';
import type { BoardStatus, ProgressSnapshot } from '../types/progress';

const BOARD_LABELS: Record<BoardStatus, string> = {
  backlog: 'Backlog',
  in_progress: 'In Progress',
  done: 'Done',
};

export function ProgressPage() {
  const [progress, setProgress] = useState<ProgressSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    const load = async () => {
      try {
        const snapshot = await fetchProgressSnapshot();
        if (isActive) {
          setProgress(snapshot);
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
