# Contributing to Bowling-HQ

Thanks for your interest in improving Bowling-HQ.

## Local development workflow

1. Copy the environment templates and install dependencies:

   ```bash
   make setup
   ```

2. Start the full local stack:

   ```bash
   make dev
   ```

3. Run quality checks before opening a pull request:

   ```bash
   make lint
   make test
   make build
   ```

## Repository structure

- `backend/` - FastAPI application source, configuration, and backend tests
- `frontend/` - React + TypeScript application source and frontend tests
- `database/` - Local PostgreSQL and MongoDB schema plus seed assets
- `docs/` - Product and feature documentation
- `architecture/` - Architecture notes and system design

## Pull requests

- Keep changes focused and small.
- Avoid committing secrets or local `.env` files.
- Update the relevant documentation when development workflows change.
