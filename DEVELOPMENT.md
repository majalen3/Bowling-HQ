# Development Setup

## Prerequisites

- Docker with Compose support
- Python 3.11+
- Node.js 20+
- GNU Make

## First-time setup

```bash
make setup
```

## Daily workflow

```bash
make dev
```

or

```bash
docker compose up --build
```

This starts:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- MongoDB: localhost:27017
- Redis: localhost:6379

## Quality checks

```bash
make lint
make test
make build
```

## Database initialization

The PostgreSQL and MongoDB schema files are mounted into their containers and applied automatically on first boot. Re-run them manually with:

```bash
make db-init
```
