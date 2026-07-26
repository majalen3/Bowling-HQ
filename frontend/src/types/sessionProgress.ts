export type SessionProgressItem = {
  id: string;
  session_type: string;
  location_name: string | null;
  started_at: string;
  completed_at: string | null;
};

export type SessionProgressSnapshot = {
  total_sessions: number;
  completed_sessions: number;
  active_sessions: number;
  sessions: SessionProgressItem[];
};

export type SessionCreateInput = {
  session_type: string;
  location_name?: string;
};
