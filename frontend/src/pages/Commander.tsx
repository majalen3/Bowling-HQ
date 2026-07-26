import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { fetchPatterns, getRecommendation } from '../services/api'
import type { RecommendationRequest } from '../types/recommendation'
import RecommendationCard from '../components/RecommendationCard'

const SESSION_TYPES = [
  { value: 'league',     label: 'League Night' },
  { value: 'tournament', label: 'Tournament' },
  { value: 'practice',   label: 'Practice' },
  { value: 'open',       label: 'Open Bowling' },
]

export default function Commander() {
  const [patternId, setPatternId] = useState<number | ''>('')
  const [sessionType, setSessionType] = useState('league')

  const { data: patterns, isLoading: patternsLoading } = useQuery({
    queryKey: ['patterns'],
    queryFn: fetchPatterns,
  })

  const { mutate, data: recommendation, isPending, error } = useMutation({
    mutationFn: (req: RecommendationRequest) => getRecommendation(req),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!patternId) return
    mutate({ pattern_id: Number(patternId), session_type: sessionType })
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">🤖 Commander AI</h1>
        <p className="text-gray-400 mt-1">
          Get an instant ball recommendation based on your lane pattern and session type.
        </p>
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="card space-y-5">
        <div>
          <label className="label">Lane Pattern</label>
          {patternsLoading ? (
            <p className="text-gray-500 text-sm">Loading patterns…</p>
          ) : (
            <select
              className="select-input"
              value={patternId}
              onChange={(e) => setPatternId(e.target.value ? Number(e.target.value) : '')}
              required
            >
              <option value="">— Select a pattern —</option>
              {patterns?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                  {p.oil_volume ? ` · ${p.oil_volume.replace('_', ' ')} oil` : ''}
                  {p.oil_length_ft ? ` · ${p.oil_length_ft} ft` : ''}
                  {p.difficulty ? ` · Diff ${p.difficulty}/4` : ''}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="label">Session Type</label>
          <select
            className="select-input"
            value={sessionType}
            onChange={(e) => setSessionType(e.target.value)}
          >
            {SESSION_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="btn-primary w-full"
          disabled={!patternId || isPending}
        >
          {isPending ? 'Analyzing…' : '🎳 Get Recommendation'}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="card border-red-800 text-red-400">
          ⚠️ {(error as Error).message}
        </div>
      )}

      {/* Result */}
      {recommendation && <RecommendationCard data={recommendation} />}
    </div>
  )
}
