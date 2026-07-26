# Database Schema Guide

## Design Principles

- Normalization for consistency
- Denormalization for performance where needed
- Soft deletes for audit trails
- Timestamps on all tables

## Core Tables

### Users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_data JSONB,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$')
);
```

### Sessions (Bowling Games)

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    venue_id UUID REFERENCES venues(id),
    date DATE NOT NULL,
    type VARCHAR(50),  -- league, tournament, practice
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_user_date ON sessions(user_id, date DESC);
```

### Games (Individual Games in Session)

```sql
CREATE TABLE games (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(id),
    game_number INT NOT NULL,
    score INT NOT NULL,
    frames JSONB,  -- Detailed frame data
    equipment_id UUID REFERENCES equipment(id),
    lane_number INT,
    lane_condition VARCHAR(50),  -- fresh, heavy, dry
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    CHECK (score >= 0 AND score <= 300),
    CHECK (game_number >= 1 AND game_number <= 10)
);
```

### Equipment (Bowling Balls/Gear)

```sql
CREATE TABLE equipment (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),  -- ball, shoes, towel
    brand VARCHAR(255),
    model VARCHAR(255),
    weight DECIMAL(4,1),  -- for balls
    specifications JSONB,  -- RG, differential, coverstock, etc.
    performance_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    retired_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Venues

```sql
CREATE TABLE venues (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    coordinates POINT,
    lanes_count INT,
    oil_pattern VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_venues_name ON venues(name);
CREATE INDEX idx_venues_location ON venues USING GIST(coordinates);
```

### Videos

```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    session_id UUID REFERENCES sessions(id),
    game_id UUID REFERENCES games(id),
    file_path VARCHAR(255) NOT NULL,
    duration INT,  -- seconds
    format VARCHAR(50),  -- mp4, mov, etc.
    file_size INT,  -- bytes
    analysis_data JSONB,
    status VARCHAR(50),  -- uploading, processing, ready
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE SET NULL
);
```

### Analysis Results

```sql
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY,
    video_id UUID REFERENCES videos(id),
    session_id UUID REFERENCES sessions(id),
    analysis_type VARCHAR(50),  -- form, equipment, patterns
    results JSONB,  -- Detailed analysis data
    confidence_score DECIMAL(3,2),  -- 0.00 to 1.00
    created_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

### Performance Stats (Denormalized for Speed)

```sql
CREATE TABLE performance_stats (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES users(id),
    total_games INT DEFAULT 0,
    average_score DECIMAL(5,2) DEFAULT 0,
    high_score INT DEFAULT 0,
    low_score INT DEFAULT 0,
    strike_rate DECIMAL(3,2) DEFAULT 0,  -- percentage
    spare_rate DECIMAL(3,2) DEFAULT 0,
    consistency_score DECIMAL(3,2) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## Indexes Strategy

### High-Priority Indexes

```sql
-- User queries
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Session queries
CREATE INDEX idx_sessions_user_date ON sessions(user_id, date DESC);
CREATE INDEX idx_sessions_venue ON sessions(venue_id);

-- Game queries
CREATE INDEX idx_games_session ON games(session_id);
CREATE INDEX idx_games_date ON games(created_at DESC);

-- Equipment queries
CREATE INDEX idx_equipment_user ON equipment(user_id);
CREATE INDEX idx_equipment_type ON equipment(type);

-- Video queries
CREATE INDEX idx_videos_user ON videos(user_id);
CREATE INDEX idx_videos_session ON videos(session_id);
CREATE INDEX idx_videos_status ON videos(status);

-- Analysis queries
CREATE INDEX idx_analysis_video ON analysis_results(video_id);
CREATE INDEX idx_analysis_session ON analysis_results(session_id);
CREATE INDEX idx_analysis_type ON analysis_results(analysis_type);
```

## Migration Strategy

### Using Alembic (Python)

```bash
# Create new migration
alembic revision --autogenerate -m "Add sessions table"

# Run migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Migration Template

```python
# alembic/versions/001_create_users_table.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

def downgrade():
    op.drop_table('users')
```

## Data Integrity

### Foreign Keys

```sql
-- Cascade deletes
ALTER TABLE games
ADD CONSTRAINT fk_games_session
FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE;

-- Prevent orphans
ALTER TABLE equipment
ADD CONSTRAINT fk_equipment_user
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
```

### Constraints

```sql
-- Check constraints
ALTER TABLE games
ADD CONSTRAINT check_score CHECK (score >= 0 AND score <= 300);

-- Unique constraints
ALTER TABLE users
ADD CONSTRAINT unique_email UNIQUE (email);
```

## Performance Optimization

### Partitioning (for large tables)

```sql
-- Partition sessions by month
CREATE TABLE sessions_2026_01 PARTITION OF sessions
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### Materialized Views

```sql
-- Cache expensive calculations
CREATE MATERIALIZED VIEW user_statistics AS
SELECT
    user_id,
    COUNT(*) as total_games,
    AVG(score) as average_score,
    MAX(score) as high_score
FROM games
GROUP BY user_id;

CREATE INDEX idx_user_stats_user ON user_statistics(user_id);
```

## Backup Strategy

```bash
# Full backup
pg_dump bowling_hq > backup_full.sql

# Compressed backup
pg_dump bowling_hq | gzip > backup_full.sql.gz

# Restore from backup
psql bowling_hq < backup_full.sql
```

---

**This is a comprehensive database schema guide for implementation.**
