# Backend Directory

This directory contains all Python/FastAPI code for the Bowling-HQ API server.

## Structure

```
backend/
├── main.py              → FastAPI application entry point
├── requirements.txt     → Python dependencies
├── .env.example        → Environment variables template
├── config.py           → Configuration management
├── services/           → Business logic (engines)
│   ├── commander_engine.py
│   ├── ghost_engine.py
│   ├── pattern_engine.py
│   ├── maxwell_engine.py
│   └── session_engine.py
├── models/             → Data models and schemas
│   ├── ball.py
│   ├── pattern.py
│   ├── session.py
│   └── recommendation.py
├── routes/             → API endpoints
│   ├── commander.py
│   ├── arsenal.py
│   ├── patterns.py
│   ├── sessions.py
│   └── ghost_bowler.py
├── database/           → Database connections
│   ├── postgres.py
│   ├── mongodb.py
│   └── redis.py
└── tests/              → Unit and integration tests
    ├── test_commander.py
    ├── test_ghost_bowler.py
    └── test_patterns.py
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run the server
uvicorn main:app --reload
```

## Tech Stack

- **Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Database**: PostgreSQL, MongoDB, Redis
- **Language**: Python 3.11+

## Development

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.