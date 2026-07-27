-- Idempotent seed data for Bowling-HQ.
-- Safe to run multiple times: all statements use ON CONFLICT DO NOTHING.

-- Default demo user (no auth system yet; every service uses this fixed id).
INSERT INTO users (id, email, display_name)
VALUES ('00000000-0000-0000-0000-000000000001', 'demo@bowling-hq.local', 'Demo User')
ON CONFLICT (id) DO NOTHING;

-- Arsenal DNA: bowling ball catalog.
INSERT INTO bowling_balls (
    id, brand, name, coverstock_type, core_type, rg, differential,
    hook_potential, length, backend, oil_condition, weight_options, description
) VALUES
    (
        '10000000-0000-0000-0000-000000000001', 'Storm', 'Phaze II', 'reactive_resin',
        'symmetrical', 2.51, 0.051, 7, 6, 7, 'light',
        '12,13,14,15,16', 'Smooth, controllable motion suited to dry to light oil.'
    ),
    (
        '10000000-0000-0000-0000-000000000002', 'Storm', 'IQ Tour', 'reactive_resin',
        'symmetrical', 2.49, 0.048, 7, 6, 6, 'medium',
        '12,13,14,15,16', 'Benchmark performer for blended house conditions.'
    ),
    (
        '10000000-0000-0000-0000-000000000003', 'Storm', 'Phaze III', 'reactive_resin',
        'symmetrical', 2.50, 0.050, 7, 6, 7, 'medium',
        '12,13,14,15,16', 'Balanced continuation through medium volumes.'
    ),
    (
        '10000000-0000-0000-0000-000000000004', '900 Global', 'Zen Gold Label', 'reactive_resin',
        'asymmetrical', 2.44, 0.056, 9, 4, 9, 'heavy',
        '14,15,16', 'Strong asymmetric move built for heavier oil volumes.'
    ),
    (
        '10000000-0000-0000-0000-000000000005', 'Hammer', 'Black Widow', 'reactive_resin',
        'asymmetrical', 2.53, 0.054, 8, 7, 8, 'light',
        '12,13,14,15,16', 'Aggressive backend with a legendary name, best on lighter oil.'
    ),
    (
        '10000000-0000-0000-0000-000000000006', 'Roto Grip', 'Halo', 'pearl_reactive',
        'asymmetrical', 2.46, 0.055, 9, 5, 9, 'heavy',
        '14,15,16', 'High-revving pearl asymmetric for heavier, thicker patterns.'
    ),
    (
        '10000000-0000-0000-0000-000000000007', 'Brunswick', 'Rhino', 'reactive_resin',
        'symmetrical', 2.54, 0.036, 5, 7, 5, 'medium',
        '10,12,13,14,15,16', 'Entry-level symmetric workhorse for medium house shots.'
    ),
    (
        '10000000-0000-0000-0000-000000000008', 'Motiv', 'Venom Shock', 'pearl_reactive',
        'symmetrical', 2.49, 0.045, 7, 6, 7, 'medium',
        '12,13,14,15,16', 'Skid/flip pearl reaction for medium conditions.'
    ),
    (
        '10000000-0000-0000-0000-000000000009', 'Ebonite', 'Maxim', 'plastic',
        'symmetrical', 2.70, 0.020, 1, 9, 1, 'any',
        '8,10,12,13,14,15,16', 'Classic spare ball with minimal hook, straight rolling.'
    ),
    (
        '10000000-0000-0000-0000-000000000010', 'Storm', 'Hy-Road', 'reactive_resin',
        'symmetrical', 2.48, 0.052, 8, 5, 8, 'medium',
        '12,13,14,15,16', 'Versatile medium-heavy oil workhorse with strong midlane read.'
    ),
    (
        '10000000-0000-0000-0000-000000000011', 'DV8', 'Ruthless', 'reactive_resin',
        'asymmetrical', 2.45, 0.058, 9, 4, 9, 'heavy',
        '14,15,16', 'Big, angular asymmetric motion for heavy oil.'
    ),
    (
        '10000000-0000-0000-0000-000000000012', 'Pyramid', 'Path', 'plastic',
        'symmetrical', 2.71, 0.018, 1, 9, 1, 'any',
        '8,10,12,13,14,15,16', 'Affordable spare shooting ball with predictable roll.'
    )
ON CONFLICT (id) DO NOTHING;

-- Pattern Intelligence: lane pattern library.
INSERT INTO lane_patterns (
    id, name, pattern_type, oil_volume, oil_distance, difficulty, description,
    recommended_coverstock, recommended_hook_min, recommended_hook_max, notes
) VALUES
    (
        '20000000-0000-0000-0000-000000000001', 'Weekly House League', 'house', 20, 32, 1,
        'Standard house shot with a forgiving blend and generous backend miss room.',
        'reactive_resin', 4, 7, 'Great for building repeatable shots and confidence.'
    ),
    (
        '20000000-0000-0000-0000-000000000002', 'Friday Night Blend', 'house', 22, 34, 1,
        'Slightly longer house pattern with moderate friction down lane.',
        'reactive_resin', 4, 7, 'Common recreational league pattern.'
    ),
    (
        '20000000-0000-0000-0000-000000000003', 'Kegel Scorpion', 'sport', 23, 40, 3,
        'Flat sport pattern requiring precise line and consistent release.',
        'reactive_resin', 6, 8, 'Rewards accuracy over raw power.'
    ),
    (
        '20000000-0000-0000-0000-000000000004', 'Kegel Sinister', 'sport', 24, 41, 3,
        'Demanding sport shot with a tight, flat oil ratio.',
        'reactive_resin', 6, 9, 'Requires strong ball reaction to finish through the pins.'
    ),
    (
        '20000000-0000-0000-0000-000000000005', 'US Open Pattern', 'pba', 25, 41, 4,
        'Ultra-flat, high-volume PBA tour pattern used at the US Open.',
        'reactive_resin', 7, 9, 'Elite-level challenge; minimal room for error.'
    ),
    (
        '20000000-0000-0000-0000-000000000006', 'PBA Cheetah', 'pba', 20, 36, 2,
        'Shorter, higher-volume tour pattern that plays lower and flatter.',
        'reactive_resin', 5, 7, 'Favors players who can play a direct, angular line.'
    ),
    (
        '20000000-0000-0000-0000-000000000007', 'PBA Chameleon', 'pba', 23, 39, 3,
        'Medium-length tour pattern that transitions quickly with play.',
        'reactive_resin', 6, 8, 'Ball motion changes noticeably as the pattern breaks down.'
    ),
    (
        '20000000-0000-0000-0000-000000000008', 'PBA Shark', 'pba', 24, 42, 4,
        'Long, heavy tour pattern demanding strong continuous ball motion.',
        'pearl_reactive', 7, 9, 'One of the toughest touring patterns to strike on.'
    ),
    (
        '20000000-0000-0000-0000-000000000009', 'Challenge Pattern - The Wall', 'challenge', 27, 43, 4,
        'Extreme volume, extreme distance challenge pattern for experienced bowlers.',
        'pearl_reactive', 8, 10, 'Best attempted with a deep arsenal and high ball speed.'
    ),
    (
        '20000000-0000-0000-0000-000000000010', 'Sunday Easy Street', 'house', 18, 30, 1,
        'Short, light-volume house pattern that is very forgiving.',
        'urethane', 2, 5, 'Ideal for beginners or spare-shooting practice.'
    ),
    (
        '20000000-0000-0000-0000-000000000011', 'Masters Challenge', 'sport', 24, 40, 4,
        'Championship-level sport pattern with tight ratios end to end.',
        'reactive_resin', 7, 9, 'Used for high-stakes tournament qualifying rounds.'
    )
ON CONFLICT (id) DO NOTHING;
