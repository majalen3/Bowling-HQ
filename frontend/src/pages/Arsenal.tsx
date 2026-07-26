import { useQuery } from '@tanstack/react-query'
import { fetchBalls } from '../api/client'
import LoadingSpinner, { ErrorCard } from '../components/ui'

const CONDITION_COLORS: Record<string, string> = {
  dry: 'bg-yellow-700 text-yellow-100',
  medium: 'bg-blue-700 text-blue-100',
  heavy: 'bg-purple-700 text-purple-100',
  all: 'bg-green-700 text-green-100',
}

export default function Arsenal() {
  const { data: balls, isLoading, isError } = useQuery({
    queryKey: ['balls'],
    queryFn: () => fetchBalls(),
  })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorCard message="Failed to load ball catalog." />

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Ball Catalog</h2>
      <p className="text-gray-400 mb-6">{balls?.length} balls in the database.</p>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {balls?.map(ball => (
          <div
            key={ball.id}
            className="rounded-xl bg-gray-800 border border-gray-700 p-5 flex flex-col gap-2"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-semibold text-white">{ball.brand} {ball.name}</p>
                <p className="text-xs text-gray-400">{ball.weight_oz} oz · {ball.core_type} core · {ball.coverstock_type}</p>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${CONDITION_COLORS[ball.best_conditions] ?? 'bg-gray-700 text-gray-200'}`}>
                {ball.best_conditions}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-1">
              {[
                { label: 'Hook', val: ball.hook_potential },
                { label: 'Length', val: ball.length_score },
                { label: 'Backend', val: ball.backend_score },
              ].map(({ label, val }) => (
                <div key={label} className="rounded-lg bg-gray-900 p-2 text-center">
                  <p className="text-xs text-gray-500">{label}</p>
                  <p className="text-lg font-bold text-white">{val ?? '—'}</p>
                </div>
              ))}
            </div>

            {ball.notes && (
              <p className="text-xs text-gray-400 border-t border-gray-700 pt-2 mt-1">{ball.notes}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
