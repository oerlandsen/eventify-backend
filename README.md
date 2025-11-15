# Eventify Backend

FastAPI backend application with Docker and Docker Compose support.

## Features

- FastAPI framework
- Pydantic for data validation
- Docker multi-stage builds (dev and prod)
- Docker Compose for easy orchestration
- Makefile for common operations

## Prerequisites

- Docker
- Docker Compose
- Make (optional, but recommended)

## Quick Start

### Development

```bash
make dev
```

This will:
- Build the development Docker image
- Start the development container with hot reload
- Server available at http://localhost:8000
- API documentation at http://localhost:8000/docs

### Production

```bash
make prod
```

This will:
- Build the production Docker image
- Start the production container
- Server available at http://localhost:8001
- API documentation at http://localhost:8001/docs

## Available Make Commands

- `make dev` - Build and start development server
- `make prod` - Build and start production server
- `make dev-up` - Start development container (without building)
- `make prod-up` - Start production container (without building)
- `make dev-down` - Stop development container
- `make prod-down` - Stop production container
- `make down` - Stop all containers
- `make logs-dev` - View development logs
- `make logs-prod` - View production logs
- `make clean` - Remove all containers, networks, and images
- `make dev-shell` - Open shell in development container
- `make prod-shell` - Open shell in production container
- `make help` - Show all available commands

## Manual Docker Commands

If you prefer not to use Make:

### Development
```bash
docker-compose up -d api-dev
```

### Production
```bash
docker-compose up -d api-prod
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `POST /items/` - Create an item (example endpoint)
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── Dockerfile           # Multi-stage Dockerfile
├── docker-compose.yml   # Docker Compose configuration
├── Makefile            # Make commands
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Development

The development stage includes:
- Hot reload enabled
- Volume mounting for live code updates
- Debug-friendly configuration

## Production

The production stage includes:
- Optimized build
- Non-root user for security
- Multiple workers for better performance
- No hot reload

