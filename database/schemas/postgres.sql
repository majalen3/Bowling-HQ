-- ============================================================
-- Bowling-HQ PostgreSQL Schema
-- Run order: tables with no FK deps first, then dependents.
-- ============================================================

-- ─── Extensions ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Users ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password TEXT         NOT NULL,
    display_name    VARCHAR(100),
    hand            VARCHAR(5)   NOT NULL DEFAULT 'right' CHECK (hand IN ('right', 'left')),
    ball_speed_avg  NUMERIC(4,1),          -- mph
    rev_rate_avg    INTEGER,               -- rpms
    axis_rotation   NUMERIC(5,2),          -- degrees
    axis_tilt       NUMERIC(5,2),          -- degrees
    experience_level VARCHAR(20) NOT NULL DEFAULT 'beginner'
                    CHECK (experience_level IN ('beginner','recreational','competitive','advanced','professional')),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─── Bowling Centers ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bowling_centers (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           VARCHAR(150) NOT NULL,
    address        VARCHAR(255),
    city           VARCHAR(100),
    state          VARCHAR(50),
    country        VARCHAR(50)  NOT NULL DEFAULT 'USA',
    lanes_count    INTEGER,
    year_built     INTEGER,
    last_renovated INTEGER,
    rating         NUMERIC(3,2) CHECK (rating BETWEEN 0 AND 5),
    notes          TEXT,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─── Lane Patterns ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lane_patterns (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(100) NOT NULL,
    pattern_type        VARCHAR(20)  NOT NULL DEFAULT 'house'
                        CHECK (pattern_type IN ('house','sport','pba','custom')),
    oil_volume          VARCHAR(20)  NOT NULL DEFAULT 'medium'
                        CHECK (oil_volume IN ('light','medium','heavy','very_heavy')),
    length_feet         INTEGER,
    difficulty_score    NUMERIC(4,2) CHECK (difficulty_score BETWEEN 1 AND 10),
    board_distribution  JSONB,   -- oil profile per board zone
    description         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Bowling Balls (Master Catalog) ─────────────────────────
CREATE TABLE IF NOT EXISTS bowling_balls (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand               VARCHAR(80)  NOT NULL,
    name                VARCHAR(100) NOT NULL,
    weight_oz           NUMERIC(4,1) NOT NULL,
    core_type           VARCHAR(20)  NOT NULL DEFAULT 'symmetrical'
                        CHECK (core_type IN ('symmetrical','asymmetrical','pancake')),
    rg_min              NUMERIC(5,3),   -- radius of gyration
    differential        NUMERIC(5,3),
    coverstock_type     VARCHAR(30)  NOT NULL DEFAULT 'reactive'
                        CHECK (coverstock_type IN ('plastic','urethane','reactive','particle')),
    finish              VARCHAR(50),
    release_year        INTEGER,
    best_conditions     VARCHAR(20)  NOT NULL DEFAULT 'medium'
                        CHECK (best_conditions IN ('dry','medium','heavy','all')),
    hook_potential      NUMERIC(3,1) CHECK (hook_potential BETWEEN 0 AND 10),
    length_score        NUMERIC(3,1) CHECK (length_score BETWEEN 0 AND 10),
    backend_score       NUMERIC(3,1) CHECK (backend_score BETWEEN 0 AND 10),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (brand, name, weight_oz)
);

-- ─── User Arsenal (bridge: user ↔ ball) ─────────────────────
CREATE TABLE IF NOT EXISTS user_arsenal (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ball_id       UUID         NOT NULL REFERENCES bowling_balls(id),
    layout        VARCHAR(50),          -- e.g. "50x4x35"
    purchase_date DATE,
    games_thrown  INTEGER      NOT NULL DEFAULT 0,
    is_retired    BOOLEAN      NOT NULL DEFAULT FALSE,
    personal_notes TEXT,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─── Bowling Sessions ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bowling_sessions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    center_id     UUID         REFERENCES bowling_centers(id),
    pattern_id    UUID         REFERENCES lane_patterns(id),
    session_type  VARCHAR(20)  NOT NULL DEFAULT 'practice'
                  CHECK (session_type IN ('league','tournament','practice','open')),
    session_date  DATE         NOT NULL,
    duration_min  INTEGER,
    notes         TEXT,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─── Games ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS games (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id    UUID         NOT NULL REFERENCES bowling_sessions(id) ON DELETE CASCADE,
    lane_number   INTEGER,
    primary_ball_id UUID       REFERENCES bowling_balls(id),
    total_score   INTEGER      CHECK (total_score BETWEEN 0 AND 300),
    strike_count  SMALLINT     NOT NULL DEFAULT 0,
    spare_count   SMALLINT     NOT NULL DEFAULT 0,
    open_count    SMALLINT     NOT NULL DEFAULT 0,
    game_number   SMALLINT     NOT NULL DEFAULT 1,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─── Frames ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS frames (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id           UUID         NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    frame_number      SMALLINT     NOT NULL CHECK (frame_number BETWEEN 1 AND 10),
    ball_id           UUID         REFERENCES bowling_balls(id),
    first_ball_pins   SMALLINT     CHECK (first_ball_pins BETWEEN 0 AND 10),
    second_ball_pins  SMALLINT     CHECK (second_ball_pins BETWEEN 0 AND 10),
    third_ball_pins   SMALLINT     CHECK (third_ball_pins BETWEEN 0 AND 10),  -- 10th frame bonus only
    result_type       VARCHAR(10)  NOT NULL DEFAULT 'open'
                      CHECK (result_type IN ('strike','spare','open','split')),
    board_number      SMALLINT,    -- target board
    speed_mph         NUMERIC(4,1),
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (game_id, frame_number)
);

-- ─── Commander Recommendations ───────────────────────────────
CREATE TABLE IF NOT EXISTS commander_recommendations (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id        UUID         REFERENCES bowling_sessions(id),
    frame_number      SMALLINT,
    recommended_ball_id UUID       REFERENCES bowling_balls(id),
    confidence_score  NUMERIC(5,4) CHECK (confidence_score BETWEEN 0 AND 1),
    reasoning         JSONB,       -- structured reasoning breakdown
    was_followed      BOOLEAN,
    actual_result     SMALLINT,    -- pins knocked down
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ─── Tournament Bag Lineups ──────────────────────────────────
CREATE TABLE IF NOT EXISTS tournament_bag_lineups (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    target_pattern_id UUID      REFERENCES lane_patterns(id),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Lineup Balls (bridge: lineup ↔ user_arsenal) ────────────
CREATE TABLE IF NOT EXISTS lineup_balls (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lineup_id        UUID        NOT NULL REFERENCES tournament_bag_lineups(id) ON DELETE CASCADE,
    arsenal_entry_id UUID        NOT NULL REFERENCES user_arsenal(id),
    role             VARCHAR(20) NOT NULL DEFAULT 'primary'
                     CHECK (role IN ('primary','backup','spare','benchmark')),
    ball_order       SMALLINT    NOT NULL DEFAULT 1
);

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_user_arsenal_user        ON user_arsenal(user_id);
CREATE INDEX IF NOT EXISTS idx_user_arsenal_active      ON user_arsenal(user_id) WHERE is_retired = FALSE;
CREATE INDEX IF NOT EXISTS idx_sessions_user_date       ON bowling_sessions(user_id, session_date DESC);
CREATE INDEX IF NOT EXISTS idx_games_session            ON games(session_id);
CREATE INDEX IF NOT EXISTS idx_frames_game              ON frames(game_id);
CREATE INDEX IF NOT EXISTS idx_cmd_recs_user_session    ON commander_recommendations(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_balls_brand_name         ON bowling_balls(brand, name);
CREATE INDEX IF NOT EXISTS idx_lineups_user             ON tournament_bag_lineups(user_id);

-- ============================================================
-- updated_at auto-update trigger
-- ============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_user_arsenal_updated_at
    BEFORE UPDATE ON user_arsenal
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_sessions_updated_at
    BEFORE UPDATE ON bowling_sessions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_lineups_updated_at
    BEFORE UPDATE ON tournament_bag_lineups
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
