# Bowling-HQ

Bowling-HQ is an AI-powered bowling intelligence platform with production-ready local development scaffolding for FastAPI, React, PostgreSQL, MongoDB, and Redis.

## Open the app

**Easiest — runs in the cloud, no install needed:**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/majalen3/Bowling-HQ)

Click the button above. GitHub will start a cloud environment, launch the full stack automatically, and open the frontend for you. Works from any browser including iPhone Safari.

**Deploy permanently to the cloud:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.com/new/template?template=https://github.com/majalen3/Bowling-HQ)

Click to deploy the app to Railway (free tier available). Once deployed, you get a permanent public URL you can bookmark and open from any device.

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
