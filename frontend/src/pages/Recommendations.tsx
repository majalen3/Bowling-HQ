import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { fetchRecommendation, type RecommendationOut } from '../api/client'
import LoadingSpinner, { ErrorCard } from '../components/ui'

// Demo user ID — would come from auth in a real session
const DEMO_USER_ID = '00000000-0000-0000-0000-000000000001'

const OIL_OPTIONS = ['light', 'medium', 'heavy', 'very_heavy']
const SESSION_TYPES = ['practice', 'league', 'tournament', 'open']

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 75 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="mt-1">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>Confidence</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function Recommendations() {
  const [oilVolume, setOilVolume] = useState('medium')
  const [sessionType, setSessionType] = useState('practice')

  const mutation = useMutation({
    mutationFn: () =>
      fetchRecommendation({
        user_id: DEMO_USER_ID,
        oil_volume: oilVolume,
        session_type: sessionType,
      }),
  })

  const rec: RecommendationOut | undefined = mutation.data

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Commander AI</h2>
      <p className="text-gray-400 mb-6">
        Get an intelligent opening-ball recommendation based on lane conditions.
      </p>

      {/* Request form */}
      <div className="rounded-xl bg-gray-800 border border-gray-700 p-6 mb-6 max-w-md">
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Oil Volume</label>
            <select
              value={oilVolume}
              onChange={e => setOilVolume(e.target.value)}
              className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              {OIL_OPTIONS.map(o => (
                <option key={o} value={o}>{o.replaceAll('_', ' ')}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Session Type</label>
            <select
              value={sessionType}
              onChange={e => setSessionType(e.target.value)}
              className="w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              {SESSION_TYPES.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {mutation.isPending ? 'Analyzing…' : '🤖 Get Recommendation'}
          </button>
        </div>
      </div>

      {mutation.isPending && <LoadingSpinner />}
      {mutation.isError && <ErrorCard message="Failed to get recommendation. Is the API running?" />}

      {rec && (
        <div className="space-y-4 max-w-2xl">
          {/* Top pick */}
          <div className="rounded-xl bg-blue-900/30 border border-blue-700 p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🏆</span>
              <h3 className="text-lg font-bold text-blue-300">Top Pick</h3>
            </div>
            <p className="text-2xl font-bold text-white">
              {rec.recommended_ball.brand} {rec.recommended_ball.name}
            </p>
            <p className="text-gray-400 text-sm mt-0.5">
              {rec.recommended_ball.weight_oz} oz · {rec.recommended_ball.coverstock_type} · {rec.recommended_ball.best_conditions}
            </p>
            <ConfidenceBar value={rec.confidence} />
            <p className="text-gray-300 mt-4 text-sm">{rec.reason}</p>
          </div>

          {/* Strategy */}
          <div className="rounded-xl bg-gray-800 border border-gray-700 p-5">
            <h4 className="font-semibold text-gray-300 mb-2">🎯 Strategy</h4>
            <p className="text-gray-400 text-sm">{rec.strategy}</p>
          </div>

          {/* Alternatives */}
          {rec.alternatives.length > 0 && (
            <div className="rounded-xl bg-gray-800 border border-gray-700 p-5">
              <h4 className="font-semibold text-gray-300 mb-3">🔄 Alternatives</h4>
              <div className="space-y-3">
                {rec.alternatives.map(alt => (
                  <div key={alt.ball.id} className="flex items-start gap-3 text-sm">
                    <span className="text-gray-500 mt-0.5">•</span>
                    <div>
                      <p className="font-medium text-white">{alt.ball.brand} {alt.ball.name}</p>
                      <p className="text-gray-400">{alt.reason}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
