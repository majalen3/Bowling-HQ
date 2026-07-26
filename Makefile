# Bowling-HQ Makefile

.PHONY: help setup install dev docker-up docker-down lint test clean db-init db-seed

help:
	@echo "Bowling-HQ Development Commands"
	@echo "================================"
	@echo "make setup          - Set up development environment (first time)"
	@echo "make install        - Install all dependencies"
	@echo "make dev            - Run full stack via Docker (recommended)"
	@echo "make docker-up      - Start Docker containers in background"
	@echo "make docker-down    - Stop Docker containers"
	@echo "make lint           - Run code quality checks"
	@echo "make test           - Run all tests"
	@echo "make db-init        - Apply schema to running postgres container"
	@echo "make db-seed        - Load seed data into running postgres container"
	@echo "make clean          - Clean up generated files"

setup:
	@echo "Setting up Bowling-HQ development environment..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env from .env.example"; fi
	$(MAKE) install
	@echo "✅ Setup complete! Run 'make dev' to start."

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Dependencies installed!"

dev:
	@echo "Starting full stack (Backend: http://localhost:8000 | Frontend: http://localhost:5173)"
	docker compose up --build

docker-up:
	@echo "Starting Docker containers in background..."
	docker compose up -d --build
	@echo "✅ Containers started!"

docker-down:
	@echo "Stopping Docker containers..."
	docker compose down
	@echo "✅ Containers stopped!"

lint:
	@echo "Running linters..."
	cd backend && flake8 . --max-line-length=100
	cd frontend && npm run lint
	@echo "✅ Lint complete!"

test:
	@echo "Running tests..."
	cd backend && pytest
	cd frontend && npm test
	@echo "✅ Tests complete!"

db-init:
	@echo "Applying schema..."
	docker compose exec postgres psql -U postgres -d bowling_hq -f /docker-entrypoint-initdb.d/01_schema.sql
	@echo "✅ Schema applied!"

db-seed:
	@echo "Loading seed data..."
	docker compose exec postgres psql -U postgres -d bowling_hq -f /docker-entrypoint-initdb.d/02_seed.sql
	@echo "✅ Seed data loaded!"

clean:
	@echo "Cleaning up..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf frontend/dist frontend/node_modules/.cache
	@echo "✅ Clean complete!"

.DEFAULT_GOAL := help