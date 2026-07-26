import { Link, useLocation } from 'react-router-dom'

const NAV_LINKS = [
  { to: '/',             label: '🎳 Bowling HQ' },
  { to: '/commander',   label: 'Commander AI' },
  { to: '/arsenal',     label: 'Arsenal' },
  { to: '/patterns',    label: 'Patterns' },
  { to: '/sessions',    label: 'Sessions' },
  { to: '/ghost-bowler',label: 'Ghost Bowler' },
]

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 flex items-center gap-1 h-14 overflow-x-auto">
        {NAV_LINKS.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={`px-3 py-1.5 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
              pathname === to
                ? 'bg-blue-700 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
          >
            {label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
