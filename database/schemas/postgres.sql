CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bowling_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    session_type VARCHAR(50) NOT NULL,
    location_name VARCHAR(255),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS games (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES bowling_sessions(id) ON DELETE CASCADE,
    game_number INTEGER NOT NULL,
    score INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (session_id, game_number)
);

-- Feature: Arsenal DNA
CREATE TABLE IF NOT EXISTS bowling_balls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    coverstock_type VARCHAR(50) NOT NULL, -- 'plastic', 'urethane', 'reactive_resin', 'pearl_reactive'
    core_type VARCHAR(50) NOT NULL,       -- 'symmetrical', 'asymmetrical'
    rg DECIMAL(4,2),                      -- 2.40 to 2.80
    differential DECIMAL(4,3),            -- 0.010 to 0.060
    hook_potential INTEGER,               -- 1-10
    length INTEGER,                       -- 1-10 (1=early, 10=long)
    backend INTEGER,                      -- 1-10
    oil_condition VARCHAR(50),            -- 'dry', 'light', 'medium', 'heavy', 'very_heavy'
    weight_options VARCHAR(100),          -- e.g. '12,14,15,16'
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_arsenal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    ball_id UUID NOT NULL REFERENCES bowling_balls(id),
    purchase_date DATE,
    layout VARCHAR(100),
    notes TEXT,
    games_played INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, ball_id)
);

-- Feature: Pattern Intelligence
CREATE TABLE IF NOT EXISTS lane_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,    -- 'house', 'sport', 'challenge', 'pba'
    oil_volume INTEGER,                   -- milliliters, e.g. 25
    oil_distance INTEGER,                 -- feet, e.g. 40
    difficulty INTEGER,                   -- 1-4 (1=easy house, 4=ultra)
    description TEXT,
    recommended_coverstock VARCHAR(50),   -- 'plastic', 'urethane', 'reactive_resin', 'pearl_reactive'
    recommended_hook_min INTEGER,
    recommended_hook_max INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Feature: Tournament Bag
CREATE TABLE IF NOT EXISTS tournament_lineups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    tournament_name VARCHAR(200),
    pattern_id UUID REFERENCES lane_patterns(id),
    strategy VARCHAR(50),  -- 'conservative', 'versatile', 'aggressive', 'defensive'
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lineup_balls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lineup_id UUID NOT NULL REFERENCES tournament_lineups(id) ON DELETE CASCADE,
    user_arsenal_id UUID NOT NULL REFERENCES user_arsenal(id),
    role VARCHAR(50) NOT NULL,  -- 'primary', 'secondary', 'tertiary', 'spare'
    order_index INTEGER NOT NULL,
    notes TEXT
);
