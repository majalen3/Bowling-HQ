import { useQuery } from '@tanstack/react-query'
import { fetchBalls, fetchCenters, fetchPatterns } from '../api/client'
import { StatCard } from '../components/ui'

export default function Dashboard() {
  const balls = useQuery({ queryKey: ['balls'], queryFn: () => fetchBalls() })
  const patterns = useQuery({ queryKey: ['patterns'], queryFn: () => fetchPatterns() })
  const centers = useQuery({ queryKey: ['centers'], queryFn: () => fetchCenters() })

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Dashboard</h2>
      <p className="text-gray-400 mb-8">Welcome to Bowling HQ — your intelligent bowling platform.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <StatCard
          label="Balls in Catalog"
          value={balls.data?.length ?? '—'}
          sub="full equipment database"
        />
        <StatCard
          label="Lane Patterns"
          value={patterns.data?.length ?? '—'}
          sub="house, sport & PBA"
        />
        <StatCard
          label="Bowling Centers"
          value={centers.data?.length ?? '—'}
          sub="registered venues"
        />
        <StatCard
          label="Commander AI"
          value="Active"
          sub="opening-ball engine ready"
        />
      </div>

      <div className="rounded-xl bg-gray-800 border border-gray-700 p-6">
        <h3 className="font-semibold text-lg mb-3">Quick Links</h3>
        <ul className="space-y-2 text-sm text-gray-300">
          <li>🎳 <a href="/arsenal" className="text-blue-400 hover:underline">Browse the ball catalog</a></li>
          <li>🤖 <a href="/recommendations" className="text-blue-400 hover:underline">Get a Commander AI recommendation</a></li>
          <li>🛣️ <a href="/patterns" className="text-blue-400 hover:underline">View lane patterns</a></li>
          <li>📋 <a href="/sessions" className="text-blue-400 hover:underline">View bowling sessions</a></li>
        </ul>
      </div>
    </div>
  )
}
