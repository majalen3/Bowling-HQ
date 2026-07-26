import type { RecommendationResponse } from '../types/recommendation'
import ConfidenceDisplay from './ConfidenceDisplay'

interface Props {
  data: RecommendationResponse
}

const DIFFICULTY_LABELS: Record<number, string> = {
  1: 'Easy',
  2: 'Moderate',
  3: 'Challenging',
  4: 'Elite',
}

export default function RecommendationCard({ data }: Props) {
  return (
    <div className="space-y-6">
      {/* Primary recommendation */}
      <div className="card border-blue-700">
        <div className="flex items-start justify-between mb-3">
          <div>
            <p className="text-xs text-blue-400 uppercase tracking-widest mb-1">Commander AI Recommends</p>
            <h2 className="text-3xl font-bold text-white">{data.ball_name}</h2>
          </div>
          <span className="text-2xl">🎳</span>
        </div>

        <ConfidenceDisplay score={data.confidence_score} size="lg" />

        <div className="mt-4 p-3 bg-gray-800 rounded-lg text-sm text-gray-300 leading-relaxed">
          {data.reason}
        </div>

        <div className="mt-3 flex gap-3 text-sm text-gray-400">
          <span>📍 {data.pattern_name}</span>
          <span>•</span>
          <span>Difficulty: {DIFFICULTY_LABELS[data.pattern_difficulty] ?? data.pattern_difficulty}</span>
        </div>

        {data.tip && (
          <div className="mt-3 p-3 bg-blue-950 border border-blue-800 rounded-lg text-sm text-blue-200">
            💡 {data.tip}
          </div>
        )}
      </div>

      {/* Alternatives */}
      {data.alternatives.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Alternatives</h3>
          <div className="space-y-3">
            {data.alternatives.map((alt) => (
              <div key={alt.ball_id} className="card">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-gray-200">{alt.ball_name}</span>
                  <ConfidenceDisplay score={alt.confidence} size="sm" />
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">{alt.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
