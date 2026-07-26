-- ============================================================
-- Bowling-HQ Seed Data
-- Inserts starter bowling balls, patterns, and one center.
-- ============================================================

-- ─── Bowling Centers ─────────────────────────────────────────
INSERT INTO bowling_centers (name, city, state, lanes_count, rating, notes) VALUES
    ('Maxwell AFB Lanes', 'Montgomery', 'AL', 24, 4.7, 'On-base bowling center. Consistent house shot.')
ON CONFLICT DO NOTHING;

-- ─── Lane Patterns ──────────────────────────────────────────
INSERT INTO lane_patterns (name, pattern_type, oil_volume, length_feet, difficulty_score, description) VALUES
    ('Standard House Shot',  'house',  'medium',     40, 3.0, 'Classic 40-foot house pattern with outside guide oil'),
    ('Sport Shot',           'sport',  'heavy',      43, 7.5, 'Flat sport pattern — minimal outside oil'),
    ('PBA Cheetah',          'pba',    'light',      33, 8.0, 'Short PBA pattern requiring precise targeting'),
    ('PBA Scorpion',         'pba',    'heavy',      45, 8.5, 'Long, heavy PBA pattern for strong equipment'),
    ('PBA Shark',            'pba',    'very_heavy', 48, 9.0, 'Longest PBA pattern, demands power game'),
    ('PBA Chameleon',        'pba',    'medium',     39, 7.0, 'Medium PBA pattern with tricky transition'),
    ('PBA Viper',            'pba',    'medium',     37, 8.0, 'Medium-short pattern, speed dominant')
ON CONFLICT DO NOTHING;

-- ─── Bowling Balls (Catalog) ─────────────────────────────────
INSERT INTO bowling_balls (brand, name, weight_oz, core_type, rg_min, differential, coverstock_type, finish, release_year, best_conditions, hook_potential, length_score, backend_score, notes) VALUES
    -- Storm
    ('Storm', 'Phaze II',       15, 'symmetrical',  2.48, 0.048, 'reactive', '500/2000 Abralon',      2019, 'dry',    8.5, 6.0, 7.5, 'Benchmark dry-to-medium ball'),
    ('Storm', 'IQ Tour',        15, 'symmetrical',  2.56, 0.039, 'reactive', '4000 Abralon',          2018, 'heavy',  6.5, 8.0, 6.0, 'Strong medium-heavy ball'),
    ('Storm', 'Phaze',          15, 'symmetrical',  2.52, 0.051, 'reactive', '500/2000 Abralon',      2016, 'medium', 7.0, 6.5, 7.0, 'Versatile mid-lane read'),
    ('Storm', 'Phaze III',      15, 'symmetrical',  2.48, 0.048, 'reactive', '500/2000/4000 Abralon', 2021, 'dry',    9.0, 5.5, 8.5, 'Strong backend, dry lanes'),
    ('Storm', 'Code Red',       15, 'asymmetrical', 2.47, 0.053, 'reactive', '500/2000 Abralon',      2022, 'heavy',  8.5, 7.0, 8.0, 'Asymmetric heavy-oil option'),
    ('Storm', 'Hy-Road',        15, 'symmetrical',  2.48, 0.050, 'reactive', '500/2000 Abralon',      2015, 'heavy',  8.0, 7.0, 7.5, 'Classic benchmark ball'),
    -- Brunswick
    ('Brunswick', 'Nirvana',    15, 'asymmetrical', 2.47, 0.054, 'reactive', '500/1000/2000 Abralon', 2022, 'heavy',  9.0, 6.5, 8.5, 'Aggressive heavy-oil asym'),
    ('Brunswick', 'Quantum',    15, 'symmetrical',  2.49, 0.046, 'reactive', '500/2000 Abralon',      2020, 'medium', 7.5, 7.0, 7.0, 'Smooth mid-lane benchmark'),
    -- Roto Grip
    ('Roto Grip', 'Hustle Ink', 15, 'symmetrical',  2.56, 0.038, 'reactive', '4000 Abralon',          2021, 'dry',    6.0, 8.5, 5.5, 'Long and angular dry ball'),
    ('Roto Grip', 'Gem',        15, 'symmetrical',  2.54, 0.040, 'reactive', '2000 Abralon',          2020, 'medium', 7.0, 7.5, 6.5, 'Clean through the front'),
    -- Hammer
    ('Hammer', 'Black Widow 3.0', 15, 'asymmetrical', 2.47, 0.058, 'reactive', '500/1000/2000 Abralon', 2021, 'heavy', 9.5, 6.0, 9.0, 'High flare asymmetric'),
    -- Motiv
    ('Motiv', 'Forge Fire',     15, 'asymmetrical', 2.49, 0.053, 'reactive', '4000 LSP',              2022, 'heavy',  9.0, 6.5, 8.5, 'Benchmark heavy-oil asym'),
    -- Plastic spare ball
    ('Storm', 'Mix',            15, 'pancake',      2.65, 0.000, 'plastic',  '2000 Abralon',          2020, 'all',    1.0, 9.5, 1.0, 'Spare ball — minimal hook')
ON CONFLICT DO NOTHING;
