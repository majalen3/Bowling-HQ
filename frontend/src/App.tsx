import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { Layout } from './components/Layout';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ArsenalPage } from './pages/ArsenalPage';
import { AuthPage } from './pages/AuthPage';
import { CommanderPage } from './pages/CommanderPage';
import { DevPage } from './pages/DevPage';
import { ProgressPage } from './pages/ProgressPage';
import { SessionsPage } from './pages/SessionsPage';

export function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<CommanderPage />} />
          <Route path="/sessions" element={<SessionsPage />} />
          <Route path="/arsenal" element={<ArsenalPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/dev" element={<DevPage />} />
          <Route path="/auth" element={<AuthPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
