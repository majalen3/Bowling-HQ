# Bowling-HQ

Bowling-HQ is an AI-powered bowling intelligence platform with production-ready local development scaffolding for FastAPI, React, PostgreSQL, MongoDB, and Redis.

## 🎳 Open the App

### → [Deploy to Render (free, permanent URL)](https://render.com/deploy?repo=https://github.com/majalen3/Bowling-HQ)

Click the link above → sign in with GitHub → click **Apply** → wait ~3 minutes → Render gives you a permanent URL you can bookmark and open from any device including iPhone. Free, no credit card needed.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/majalen3/Bowling-HQ)

---

**Or open temporarily in GitHub Codespaces (no account needed beyond GitHub):**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/majalen3/Bowling-HQ)

---

## Quick start (local)

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
