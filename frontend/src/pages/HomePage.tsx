import { ServiceStatus } from '../components/ServiceStatus';
import { apiConfig } from '../services/api';

const services = [
  ['Backend API', apiConfig.baseUrl],
  ['Frontend Dev Server', 'http://localhost:5173'],
  ['PostgreSQL', 'postgres:5432'],
  ['MongoDB', 'mongo:27017'],
  ['Redis', 'redis:6379'],
] as const;

export function HomePage() {
  return (
    <main>
      <section>
        <p>Production-ready local development scaffold</p>
        <h1>Bowling-HQ</h1>
        <p>
          The stack is configured for FastAPI, React, PostgreSQL, MongoDB, and Redis with
          Docker-first local development.
        </p>
        <ul>
          {services.map(([label, value]) => (
            <ServiceStatus key={label} label={label} value={value} />
          ))}
        </ul>
      </section>
    </main>
  );
}
