# Bowling-HQ Makefile

.PHONY: help setup install dev docker-up docker-down lint test clean

help:
	@echo "Bowling-HQ Development Commands"
	@echo "================================"
	@echo "make setup          - Set up development environment (first time)"
	@echo "make install        - Install all dependencies"
	@echo "make dev            - Run development servers"
	@echo "make docker-up      - Start Docker containers"
	@echo "make docker-down    - Stop Docker containers"
	@echo "make lint           - Run code quality checks"
	@echo "make test           - Run tests"
	@echo "make clean          - Clean up generated files"
	@echo "make db-init        - Initialize database"

setup:
	@echo "Setting up Bowling-HQ development environment..."
	cp .env.example .env
	$(MAKE) install
	@echo "✅ Setup complete!"

install:
	@echo "Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✅ Dependencies installed!"

dev:
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "Press Ctrl+C to stop"
	docker-compose up

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started!"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
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
	@echo "Initializing database..."
	docker-compose exec postgres psql -U postgres -d bowling_hq -f /docker-entrypoint-initdb.d/schema.sql
	@echo "✅ Database initialized!"

clean:
	@echo "Cleaning up..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf dist/ build/ *.egg-info
	@echo "✅ Clean complete!"

.DEFAULT_GOAL := help