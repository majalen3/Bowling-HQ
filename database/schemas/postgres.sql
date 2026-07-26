-- =============================================================================
-- Bowling-HQ PostgreSQL Schema
-- =============================================================================

-- Users
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    display_name    VARCHAR(100),
    hand            VARCHAR(10)  DEFAULT 'right',  -- 'right' | 'left'
    ball_speed_avg  DECIMAL(4,1),                  -- mph
    rev_rate_avg    INTEGER,                        -- rpm
    created_at      TIMESTAMPTZ  DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Bowling Centers
CREATE TABLE IF NOT EXISTS bowling_centers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    location        VARCHAR(255),
    number_of_lanes INTEGER,
    notes           TEXT,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Lane Patterns
CREATE TABLE IF NOT EXISTS patterns (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    pattern_type    VARCHAR(50),                   -- 'house' | 'sport' | 'pba' | 'custom'
    oil_volume      VARCHAR(20),                   -- 'light' | 'medium' | 'heavy' | 'very_heavy'
    oil_length_ft   INTEGER,                        -- feet (e.g. 38)
    difficulty      INTEGER CHECK (difficulty BETWEEN 1 AND 4),
    description     TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Arsenal — Bowling Balls
CREATE TABLE IF NOT EXISTS balls (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    brand           VARCHAR(50)  NOT NULL,
    weight_lbs      INTEGER      NOT NULL,
    coverstock_type VARCHAR(50),                   -- 'plastic' | 'urethane' | 'reactive_resin' | 'hybrid_reactive' | 'pearl_reactive'
    core_type       VARCHAR(20),                   -- 'symmetrical' | 'asymmetrical'
    rg              DECIMAL(4,3),                  -- radius of gyration (2.40-2.80)
    differential    DECIMAL(5,3),                  -- flare potential (0.010-0.060)
    finish          VARCHAR(50),                   -- 'polished' | '500_grit' | '1000_grit' | '2000_grit' | '4000_grit'
    layout          VARCHAR(50),                   -- drilling layout e.g. '50x4x35'
    purpose         VARCHAR(150),
    hook_potential  INTEGER CHECK (hook_potential  BETWEEN 1 AND 10),
    length_rating   INTEGER CHECK (length_rating   BETWEEN 1 AND 10),
    backend_rating  INTEGER CHECK (backend_rating  BETWEEN 1 AND 10),
    is_spare_ball   BOOLEAN      DEFAULT FALSE,
    active          BOOLEAN      DEFAULT TRUE,
    notes           TEXT,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Bowling Sessions
CREATE TABLE IF NOT EXISTS bowling_sessions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER      REFERENCES users(id) ON DELETE CASCADE,
    center_id       INTEGER      REFERENCES bowling_centers(id),
    pattern_id      INTEGER      REFERENCES patterns(id),
    session_type    VARCHAR(50),                   -- 'league' | 'tournament' | 'practice' | 'open'
    session_date    DATE         NOT NULL,
    total_games     INTEGER,
    notes           TEXT,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Games (within a session)
CREATE TABLE IF NOT EXISTS games (
    id              SERIAL PRIMARY KEY,
    session_id      INTEGER      REFERENCES bowling_sessions(id) ON DELETE CASCADE,
    game_number     INTEGER      NOT NULL,
    score           INTEGER      CHECK (score BETWEEN 0 AND 300),
    ball_id         INTEGER      REFERENCES balls(id),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- Frames (within a game)
CREATE TABLE IF NOT EXISTS frames (
    id              SERIAL PRIMARY KEY,
    game_id         INTEGER      REFERENCES games(id) ON DELETE CASCADE,
    frame_number    INTEGER      NOT NULL CHECK (frame_number BETWEEN 1 AND 10),
    ball_1          INTEGER,                       -- pins knocked on first ball
    ball_2          INTEGER,                       -- pins knocked on second ball
    ball_3          INTEGER,                       -- third ball (10th frame fill)
    is_strike       BOOLEAN      DEFAULT FALSE,
    is_spare        BOOLEAN      DEFAULT FALSE,
    frame_score     INTEGER,
    running_total   INTEGER,
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- AI Recommendations (historical log)
CREATE TABLE IF NOT EXISTS recommendations (
    id                   SERIAL PRIMARY KEY,
    user_id              INTEGER      REFERENCES users(id),
    center_id            INTEGER      REFERENCES bowling_centers(id),
    pattern_id           INTEGER      REFERENCES patterns(id),
    session_type         VARCHAR(50),
    recommended_ball_id  INTEGER      REFERENCES balls(id),
    confidence_score     DECIMAL(5,2),
    reason               TEXT,
    alternatives         JSONB,
    was_used             BOOLEAN,
    actual_score         INTEGER,
    created_at           TIMESTAMPTZ  DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user      ON bowling_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_center    ON bowling_sessions(center_id);
CREATE INDEX IF NOT EXISTS idx_games_session      ON games(session_id);
CREATE INDEX IF NOT EXISTS idx_frames_game        ON frames(game_id);
CREATE INDEX IF NOT EXISTS idx_recs_user          ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recs_pattern       ON recommendations(pattern_id);
CREATE INDEX IF NOT EXISTS idx_balls_active       ON balls(active);
