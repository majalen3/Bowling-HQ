import { useCallback, useEffect, useMemo, useState } from 'react';

import {
  addToArsenal,
  fetchBallCatalog,
  fetchUserArsenal,
  removeFromArsenal,
} from '../services/api';
import type { ArsenalItem, BowlingBall } from '../types/arsenal';

type Tab = 'arsenal' | 'catalog';

const OIL_CONDITIONS = ['dry', 'light', 'medium', 'heavy', 'very_heavy', 'any'];
const COVERSTOCK_TYPES = ['plastic', 'urethane', 'reactive_resin', 'pearl_reactive'];

function BallCard({ ball, children }: { ball: BowlingBall; children?: React.ReactNode }) {
  return (
    <div className="card">
      <p className="eyebrow">{ball.brand}</p>
      <h2>{ball.name}</h2>
      <p className="subtext">{ball.description}</p>
      <ul>
        <li>Coverstock: {ball.coverstock_type.replace('_', ' ')}</li>
        <li>Core: {ball.core_type}</li>
        <li>Oil condition: {ball.oil_condition ?? 'n/a'}</li>
        <li>Hook potential: {ball.hook_potential ?? '—'}/10</li>
        <li>Length: {ball.length ?? '—'}/10</li>
        <li>Backend: {ball.backend ?? '—'}/10</li>
        <li>RG: {ball.rg ?? '—'} | Diff: {ball.differential ?? '—'}</li>
        <li>Weights: {ball.weight_options ?? '—'}</li>
      </ul>
      {children}
    </div>
  );
}

export function ArsenalPage() {
  const [tab, setTab] = useState<Tab>('arsenal');
  const [arsenal, setArsenal] = useState<ArsenalItem[] | null>(null);
  const [catalog, setCatalog] = useState<BowlingBall[] | null>(null);
  const [oilFilter, setOilFilter] = useState('');
  const [coverstockFilter, setCoverstockFilter] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isBusy, setIsBusy] = useState(false);

  const loadArsenal = async (): Promise<void> => {
    try {
      setArsenal(await fetchUserArsenal());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load arsenal');
    }
  };

  const loadCatalog = useCallback(async (): Promise<void> => {
    try {
      setCatalog(
        await fetchBallCatalog({
          oil_condition: oilFilter || undefined,
          coverstock_type: coverstockFilter || undefined,
        }),
      );
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load catalog');
    }
  }, [oilFilter, coverstockFilter]);

  useEffect(() => {
    loadArsenal();
  }, []);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const ownedBallIds = useMemo(
    () => new Set((arsenal ?? []).map((item) => item.ball_id)),
    [arsenal],
  );

  const onAdd = async (ballId: string): Promise<void> => {
    setIsBusy(true);
    try {
      await addToArsenal({ ball_id: ballId });
      await loadArsenal();
      setError(null);
    } catch (addError) {
      setError(addError instanceof Error ? addError.message : 'Failed to add ball');
    } finally {
      setIsBusy(false);
    }
  };

  const onRemove = async (userArsenalId: string): Promise<void> => {
    setIsBusy(true);
    try {
      await removeFromArsenal(userArsenalId);
      await loadArsenal();
      setError(null);
    } catch (removeError) {
      setError(removeError instanceof Error ? removeError.message : 'Failed to remove ball');
    } finally {
      setIsBusy(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="hero">
          <p className="eyebrow">Arsenal DNA</p>
          <h1>Ball Arsenal</h1>
          <p className="subtext">Browse the catalog and manage your personal arsenal.</p>
        </header>
        {error && <p role="alert">{error}</p>}
        <div className="stack">
          <div className="card">
            <button type="button" onClick={() => setTab('arsenal')} disabled={tab === 'arsenal'}>
              My Arsenal
            </button>
            <button type="button" onClick={() => setTab('catalog')} disabled={tab === 'catalog'}>
              Ball Catalog
            </button>
          </div>

          {tab === 'arsenal' && (
            <div className="stack">
              {!arsenal && <p>Loading arsenal…</p>}
              {arsenal && arsenal.length === 0 && (
                <p className="subtext">No balls in your arsenal yet. Add some from the catalog.</p>
              )}
              {arsenal?.map((item) => (
                <BallCard key={item.id} ball={item.ball}>
                  <p className="subtext">Layout: {item.layout ?? 'n/a'}</p>
                  <p className="subtext">Games played: {item.games_played}</p>
                  <button type="button" onClick={() => onRemove(item.id)} disabled={isBusy}>
                    Remove from arsenal
                  </button>
                </BallCard>
              ))}
            </div>
          )}

          {tab === 'catalog' && (
            <div className="stack">
              <div className="card">
                <label htmlFor="oilFilter">Oil condition</label>
                <select
                  id="oilFilter"
                  value={oilFilter}
                  onChange={(event) => setOilFilter(event.target.value)}
                >
                  <option value="">All</option>
                  {OIL_CONDITIONS.map((option) => (
                    <option key={option} value={option}>
                      {option.replace('_', ' ')}
                    </option>
                  ))}
                </select>
                <label htmlFor="coverstockFilter">Coverstock</label>
                <select
                  id="coverstockFilter"
                  value={coverstockFilter}
                  onChange={(event) => setCoverstockFilter(event.target.value)}
                >
                  <option value="">All</option>
                  {COVERSTOCK_TYPES.map((option) => (
                    <option key={option} value={option}>
                      {option.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </div>
              {!catalog && <p>Loading catalog…</p>}
              {catalog?.map((ball) => (
                <BallCard key={ball.id} ball={ball}>
                  {ownedBallIds.has(ball.id) ? (
                    <p className="subtext">Already in your arsenal</p>
                  ) : (
                    <button type="button" onClick={() => onAdd(ball.id)} disabled={isBusy}>
                      Add to arsenal
                    </button>
                  )}
                </BallCard>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
