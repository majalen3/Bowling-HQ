import { useQuery } from '@tanstack/react-query'
import { fetchPatterns } from '../services/api'

const DIFFICULTY_COLORS: Record<number, string> = {
  1: 'bg-green-900 text-green-300',
  2: 'bg-yellow-900 text-yellow-300',
  3: 'bg-orange-900 text-orange-300',
  4: 'bg-red-900 text-red-300',
}

const DIFFICULTY_LABELS: Record<number, string> = {
  1: 'Easy',
  2: 'Moderate',
  3: 'Challenging',
  4: 'Elite',
}

const OIL_LABELS: Record<string, string> = {
  light: '💧 Light',
  medium: '💧💧 Medium',
  heavy: '💧💧💧 Heavy',
  very_heavy: '💧💧💧💧 Very Heavy',
}

export default function Patterns() {
  const { data: patterns, isLoading, error } = useQuery({
    queryKey: ['patterns'],
    queryFn: fetchPatterns,
  })

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">🛣️ Pattern Intelligence</h1>
        <p className="text-gray-400 mt-1">Lane patterns available for analysis and Commander AI recommendations.</p>
      </div>

      {isLoading && <p className="text-gray-500">Loading patterns…</p>}
      {error    && <p className="text-red-400">Failed to load patterns.</p>}

      <div className="space-y-3">
        {patterns?.map((p) => (
          <div key={p.id} className="card">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="font-semibold text-white">{p.name}</h3>
                <p className="text-xs text-gray-500 capitalize mt-0.5">{p.pattern_type ?? 'unknown'} pattern</p>
              </div>
              {p.difficulty != null && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${DIFFICULTY_COLORS[p.difficulty] ?? ''}`}>
                  {DIFFICULTY_LABELS[p.difficulty] ?? `Diff ${p.difficulty}`}
                </span>
              )}
            </div>

            <div className="flex gap-4 text-sm text-gray-400 mb-2">
              {p.oil_volume && <span>{OIL_LABELS[p.oil_volume] ?? p.oil_volume}</span>}
              {p.oil_length_ft && <span>📏 {p.oil_length_ft} ft</span>}
            </div>

            {p.description && (
              <p className="text-sm text-gray-400 leading-relaxed">{p.description}</p>
            )}
            {p.notes && (
              <p className="text-xs text-gray-600 mt-1 italic">{p.notes}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
