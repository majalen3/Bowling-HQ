-- 003_vertical_slice_tables.sql
-- Adds persistence tables for Ghost Bowler, Pattern Intelligence, and Simulator.

CREATE TABLE IF NOT EXISTS ghost_bowler_baselines (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    total_games INTEGER NOT NULL,
    overall_average NUMERIC(5,2) NOT NULL,
    overall_strike_rate NUMERIC(4,3) NOT NULL,
    overall_spare_rate NUMERIC(4,3) NOT NULL,
    overall_open_rate NUMERIC(4,3) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pattern_analyses (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    pattern_name VARCHAR(255) NOT NULL,
    difficulty_score NUMERIC(4,2) NOT NULL,
    difficulty_label VARCHAR(50) NOT NULL,
    breakpoint_board NUMERIC(4,1) NOT NULL,
    transition_risk VARCHAR(20) NOT NULL,
    transition_rate NUMERIC(4,3) NOT NULL,
    guidance TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS simulator_runs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    pattern_name VARCHAR(255) NOT NULL,
    ball_name VARCHAR(255) NOT NULL,
    predicted_score INTEGER NOT NULL,
    confidence_low INTEGER NOT NULL,
    confidence_high INTEGER NOT NULL,
    strike_probability NUMERIC(4,3) NOT NULL,
    confidence NUMERIC(4,3) NOT NULL,
    breakpoint_board NUMERIC(4,1) NOT NULL,
    entry_angle_deg NUMERIC(4,1) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ghost_baseline_user
ON ghost_bowler_baselines(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_pattern_analyses_user
ON pattern_analyses(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_simulator_runs_user
ON simulator_runs(user_id, created_at DESC);
