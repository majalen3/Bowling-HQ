# Bowling-HQ

Bowling-HQ is an AI-powered bowling intelligence platform with production-ready local development scaffolding for FastAPI, React, PostgreSQL, MongoDB, and Redis.

## Quick start

```bash
make setup
make dev
```

Or start the full stack directly with Docker Compose:

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Backend health: http://localhost:8000/health

## Project structure

```text
Bowling-HQ/
├── backend/
│   ├── src/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
├── database/
│   ├── schemas/
│   ├── seeds/
│   └── migrations/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
├── Makefile
├── DEVELOPMENT.md
└── docs/
```

## Development commands

```bash
make help
make lint
make test
make build
make clean
```

For the complete local workflow, see [DEVELOPMENT.md](DEVELOPMENT.md). Product documentation remains in [docs/](docs/).
