import { NavLink } from 'react-router-dom';

const LINKS: Array<{ to: string; label: string }> = [
  { to: '/', label: 'Commander' },
  { to: '/sessions', label: 'Sessions' },
  { to: '/arsenal', label: 'Arsenal' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/progress', label: 'Progress' },
  { to: '/dev', label: 'Dev' },
];

export function NavBar() {
  return (
    <nav className="navbar" aria-label="Primary">
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.to === '/'}
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
