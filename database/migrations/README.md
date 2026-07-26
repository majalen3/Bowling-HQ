# Migrations

Database migrations will be managed here using Alembic once the backend models are implemented.

## Getting Started

```bash
# Initialize Alembic (run once)
cd backend && alembic init alembic

# Create a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```
