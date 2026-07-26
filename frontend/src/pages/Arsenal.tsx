import { useQuery } from '@tanstack/react-query'
import { fetchArsenal } from '../services/api'
import type { Ball } from '../types/ball'

function RatingBar({ value, max = 10 }: { value: number | null; max?: number }) {
  if (value === null) return <span className="text-gray-600">—</span>
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 bg-gray-700 rounded-full h-1.5">
        <div
          className="bg-blue-500 h-1.5 rounded-full"
          style={{ width: `${(value / max) * 100}%` }}
        />
      </div>
      <span className="text-xs text-gray-400">{value}/{max}</span>
    </div>
  )
}

function BallCard({ ball }: { ball: Ball }) {
  return (
    <div className="card hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-bold text-white text-lg">{ball.brand} {ball.name}</h3>
          <p className="text-sm text-gray-400">{ball.purpose ?? 'General use'}</p>
        </div>
        {ball.is_spare_ball && (
          <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full">Spare</span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mb-4">
        <div>
          <span className="text-gray-500">Weight</span>
          <p className="text-gray-200">{ball.weight_lbs} lbs</p>
        </div>
        <div>
          <span className="text-gray-500">Cover</span>
          <p className="text-gray-200 capitalize">{ball.coverstock_type?.replace('_', ' ') ?? '—'}</p>
        </div>
        <div>
          <span className="text-gray-500">Core</span>
          <p className="text-gray-200 capitalize">{ball.core_type ?? '—'}</p>
        </div>
        <div>
          <span className="text-gray-500">RG / Diff</span>
          <p className="text-gray-200">{ball.rg ?? '—'} / {ball.differential ?? '—'}</p>
        </div>
        <div>
          <span className="text-gray-500">Finish</span>
          <p className="text-gray-200">{ball.finish?.replace(/_/g, ' ') ?? '—'}</p>
        </div>
        <div>
          <span className="text-gray-500">Layout</span>
          <p className="text-gray-200">{ball.layout ?? '—'}</p>
        </div>
      </div>

      {!ball.is_spare_ball && (
        <div className="space-y-1.5 pt-3 border-t border-gray-800">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">Hook</span>
            <RatingBar value={ball.hook_potential} />
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">Length</span>
            <RatingBar value={ball.length_rating} />
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">Backend</span>
            <RatingBar value={ball.backend_rating} />
          </div>
        </div>
      )}

      {ball.notes && (
        <p className="mt-3 text-xs text-gray-500 italic">{ball.notes}</p>
      )}
    </div>
  )
}

export default function Arsenal() {
  const { data: balls, isLoading, error } = useQuery({
    queryKey: ['arsenal'],
    queryFn: fetchArsenal,
  })

  const strikeBalls = balls?.filter((b) => !b.is_spare_ball) ?? []
  const spareBalls  = balls?.filter((b) => b.is_spare_ball)  ?? []

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">⚙️ Arsenal DNA</h1>
        <p className="text-gray-400 mt-1">Your complete ball inventory and specifications.</p>
      </div>

      {isLoading && <p className="text-gray-500">Loading arsenal…</p>}
      {error    && <p className="text-red-400">Failed to load arsenal.</p>}

      {strikeBalls.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-gray-300 mb-4">Strike Balls ({strikeBalls.length})</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {strikeBalls.map((b) => <BallCard key={b.id} ball={b} />)}
          </div>
        </section>
      )}

      {spareBalls.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-gray-300 mb-4">Spare Balls ({spareBalls.length})</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {spareBalls.map((b) => <BallCard key={b.id} ball={b} />)}
          </div>
        </section>
      )}
    </div>
  )
}
