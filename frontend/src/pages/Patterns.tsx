import { useQuery } from '@tanstack/react-query'
import { fetchPatterns } from '../api/client'
import LoadingSpinner, { ErrorCard } from '../components/ui'

const OIL_COLORS: Record<string, string> = {
  light: 'text-yellow-400',
  medium: 'text-blue-400',
  heavy: 'text-purple-400',
  very_heavy: 'text-red-400',
}

const TYPE_BADGE: Record<string, string> = {
  house: 'bg-green-800 text-green-200',
  sport: 'bg-yellow-800 text-yellow-200',
  pba: 'bg-red-800 text-red-200',
  custom: 'bg-gray-700 text-gray-200',
}

export default function Patterns() {
  const { data: patterns, isLoading, isError } = useQuery({
    queryKey: ['patterns'],
    queryFn: () => fetchPatterns(),
  })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorCard message="Failed to load patterns." />

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Lane Patterns</h2>
      <p className="text-gray-400 mb-6">{patterns?.length} patterns loaded.</p>

      <div className="overflow-x-auto rounded-xl border border-gray-700">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-800 text-gray-400 text-left">
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Oil Volume</th>
              <th className="px-4 py-3">Length (ft)</th>
              <th className="px-4 py-3">Difficulty</th>
              <th className="px-4 py-3">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {patterns?.map(p => (
              <tr key={p.id} className="hover:bg-gray-800 transition-colors">
                <td className="px-4 py-3 font-medium text-white">{p.name}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${TYPE_BADGE[p.pattern_type] ?? 'bg-gray-700 text-gray-200'}`}>
                    {p.pattern_type.toUpperCase()}
                  </span>
                </td>
                <td className={`px-4 py-3 font-medium ${OIL_COLORS[p.oil_volume] ?? 'text-gray-300'}`}>
                  {p.oil_volume.replaceAll('_', ' ')}
                </td>
                <td className="px-4 py-3 text-gray-300">{p.length_feet ?? '—'}</td>
                <td className="px-4 py-3">
                  {p.difficulty_score != null ? (
                    <span className={`font-bold ${p.difficulty_score >= 8 ? 'text-red-400' : p.difficulty_score >= 6 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {p.difficulty_score}
                    </span>
                  ) : '—'}
                </td>
                <td className="px-4 py-3 text-gray-400 max-w-xs truncate">{p.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
