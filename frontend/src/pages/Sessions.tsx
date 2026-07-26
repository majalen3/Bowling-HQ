import { useQuery } from '@tanstack/react-query'
import { fetchSessions } from '../services/api'

export default function Sessions() {
  const { data: sessions, isLoading, error } = useQuery({
    queryKey: ['sessions'],
    queryFn: fetchSessions,
  })

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">📊 Session Intelligence</h1>
        <p className="text-gray-400 mt-1">Track and review your bowling sessions over time.</p>
      </div>

      {isLoading && <p className="text-gray-500">Loading sessions…</p>}
      {error    && <p className="text-red-400">Failed to load sessions.</p>}

      {sessions?.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-4xl mb-4">🎳</p>
          <p className="text-gray-300 font-medium">No sessions yet</p>
          <p className="text-gray-500 text-sm mt-1">
            Use the API at <code className="text-blue-400">POST /api/v1/sessions/</code> to record your first session.
          </p>
        </div>
      )}

      <div className="space-y-3">
        {sessions?.map((s) => (
          <div key={s.id} className="card">
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-white capitalize">
                {s.session_type ?? 'Session'} — {s.session_date}
              </span>
              {s.total_games != null && (
                <span className="text-sm text-gray-400">{s.total_games} game{s.total_games !== 1 ? 's' : ''}</span>
              )}
            </div>
            {s.notes && <p className="text-sm text-gray-500">{s.notes}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}
