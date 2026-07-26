CREATE INDEX IF NOT EXISTS idx_bowling_sessions_user_started_at
ON bowling_sessions (user_id, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_bowling_sessions_completion
ON bowling_sessions (user_id, completed_at);
