.PHONY: help dev prod dev-build prod-build dev-up prod-up dev-down prod-down down logs-dev logs-prod clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev-build: ## Build development Docker image
	docker-compose build api-dev

prod-build: ## Build production Docker image
	docker-compose build api-prod

dev-up: ## Start development container
	docker-compose up -d api-dev

prod-up: ## Start production container
	docker-compose up -d api-prod

dev: dev-build dev-up ## Build and start development container
	@echo "Development server running at http://localhost:8000"
	@echo "API docs available at http://localhost:8000/docs"

prod: prod-build prod-up ## Build and start production container
	@echo "Production server running at http://localhost:8001"
	@echo "API docs available at http://localhost:8001/docs"

dev-down: ## Stop development container
	docker-compose stop api-dev
	docker-compose rm -f api-dev

prod-down: ## Stop production container
	docker-compose stop api-prod
	docker-compose rm -f api-prod

down: ## Stop all containers
	docker-compose down

logs-dev: ## View development container logs
	docker-compose logs -f api-dev

logs-prod: ## View production container logs
	docker-compose logs -f api-prod

clean: ## Remove all containers, networks, and images
	docker-compose down -v --rmi all

dev-shell: ## Open shell in development container
	docker-compose exec api-dev /bin/bash

prod-shell: ## Open shell in production container
	docker-compose exec api-prod /bin/bash

