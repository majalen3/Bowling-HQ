import { NavLink } from 'react-router-dom';

const LINKS: Array<{ to: string; label: string; end?: boolean }> = [
  { to: '/', label: 'Home', end: true },
  { to: '/commander', label: 'Commander', end: true },
  { to: '/sessions', label: 'Sessions' },
  { to: '/arsenal', label: 'Arsenal' },
  { to: '/patterns', label: 'Patterns' },
  { to: '/tournament', label: 'Tournament' },
  { to: '/ghost-bowler', label: 'Ghost Bowler' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/auth', label: 'Auth' },
  { to: '/dev', label: 'Dev' },
];

export function NavBar() {
  return (
    <nav className="navbar" aria-label="Primary">
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          className={({ isActive }) =>
            isActive ? 'nav-tab active' : 'nav-tab'
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
