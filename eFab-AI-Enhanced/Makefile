.PHONY: help install run test clean docker-up docker-down

# Variables
PYTHON := python3
PIP := pip
VENV := venv
API_MODULE := src.api.app:app
UI_MODULE := src/ui/app.py

help: ## Show this help message
	@echo "eFab AI Enhanced - Make Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install --upgrade pip
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	. $(VENV)/bin/activate && $(PIP) install -r requirements-dev.txt

setup-env: ## Setup environment from example
	cp .env.example .env
	@echo "Environment file created. Please update .env with your settings."

run-api: ## Run FastAPI server
	. $(VENV)/bin/activate && uvicorn $(API_MODULE) --reload --port 8000

run-ui: ## Run Streamlit UI
	. $(VENV)/bin/activate && streamlit run $(UI_MODULE)

run-worker: ## Run Celery worker
	. $(VENV)/bin/activate && celery -A src.workers.celery_app worker --loglevel=info

run-beat: ## Run Celery beat scheduler
	. $(VENV)/bin/activate && celery -A src.workers.celery_app beat --loglevel=info

run-flower: ## Run Flower monitoring
	. $(VENV)/bin/activate && celery -A src.workers.celery_app flower

test: ## Run tests
	. $(VENV)/bin/activate && pytest tests/ -v --cov=src --cov-report=html

test-unit: ## Run unit tests only
	. $(VENV)/bin/activate && pytest tests/unit/ -v

test-integration: ## Run integration tests
	. $(VENV)/bin/activate && pytest tests/integration/ -v

lint: ## Run linting
	. $(VENV)/bin/activate && ruff check src/
	. $(VENV)/bin/activate && black --check src/
	. $(VENV)/bin/activate && mypy src/

format: ## Format code
	. $(VENV)/bin/activate && black src/
	. $(VENV)/bin/activate && ruff check --fix src/

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services with Docker
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-clean: ## Clean Docker resources
	docker-compose down -v
	docker system prune -f

db-migrate: ## Run database migrations
	. $(VENV)/bin/activate && alembic upgrade head

db-rollback: ## Rollback last migration
	. $(VENV)/bin/activate && alembic downgrade -1

db-reset: ## Reset database
	. $(VENV)/bin/activate && alembic downgrade base
	. $(VENV)/bin/activate && alembic upgrade head

monitoring: ## Open monitoring dashboards
	@echo "Opening monitoring dashboards..."
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Streamlit UI: http://localhost:8501"
	@echo "Flower: http://localhost:5555"