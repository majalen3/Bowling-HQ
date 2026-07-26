import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Arsenal from './pages/Arsenal'
import Dashboard from './pages/Dashboard'
import Patterns from './pages/Patterns'
import Recommendations from './pages/Recommendations'
import Sessions from './pages/Sessions'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="arsenal" element={<Arsenal />} />
            <Route path="patterns" element={<Patterns />} />
            <Route path="sessions" element={<Sessions />} />
            <Route path="recommendations" element={<Recommendations />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
