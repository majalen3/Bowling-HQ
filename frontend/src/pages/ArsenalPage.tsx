import { useEffect, useState } from 'react';

import {
  addBallToArsenal,
  fetchArsenal,
  fetchBallCatalog,
  removeBallFromArsenal,
} from '../services/api';
import type {
  ArsenalResponse,
  BallItem,
  CreateAndAddBallRequest,
} from '../types/arsenal';

const EMPTY_FORM: CreateAndAddBallRequest = {
  name: '',
  brand: '',
  coverstock: 'solid reactive',
  rg: 2.5,
  differential: 0.04,
  mass_bias: 0.0,
  surface_grit: 3000,
  weight_lbs: 15,
  notes: '',
};

export function ArsenalPage() {
  const [arsenal, setArsenal] = useState<ArsenalResponse | null>(null);
  const [catalog, setCatalog] = useState<BallItem[]>([]);
  const [form, setForm] = useState<CreateAndAddBallRequest>(EMPTY_FORM);
  const [selectedCatalogId, setSelectedCatalogId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const loadArsenal = async (): Promise<void> => {
    try {
      const [arsenalData, catalogData] = await Promise.all([
        fetchArsenal(),
        fetchBallCatalog(),
      ]);
      setArsenal(arsenalData);
      setCatalog(catalogData);
      setError(null);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : 'Failed to load arsenal',
      );
    }
  };

  useEffect(() => {
    loadArsenal();
  }, []);

  const onSelectCatalog = (ballId: string): void => {
    setSelectedCatalogId(ballId);
    const ball = catalog.find((item) => item.id === ballId);
    if (ball) {
      setForm({
        name: ball.name,
        brand: ball.brand,
        coverstock: ball.coverstock,
        rg: ball.rg,
        differential: ball.differential,
        mass_bias: ball.mass_bias,
        surface_grit: ball.surface_grit,
        weight_lbs: ball.weight_lbs,
        notes: '',
      });
    }
  };

  const updateForm = (
    key: keyof CreateAndAddBallRequest,
    value: string,
  ): void => {
    const numericKeys: Array<keyof CreateAndAddBallRequest> = [
      'rg',
      'differential',
      'mass_bias',
      'surface_grit',
      'weight_lbs',
    ];
    setForm((prev) => ({
      ...prev,
      [key]: numericKeys.includes(key) ? Number(value) : value,
    }));
  };

  const onAddBall = async (): Promise<void> => {
    if (!form.name.trim() || !form.brand.trim()) {
      setError('Ball name and brand are required');
      return;
    }
    setBusy(true);
    try {
      await addBallToArsenal(form);
      setForm(EMPTY_FORM);
      setSelectedCatalogId('');
      await loadArsenal();
      setError(null);
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : 'Failed to add ball',
      );
    } finally {
      setBusy(false);
    }
  };

  const onRemove = async (arsenalId: string): Promise<void> => {
    setBusy(true);
    try {
      await removeBallFromArsenal(arsenalId);
      await loadArsenal();
    } catch (removeError) {
      setError(
        removeError instanceof Error
          ? removeError.message
          : 'Failed to remove ball',
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="stack">
      <header className="hero">
        <p className="eyebrow">Arsenal</p>
        <h1>Your Bowling Bag</h1>
        <p className="subtext">
          Manage the balls Commander AI can recommend from.
        </p>
      </header>

      {error && <p role="alert">{error}</p>}

      <section className="card">
        <h2>Add a Ball</h2>
        <div className="form-group">
          <label htmlFor="catalogSelect">Pick from catalog</label>
          <select
            id="catalogSelect"
            value={selectedCatalogId}
            onChange={(event) => onSelectCatalog(event.target.value)}
          >
            <option value="">— Manual entry —</option>
            {catalog.map((ball) => (
              <option key={ball.id} value={ball.id}>
                {ball.name} ({ball.coverstock})
              </option>
            ))}
          </select>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="ballName">Name</label>
            <input
              id="ballName"
              value={form.name}
              onChange={(event) => updateForm('name', event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="ballBrand">Brand</label>
            <input
              id="ballBrand"
              value={form.brand}
              onChange={(event) => updateForm('brand', event.target.value)}
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="ballCover">Coverstock</label>
          <select
            id="ballCover"
            value={form.coverstock}
            onChange={(event) => updateForm('coverstock', event.target.value)}
          >
            <option value="solid reactive">Solid reactive</option>
            <option value="hybrid reactive">Hybrid reactive</option>
            <option value="pearl reactive">Pearl reactive</option>
            <option value="urethane">Urethane</option>
            <option value="plastic">Plastic</option>
          </select>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="ballRg">RG</label>
            <input
              id="ballRg"
              type="number"
              step="0.01"
              value={form.rg}
              onChange={(event) => updateForm('rg', event.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="ballDiff">Differential</label>
            <input
              id="ballDiff"
              type="number"
              step="0.001"
              value={form.differential}
              onChange={(event) =>
                updateForm('differential', event.target.value)
              }
            />
          </div>
          <div className="form-group">
            <label htmlFor="ballGrit">Surface Grit</label>
            <input
              id="ballGrit"
              type="number"
              value={form.surface_grit}
              onChange={(event) =>
                updateForm('surface_grit', event.target.value)
              }
            />
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="ballNotes">Notes</label>
          <input
            id="ballNotes"
            value={form.notes ?? ''}
            onChange={(event) => updateForm('notes', event.target.value)}
          />
        </div>
        <button type="button" onClick={onAddBall} disabled={busy}>
          Add Ball
        </button>
      </section>

      <section className="card">
        <h2>My Balls ({arsenal?.count ?? 0})</h2>
        {arsenal && arsenal.balls.length === 0 && (
          <p className="subtext">No balls yet. Add one above.</p>
        )}
        {arsenal?.balls.map((entry) => (
          <article className="ball-card" key={entry.id}>
            <div className="ball-card-head">
              <strong>{entry.ball.name}</strong>
              <span className="subtext">{entry.ball.brand}</span>
            </div>
            <p className="subtext">
              {entry.ball.coverstock} · RG {entry.ball.rg} · Diff{' '}
              {entry.ball.differential} · {entry.ball.surface_grit} grit
            </p>
            {entry.notes && <p className="subtext">{entry.notes}</p>}
            <button
              type="button"
              onClick={() => onRemove(entry.id)}
              disabled={busy}
            >
              Remove
            </button>
          </article>
        ))}
      </section>
    </section>
  );
}
