import axios from 'axios'
import type { Ball } from '../types/ball'
import type { RecommendationRequest, RecommendationResponse } from '../types/recommendation'
import type { BowlingSession } from '../types/session'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

// ── Arsenal ─────────────────────────────────────────────────────────────────
export const fetchArsenal = async (): Promise<Ball[]> => {
  const { data } = await api.get<Ball[]>('/arsenal/')
  return data
}

export const fetchBall = async (id: number): Promise<Ball> => {
  const { data } = await api.get<Ball>(`/arsenal/${id}`)
  return data
}

// ── Patterns ─────────────────────────────────────────────────────────────────
export interface Pattern {
  id: number
  name: string
  pattern_type: string | null
  oil_volume: string | null
  oil_length_ft: number | null
  difficulty: number | null
  description: string | null
  notes: string | null
}

export const fetchPatterns = async (): Promise<Pattern[]> => {
  const { data } = await api.get<Pattern[]>('/patterns/')
  return data
}

// ── Commander AI ─────────────────────────────────────────────────────────────
export const getRecommendation = async (
  req: RecommendationRequest,
): Promise<RecommendationResponse> => {
  const { data } = await api.post<RecommendationResponse>('/commander/opening-ball', req)
  return data
}

// ── Sessions ─────────────────────────────────────────────────────────────────
export const fetchSessions = async (): Promise<BowlingSession[]> => {
  const { data } = await api.get<BowlingSession[]>('/sessions/')
  return data
}

// ── Ghost Bowler ─────────────────────────────────────────────────────────────
export const fetchGhostBowlerProfile = async () => {
  const { data } = await api.get('/ghost-bowler/profile')
  return data
}
