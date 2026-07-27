-- 002_full_schema.sql
-- Expand the schema with the full Bowling-HQ feature set. Idempotent.

ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

CREATE TABLE IF NOT EXISTS bowling_centers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    lane_surface VARCHAR(50) DEFAULT 'synthetic',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lane_patterns (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    length_ft NUMERIC(5,2) NOT NULL,
    volume_ml NUMERIC(5,2) NOT NULL,
    asymmetry_index NUMERIC(4,3) NOT NULL DEFAULT 0.0,
    front_oil_pct NUMERIC(4,3) NOT NULL DEFAULT 0.34,
    mid_oil_pct NUMERIC(4,3) NOT NULL DEFAULT 0.33,
    backend_oil_pct NUMERIC(4,3) NOT NULL DEFAULT 0.33,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bowling_balls (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    coverstock VARCHAR(100) NOT NULL,
    rg NUMERIC(4,3) NOT NULL,
    differential NUMERIC(5,4) NOT NULL,
    mass_bias NUMERIC(5,4) NOT NULL DEFAULT 0.0,
    surface_grit INTEGER NOT NULL DEFAULT 3000,
    weight_lbs INTEGER NOT NULL DEFAULT 15,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_arsenal (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    ball_id UUID NOT NULL REFERENCES bowling_balls(id),
    notes TEXT,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (user_id, ball_id)
);

CREATE TABLE IF NOT EXISTS frames (
    id UUID PRIMARY KEY,
    game_id UUID NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL CHECK (frame_number BETWEEN 1 AND 10),
    ball1 INTEGER NOT NULL,
    ball2 INTEGER,
    ball3 INTEGER,
    is_strike BOOLEAN DEFAULT FALSE,
    is_spare BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (game_id, frame_number)
);

CREATE TABLE IF NOT EXISTS commander_recommendations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID REFERENCES bowling_sessions(id),
    recommended_ball_id UUID REFERENCES bowling_balls(id),
    pattern_name VARCHAR(255),
    pattern_length_ft NUMERIC(5,2),
    pattern_volume_ml NUMERIC(5,2),
    fit_score NUMERIC(5,2),
    confidence NUMERIC(4,3),
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tournament_bag_lineups (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    pattern_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lineup_balls (
    id UUID PRIMARY KEY,
    lineup_id UUID NOT NULL REFERENCES tournament_bag_lineups(id)
        ON DELETE CASCADE,
    ball_id UUID NOT NULL REFERENCES bowling_balls(id),
    slot_order INTEGER NOT NULL,
    rationale TEXT,
    UNIQUE (lineup_id, slot_order)
);

CREATE INDEX IF NOT EXISTS idx_user_arsenal_user ON user_arsenal(user_id);
CREATE INDEX IF NOT EXISTS idx_commander_recs_user
ON commander_recommendations(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_frames_game ON frames(game_id);
