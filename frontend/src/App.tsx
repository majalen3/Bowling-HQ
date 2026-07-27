import { NavLink, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

import { ArsenalPage } from './pages/ArsenalPage';
import { CommanderPage } from './pages/CommanderPage';
import { GhostBowlerPage } from './pages/GhostBowlerPage';
import { PatternsPage } from './pages/PatternsPage';
import { ProgressPage } from './pages/ProgressPage';
import { TournamentPage } from './pages/TournamentPage';

const NAV_LINKS = [
  { to: '/', label: 'Home / Progress' },
  { to: '/arsenal', label: 'Arsenal DNA' },
  { to: '/commander', label: 'Commander AI' },
  { to: '/patterns', label: 'Patterns' },
  { to: '/tournament', label: 'Tournament Bag' },
  { to: '/ghost-bowler', label: 'Ghost Bowler' },
];

function NavBar() {
  return (
    <nav className="card nav-bar">
      <p className="eyebrow">Bowling-HQ</p>
      <div className="nav-links">
        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' nav-link-active' : ''}`}
          >
            {link.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}

export function App() {
  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/" element={<ProgressPage />} />
        <Route path="/arsenal" element={<ArsenalPage />} />
        <Route path="/commander" element={<CommanderPage />} />
        <Route path="/patterns" element={<PatternsPage />} />
        <Route path="/tournament" element={<TournamentPage />} />
        <Route path="/ghost-bowler" element={<GhostBowlerPage />} />
      </Routes>
    </Router>
  );
}
