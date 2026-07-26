import { useQuery } from '@tanstack/react-query'
import { fetchGhostBowlerProfile } from '../services/api'

export default function GhostBowler() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['ghost-bowler'],
    queryFn: fetchGhostBowlerProfile,
  })

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">👻 Ghost Bowler</h1>
        <p className="text-gray-400 mt-1">
          Your personal performance baseline — built from your bowling history.
        </p>
      </div>

      {isLoading && <p className="text-gray-500">Loading profile…</p>}
      {error    && <p className="text-red-400">Failed to load Ghost Bowler profile.</p>}

      {data && (
        <>
          {/* User info */}
          {data.user && (
            <div className="card">
              <h2 className="text-lg font-semibold text-white mb-4">Bowler Profile</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Name</span>
                  <p className="text-gray-200">{data.user.display_name ?? data.user.username}</p>
                </div>
                <div>
                  <span className="text-gray-500">Hand</span>
                  <p className="text-gray-200 capitalize">{data.user.hand ?? '—'}</p>
                </div>
                <div>
                  <span className="text-gray-500">Avg Ball Speed</span>
                  <p className="text-gray-200">{data.user.ball_speed_avg ? `${data.user.ball_speed_avg} mph` : '—'}</p>
                </div>
                <div>
                  <span className="text-gray-500">Rev Rate</span>
                  <p className="text-gray-200">{data.user.rev_rate_avg ? `${data.user.rev_rate_avg} rpm` : '—'}</p>
                </div>
              </div>
            </div>
          )}

          {/* Performance */}
          {data.performance && (
            <div className="card">
              <h2 className="text-lg font-semibold text-white mb-4">Performance Stats</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                {[
                  { label: 'Sessions',   value: data.performance.total_sessions },
                  { label: 'Games',      value: data.performance.total_games },
                  { label: 'Avg Score',  value: data.performance.avg_score ?? '—' },
                  { label: 'High Game',  value: data.performance.high_game ?? '—' },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-gray-800 rounded-lg p-3">
                    <p className="text-2xl font-bold text-white">{value}</p>
                    <p className="text-xs text-gray-500 mt-1">{label}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Status */}
          <div className={`card border ${data.status === 'active' ? 'border-green-700' : 'border-yellow-700'}`}>
            <p className={`font-medium ${data.status === 'active' ? 'text-green-400' : 'text-yellow-400'}`}>
              {data.status === 'active' ? '✅' : '⏳'} {data.message}
            </p>
          </div>
        </>
      )}
    </div>
  )
}
