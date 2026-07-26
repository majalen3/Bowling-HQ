import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Commander from './pages/Commander'
import Arsenal from './pages/Arsenal'
import Patterns from './pages/Patterns'
import Sessions from './pages/Sessions'
import GhostBowler from './pages/GhostBowler'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <Navbar />
        <main className="max-w-6xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/"             element={<Home />} />
            <Route path="/commander"    element={<Commander />} />
            <Route path="/arsenal"      element={<Arsenal />} />
            <Route path="/patterns"     element={<Patterns />} />
            <Route path="/sessions"     element={<Sessions />} />
            <Route path="/ghost-bowler" element={<GhostBowler />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
