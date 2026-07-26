-- =============================================================================
-- Bowling-HQ Seed Data
-- Loaded automatically by PostgreSQL on first container startup.
-- =============================================================================

-- Default user (user_id=1, used throughout MVP)
INSERT INTO users (id, username, email, display_name, hand, ball_speed_avg, rev_rate_avg)
VALUES (1, 'bowler1', 'bowler@bowlinghq.local', 'Thomas', 'right', 16.5, 280)
ON CONFLICT (username) DO NOTHING;

-- Bowling Centers
INSERT INTO bowling_centers (id, name, location, number_of_lanes, notes) VALUES
(1, 'Maxwell AFB Bowling Center', 'Maxwell AFB, Montgomery, AL', 16, 'Primary home center. Well-maintained lanes with consistent oil application.'),
(2, 'Pointe North Bowling',       'Montgomery, AL',              24, 'Nearby commercial center used for tournaments and open bowling.')
ON CONFLICT DO NOTHING;

-- Lane Patterns
INSERT INTO patterns (id, name, pattern_type, oil_volume, oil_length_ft, difficulty, description, notes) VALUES
(1,  'House Shot',              'house',  'light',      40, 1, 'Standard recreational house shot. Light oil concentrated in the middle with dry outside edges. Very forgiving and easy to score on.',        'Most common league condition'),
(2,  'Maxwell AFB House',       'house',  'medium',     38, 2, 'Maxwell AFB bowling center standard house shot. Medium oil volume with slight taper. More challenging than a typical recreational house shot.', 'Home center pattern'),
(3,  'Maxwell AFB Tournament',  'sport',  'heavy',      36, 3, 'Maxwell AFB tournament-style pattern. Heavier oil volume with shorter length creates demanding conditions requiring precise ball selection.',   'Used for in-house tournaments'),
(4,  'PBA Chameleon',           'pba',    'medium',     39, 2, 'Classic PBA animal pattern. Medium oil volume with a relatively even distribution. Considered the most bowler-friendly PBA pattern.',          'Longest of the PBA animal patterns'),
(5,  'PBA Cheetah',             'pba',    'light',      33, 2, 'Short PBA animal pattern with light oil. The short length creates an early hook requiring urethane or polished reactive balls.',                'Shortest PBA animal pattern'),
(6,  'PBA Viper',               'pba',    'medium',     37, 3, 'Challenging PBA animal pattern with medium oil and a tight window. Requires consistent ball speed and accurate targeting.',                    'Narrow strike zone'),
(7,  'PBA Scorpion',            'pba',    'heavy',      42, 3, 'Long PBA animal pattern with heavy oil. Requires a strong backend ball that can handle the distance before hooking.',                          'Demands patience and strong ball'),
(8,  'PBA Shark',               'pba',    'very_heavy', 40, 4, 'The most demanding PBA animal pattern. Very heavy oil volume requires maximum hook potential and precision.',                                   'Hardest PBA animal'),
(9,  'Sport Shot',              'sport',  'heavy',      38, 3, 'USBC Sport shot challenge. Heavier and more uniform oil distribution than a house shot.',                                                      'Eliminates hooking boards advantage'),
(10, 'US Open',                 'pba',    'very_heavy', 41, 4, 'One of the most difficult patterns in bowling. Extremely heavy oil with a very tight window for error.',                                       'Toughest major in bowling')
ON CONFLICT DO NOTHING;

-- Arsenal (Bowling Balls)
INSERT INTO balls (id, name, brand, weight_lbs, coverstock_type, core_type, rg, differential, finish, layout, purpose, hook_potential, length_rating, backend_rating, is_spare_ball, notes) VALUES
(1,  'Phaze II',           'Storm',     15, 'reactive_resin', 'symmetrical',   2.480, 0.048, '1000_grit', '50x4x35',  'Dry to medium oil primary strike ball',          8, 6,  8, false, 'Benchmark ball for medium-dry conditions'),
(2,  'IQ Tour',            'Storm',     15, 'reactive_resin', 'symmetrical',   2.490, 0.040, '1000_grit', '60x4.5x40','Medium to heavy oil, versatile control ball',     7, 7,  6, false, 'Reliable on medium to heavier patterns'),
(3,  'Proton Physix',      'Storm',     15, 'pearl_reactive', 'asymmetrical',  2.480, 0.055, 'polished',  '50x5x30',  'Heavy oil, strong backend reaction',              10, 8, 10, false, 'Maximum energy storage for very heavy patterns'),
(4,  'Trend 2',            'Storm',     15, 'hybrid_reactive','symmetrical',   2.490, 0.041, '2000_grit', '55x4x40',  'Medium oil, smooth controllable motion',          7, 7,  7, false, 'Balanced hybrid for medium conditions'),
(5,  'Halo',               'Roto Grip', 15, 'pearl_reactive', 'asymmetrical',  2.470, 0.053, 'polished',  '45x5x35',  'Heavy to very heavy oil, tournament ball',        9, 8,  9, false, 'Strong angular backend on heavy patterns'),
(6,  'RST X-1',            'Roto Grip', 15, 'pearl_reactive', 'symmetrical',   2.520, 0.040, 'polished',  '55x4x45',  'Medium-dry to dry conditions, angular entry',     7, 8,  8, false, 'Pearl cover for longer skid on medium-dry'),
(7,  'Black Widow 2.0',    'Hammer',    15, 'reactive_resin', 'asymmetrical',  2.460, 0.052, '500_grit',  '45x4x30',  'Heavy oil, aggressive coverstock',                9, 5,  8, false, 'Early and strong on heavier patterns'),
(8,  'Gauntlet Fury',      'Hammer',    15, 'hybrid_reactive','asymmetrical',  2.470, 0.052, '1000_grit', '50x5x35',  'Medium-heavy oil with angular backend',           9, 6,  9, false, 'Strong hybrid for medium-heavy conditions'),
(9,  'Quantum Evo Pearl',  'Brunswick', 15, 'pearl_reactive', 'asymmetrical',  2.480, 0.054, 'polished',  '50x5x30',  'Very heavy oil, maximum hook',                   10, 8, 10, false, 'Tournament-level ball for the heaviest patterns'),
(10, 'Rhino',              'Brunswick', 15, 'reactive_resin', 'symmetrical',   2.560, 0.035, '2000_grit', '55x4x45',  'Entry-level, light to medium oil conditions',     5, 6,  5, false, 'Beginner-friendly, predictable motion'),
(11, 'Polar A-Bomb',       'Storm',     14, 'pearl_reactive', 'asymmetrical',  2.530, 0.040, 'polished',  '55x4x40',  'Medium conditions, control with backend',         7, 8,  7, false, '14lb option for adjusted ball speed'),
(12, 'Maxim',              'Ebonite',   14, 'plastic',        'symmetrical',   2.650, 0.011, 'polished',  'stock',     '10-pin and spare shooting',                       1, 10, 1, true,  'Dedicated spare ball — straight line'),
(13, 'Mix',                'Storm',     14, 'plastic',        'symmetrical',   2.650, 0.010, 'polished',  'stock',     'Spare shooting backup',                           1, 10, 1, true,  'Backup spare ball')
ON CONFLICT DO NOTHING;

-- Reset sequences to avoid conflicts with future inserts
SELECT setval('users_id_seq',           (SELECT MAX(id) FROM users));
SELECT setval('bowling_centers_id_seq', (SELECT MAX(id) FROM bowling_centers));
SELECT setval('patterns_id_seq',        (SELECT MAX(id) FROM patterns));
SELECT setval('balls_id_seq',           (SELECT MAX(id) FROM balls));
