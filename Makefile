SHELL := /bin/bash
COMPOSE := docker compose
BACKEND_DIR := $(CURDIR)/backend
FRONTEND_DIR := $(CURDIR)/frontend

.PHONY: help setup install dev build test lint clean db-init

help:
	@echo "Bowling-HQ development commands"
	@echo "  make setup   - Create local env files and install dependencies"
	@echo "  make install - Install backend and frontend dependencies"
	@echo "  make dev     - Start the full local stack with Docker Compose"
	@echo "  make build   - Build backend and frontend Docker images"
	@echo "  make test    - Run backend and frontend tests"
	@echo "  make lint    - Run backend and frontend linters"
	@echo "  make clean   - Stop containers and remove local caches"
	@echo "  make db-init - Apply database schema files to running containers"

setup:
	@test -f .env || cp .env.example .env
	@test -f backend/.env || cp backend/.env.example backend/.env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	$(MAKE) install

install:
	python -m pip install -r $(BACKEND_DIR)/requirements.txt
	cd $(FRONTEND_DIR) && npm install

dev:
	$(COMPOSE) up --build

build:
	$(COMPOSE) build backend frontend

test:
	cd $(BACKEND_DIR) && pytest src/tests
	cd $(FRONTEND_DIR) && npm test

lint:
	cd $(BACKEND_DIR) && flake8 src
	cd $(FRONTEND_DIR) && npm run lint

db-init:
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-bowling_hq} -f /docker-entrypoint-initdb.d/postgres.sql
	$(COMPOSE) exec mongo mongosh mongodb://$${MONGO_INITDB_ROOT_USERNAME:-mongo}:$${MONGO_INITDB_ROOT_PASSWORD:-mongo_password}@localhost:27017/$${MONGO_DB:-bowling_hq}?authSource=admin /docker-entrypoint-initdb.d/mongodb.js

clean:
	$(COMPOSE) down -v --remove-orphans
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name node_modules -o -name coverage \) -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '.coverage' \) -delete
