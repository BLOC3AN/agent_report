.PHONY: help install install-dev test lint format security clean build run docker-build docker-run docker-stop

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  security     - Run security checks"
	@echo "  clean        - Clean up build artifacts"
	@echo "  build        - Build Docker image"
	@echo "  run          - Run the application locally"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker Compose"

# Installation
install:
	pip install -r deployment/requirements.txt

install-dev:
	pip install -r deployment/requirements.txt
	pip install -r requirements-test.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-fast:
	pytest tests/ -x --tb=short

# Code quality
lint:
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports
	bandit -r src/ -f json -o bandit-report.json

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

# Security
security:
	bandit -r src/ -f json -o bandit-report.json
	safety check -r deployment/requirements.txt --json --output safety-report.json

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -f bandit-report.json
	rm -f safety-report.json

# Development
run:
	python main.py

run-dev:
	DEBUG=true LOG_LEVEL=DEBUG python main.py

# Docker
docker-build:
	docker build -f deployment/Dockerfile -t auto-report-agent:latest .

docker-run:
	docker compose -f deployment/docker-compose.yml up -d

docker-stop:
	docker compose -f deployment/docker-compose.yml down

docker-logs:
	docker compose -f deployment/docker-compose.yml logs -f

docker-rebuild:
	docker compose -f deployment/docker-compose.yml down
	docker compose -f deployment/docker-compose.yml up --build -d

# CI/CD helpers
ci-test: install-dev lint test security

ci-build: clean docker-build

# Update dependencies
update-deps:
	pip-compile --upgrade deployment/requirements.in --output-file deployment/requirements.txt
	pip-compile --upgrade requirements-test.in --output-file requirements-test.txt

# Database
db-reset:
	docker compose -f deployment/docker-compose.yml exec mongodb mongosh --eval "db.dropDatabase()"

# Monitoring
logs:
	docker compose -f deployment/docker-compose.yml logs -f agent-report-service

health-check:
	curl -f http://localhost:5000/health || exit 1
