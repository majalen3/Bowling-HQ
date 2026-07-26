# Bowling-HQ Makefile

.PHONY: help setup dev docker-up docker-down docker-build docker-logs lint test clean db-init

help:
	@echo "Bowling-HQ Development Commands"
	@echo "================================"
	@echo "make setup          - First-time setup (copy .env, build images)"
	@echo "make dev            - Start full stack with docker-compose"
	@echo "make docker-up      - Start containers in background"
	@echo "make docker-down    - Stop containers"
	@echo "make docker-build   - Rebuild all images"
	@echo "make docker-logs    - Tail all container logs"
	@echo "make lint           - Run backend linter"
	@echo "make test           - Run backend tests"
	@echo "make clean          - Remove build artifacts"

setup:
	@echo "Setting up Bowling-HQ development environment..."
	@test -f .env || cp .env.example .env
	docker-compose build
	@echo ""
	@echo "✅ Setup complete! Run 'make dev' to start."
	@echo "   Backend:  http://localhost:8000"
	@echo "   API docs: http://localhost:8000/docs"
	@echo "   Frontend: http://localhost:5173"

dev:
	@echo "Starting Bowling-HQ stack..."
	docker-compose up

docker-up:
	docker-compose up -d
	@echo "✅ Stack running in background."
	@echo "   Backend:  http://localhost:8000"
	@echo "   API docs: http://localhost:8000/docs"
	@echo "   Frontend: http://localhost:5173"

docker-down:
	docker-compose down
	@echo "✅ Containers stopped."

docker-build:
	docker-compose build --no-cache
	@echo "✅ Images rebuilt."

docker-logs:
	docker-compose logs -f

lint:
	@echo "Running backend linter..."
	cd backend && pip install flake8 --quiet && flake8 . --max-line-length=100 --exclude=__pycache__
	@echo "✅ Lint complete."

test:
	@echo "Running backend tests..."
	cd backend && pip install pytest --quiet && pytest -v || true
	@echo "✅ Test run complete."

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf dist/ build/ *.egg-info
	@echo "✅ Clean complete."

.DEFAULT_GOAL := help