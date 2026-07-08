# Backend

The backend service provides the FastAPI application for Bowling-HQ.

## Structure

```text
backend/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── tests/
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

```bash
cd backend
pytest src/tests
```
