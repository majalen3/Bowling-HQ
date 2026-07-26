import { Link, Outlet, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/dashboard', label: '🏠 Dashboard' },
  { to: '/arsenal', label: '🎳 Arsenal' },
  { to: '/patterns', label: '🛣️ Patterns' },
  { to: '/sessions', label: '📋 Sessions' },
  { to: '/recommendations', label: '🤖 Commander AI' },
]

export default function Layout() {
  const { pathname } = useLocation()

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="px-6 py-5 border-b border-gray-800">
          <h1 className="text-xl font-bold text-blue-400 tracking-wide">Bowling HQ</h1>
          <p className="text-xs text-gray-500 mt-0.5">v0.1.0</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={[
                'block px-3 py-2 rounded-md text-sm font-medium transition-colors',
                pathname.startsWith(to)
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white',
              ].join(' ')}
            >
              {label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}
