# Docker Containerization Guide

This guide covers Docker containerization patterns for FastAPI applications following the vibe coding methodology.

## Why Docker?

1. **Reproducible Environments**: "Works on my machine" becomes "works everywhere"
2. **Local Dev Mirrors Production**: Same container runs locally and in production
3. **Isolation**: Dependencies don't conflict between projects
4. **Easy Onboarding**: New developers run `docker compose up` and they're ready

## Quick Start

### Generate Docker Config

Run the `/dockerize` command:

```
/dockerize
```

This creates:
- `Dockerfile` - Multi-stage build for your app
- `docker-compose.yml` - Local dev with app + database
- `.dockerignore` - Excludes unnecessary files
- `.env.example` - Environment variable template
- `/health` endpoint (if missing)

### Run Your App

```bash
# Start everything
docker compose up --build

# View logs
docker compose logs -f app

# Stop
docker compose down

# Reset database
docker compose down -v
```

## Phase Integration

### Phase 0 (Skeleton)

Docker is part of the skeleton. After scaffolding:

1. Run `/dockerize` to generate config
2. Verify `docker compose up` works
3. Check health endpoint responds

### Phase 1+ (Implementation)

- Update `requirements.txt` → rebuild image
- Add new services (Redis, etc.) → update docker-compose.yml
- Test in container before committing

## File Overview

### Dockerfile

Multi-stage build pattern:

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /home/app/.local
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Key features:
- **Multi-stage**: Smaller final image
- **Non-root user**: Security best practice
- **Health check**: Container health monitoring
- **PYTHONUNBUFFERED=1**: Proper logging

### docker-compose.yml

Local development setup:

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]

volumes:
  postgres_data:
```

Key features:
- **Health-based depends_on**: App waits for DB
- **Named volumes**: Data persists across restarts
- **Environment variables**: No hardcoded secrets

### .dockerignore

Excludes from build context:

```
.git
.env
__pycache__
.venv
tests/
.claude/
```

Why it matters:
- Faster builds
- Smaller images
- No secrets in image

## Common Commands

| Command | What It Does |
|---------|--------------|
| `docker compose up --build` | Build and start all services |
| `docker compose up -d` | Start in background |
| `docker compose logs -f app` | Follow app logs |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop and reset volumes (DB) |
| `docker compose exec app /bin/sh` | Shell into container |
| `docker compose build --no-cache` | Force rebuild |

## Troubleshooting

### "Port already in use"

```bash
# Find what's using the port
lsof -i :8000

# Or change port in .env
APP_PORT=8001
```

### "Database connection refused"

1. Check DB is healthy: `docker compose ps`
2. Check DATABASE_URL matches docker-compose service name
3. Reset: `docker compose down -v && docker compose up --build`

### "Module not found" after adding dependency

```bash
# Rebuild the image
docker compose build --no-cache app
docker compose up
```

### "Permission denied" errors

Ensure Dockerfile creates non-root user:

```dockerfile
RUN useradd --create-home app
USER app
```

## Development vs Production

### Local Development

```yaml
# Mount source for hot reload
volumes:
  - .:/app
command: uvicorn main:app --reload
```

### Production

```yaml
# No volume mount - use built image
# No --reload flag
command: uvicorn main:app --workers 4
```

## Adding Services

### Redis

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
```

### Celery Worker

```yaml
services:
  worker:
    build: .
    command: celery -A app.tasks worker
    depends_on:
      - redis
      - db
```

## Best Practices

1. **Pin versions**: `python:3.11-slim`, not `python:latest`
2. **Multi-stage builds**: Keep production images small
3. **Health checks**: Always include them
4. **Non-root user**: Security requirement
5. **No secrets in Dockerfile**: Use env vars
6. **.dockerignore**: Exclude tests, docs, .git
7. **Named volumes**: For persistent data

## Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
