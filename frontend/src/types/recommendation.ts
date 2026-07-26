export interface AlternativeBall {
  ball_id: number
  ball_name: string
  confidence: number
  reason: string
}

export interface RecommendationRequest {
  pattern_id: number
  session_type: string
  center_id?: number
  user_id?: number
}

export interface RecommendationResponse {
  ball_id: number
  ball_name: string
  brand: string
  confidence_score: number
  reason: string
  alternatives: AlternativeBall[]
  pattern_name: string
  pattern_difficulty: number
  tip: string | null
}
