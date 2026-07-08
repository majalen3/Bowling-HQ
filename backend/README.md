# Backend

The backend service provides the FastAPI application for Bowling-HQ along with a dependency-free bowling physics baseline used for prediction and planning work.

## Structure

```text
backend/
├── src/
│   ├── main.py              → FastAPI application entry point
│   ├── config.py            → Configuration management
│   ├── database/            → Database connections
│   ├── models/              → API models and schemas
│   ├── routes/              → HTTP endpoints
│   ├── services/            → Application service layer
│   └── tests/               → FastAPI app tests
├── services/
│   └── physics_engine.py    → Bowling physics baseline
├── tests/
│   └── test_physics_engine.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Local development

```bash
cp backend/.env.example backend/.env
pip install -r backend/requirements.txt
uvicorn src.main:app --app-dir backend --reload
```

## Tests

Application tests:

```bash
cd backend
PYTHONPATH=. pytest src/tests
```

Physics baseline regression tests:

```bash
python -m unittest discover -s backend/tests -p 'test_*.py'
```

## Current Physics Baseline

The repository includes `backend/services/physics_engine.py`, a dependency-free baseline for:
- oil pattern difficulty scoring
- ball-path prediction
- pin-action estimation
- condition evolution
- Monte Carlo scenario simulation

## Development

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.
