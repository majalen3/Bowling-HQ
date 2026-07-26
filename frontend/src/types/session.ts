export interface BowlingSession {
  id: number
  user_id: number
  center_id: number | null
  pattern_id: number | null
  session_type: string | null
  session_date: string
  total_games: number | null
  notes: string | null
}
