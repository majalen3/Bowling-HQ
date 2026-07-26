import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ─── Types ────────────────────────────────────────────────────────────────────

export interface BowlingBall {
  id: string
  brand: string
  name: string
  weight_oz: number
  core_type: string
  rg_min: number | null
  differential: number | null
  coverstock_type: string
  finish: string | null
  release_year: number | null
  best_conditions: string
  hook_potential: number | null
  length_score: number | null
  backend_score: number | null
  notes: string | null
}

export interface LanePattern {
  id: string
  name: string
  pattern_type: string
  oil_volume: string
  length_feet: number | null
  difficulty_score: number | null
  description: string | null
}

export interface BowlingCenter {
  id: string
  name: string
  city: string | null
  state: string | null
  country: string
  lanes_count: number | null
  rating: number | null
  notes: string | null
}

export interface ArsenalEntry {
  id: string
  user_id: string
  ball_id: string
  ball: BowlingBall
  layout: string | null
  purchase_date: string | null
  games_thrown: number
  is_retired: boolean
  personal_notes: string | null
}

export interface GameOut {
  id: string
  session_id: string
  lane_number: number | null
  primary_ball_id: string | null
  total_score: number | null
  strike_count: number
  spare_count: number
  open_count: number
  game_number: number
}

export interface SessionOut {
  id: string
  user_id: string
  session_type: string
  session_date: string
  duration_min: number | null
  notes: string | null
  games: GameOut[]
}

export interface RecommendationOut {
  recommended_ball: BowlingBall
  confidence: number
  reason: string
  strategy: string
  alternatives: { ball: BowlingBall; reason: string }[]
  pattern: LanePattern | null
  raw_scores: Record<string, unknown>
}

// ─── API functions ────────────────────────────────────────────────────────────

export const fetchBalls = (brand?: string) =>
  api.get<BowlingBall[]>('/arsenal/balls', { params: brand ? { brand } : undefined })
    .then(r => r.data)

export const fetchPatterns = (pattern_type?: string) =>
  api.get<LanePattern[]>('/patterns', { params: pattern_type ? { pattern_type } : undefined })
    .then(r => r.data)

export const fetchCenters = () =>
  api.get<BowlingCenter[]>('/centers').then(r => r.data)

export const fetchUserArsenal = (userId: string) =>
  api.get<ArsenalEntry[]>(`/arsenal/users/${userId}`).then(r => r.data)

export const fetchSessions = (userId: string) =>
  api.get<SessionOut[]>('/sessions', { params: { user_id: userId } }).then(r => r.data)

export const fetchRecommendation = (payload: {
  user_id: string
  pattern_id?: string
  session_type?: string
  oil_volume?: string
}) =>
  api.post<RecommendationOut>('/recommendations/opening-ball', payload).then(r => r.data)
