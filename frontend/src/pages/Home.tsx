import { Link } from 'react-router-dom'

const FEATURES = [
  {
    to: '/commander',
    icon: '🤖',
    title: 'Commander AI',
    desc: 'Get instant ball recommendations for any lane pattern.',
    cta: 'Get Recommendation →',
    highlight: true,
  },
  {
    to: '/arsenal',
    icon: '⚙️',
    title: 'Arsenal DNA',
    desc: 'View your complete ball inventory and specifications.',
    cta: 'View Arsenal →',
  },
  {
    to: '/patterns',
    icon: '🛣️',
    title: 'Pattern Intelligence',
    desc: 'Browse house shots, PBA animal patterns, and sport shots.',
    cta: 'View Patterns →',
  },
  {
    to: '/sessions',
    icon: '📊',
    title: 'Sessions',
    desc: 'Track your league nights, tournaments, and practice sessions.',
    cta: 'View Sessions →',
  },
  {
    to: '/ghost-bowler',
    icon: '👻',
    title: 'Ghost Bowler',
    desc: 'Your personal performance baseline built from historical data.',
    cta: 'View Profile →',
  },
]

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto space-y-12">
      {/* Hero */}
      <div className="text-center pt-8">
        <h1 className="text-5xl font-extrabold text-white mb-4">🎳 Bowling HQ</h1>
        <p className="text-xl text-gray-400 max-w-xl mx-auto">
          AI-powered bowling intelligence. Better decisions, better scores.
        </p>
        <Link to="/commander" className="inline-block mt-6 btn-primary text-base px-8 py-3">
          Try Commander AI
        </Link>
      </div>

      {/* Feature grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {FEATURES.map((f) => (
          <Link
            key={f.to}
            to={f.to}
            className={`card flex flex-col gap-3 hover:border-blue-600 transition-colors ${
              f.highlight ? 'border-blue-700 bg-blue-950' : ''
            }`}
          >
            <span className="text-3xl">{f.icon}</span>
            <h2 className="font-bold text-white">{f.title}</h2>
            <p className="text-sm text-gray-400 flex-1">{f.desc}</p>
            <span className="text-blue-400 text-sm font-medium">{f.cta}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
