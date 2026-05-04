---
description: Containerize the application with Docker and Docker Compose
---

# Dockerize Command

Creates production-ready Docker configuration for the current project. Supports local development and prepares for deployment.

## Execution Flow

**1. Context Check**
- Read `CLAUDE.md` to identify the **Active Stack**
- If no stack configured: "⚠️ Run /setup-stack first"

**2. Detect Existing Docker Config**
- Check for existing `Dockerfile`, `docker-compose.yml`
- **If exists**: Ask "Docker config found. Update or regenerate?"
- **If missing**: Proceed to generation

**3. Analyze Application**
- **Entry point**: Find main application file (`main.py`, `server.ts`, `main.go`)
- **Dependencies**: Read `requirements.txt`, `package.json`, `go.mod`
- **Database**: Check for DB connections in code or existing compose files
- **Port**: Detect configured port (default: 8000)

**4. Generate Dockerfile**

Based on detected stack, create multi-stage Dockerfile:

**Python (FastAPI/Flask/Django):**
```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy dependencies and app
COPY --from=builder /root/.local /home/app/.local
COPY --chown=app:app . .

ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Node.js (Express/Fastify/NestJS):**
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Runtime stage
FROM node:20-alpine
WORKDIR /app

RUN addgroup -g 1001 -S app && adduser -S -u 1001 app -G app
USER app

COPY --from=builder --chown=app:app /app/node_modules ./node_modules
COPY --chown=app:app . .

ENV NODE_ENV=production
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

**Go (Gin/Echo/Chi):**
```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Runtime stage
FROM alpine:3.18
WORKDIR /app

RUN adduser -D -g '' app
USER app

COPY --from=builder /app/main .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

CMD ["./main"]
```

**5. Generate docker-compose.yml**

Create compose file with detected services:

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${APP_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL:-postgresql://postgres:postgres@db:5432/app}
      - REDIS_URL=${REDIS_URL:-redis://redis:6379}
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-app}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Uncomment if Redis needed:
  # redis:
  #   image: redis:7-alpine
  #   ports:
  #     - "${REDIS_PORT:-6379}:6379"
  #   healthcheck:
  #     test: ["CMD", "redis-cli", "ping"]
  #     interval: 10s
  #     timeout: 5s
  #     retries: 5

volumes:
  postgres_data:
```

**6. Generate .dockerignore**

```
.git
.gitignore
.env
.env.*
__pycache__
*.pyc
*.pyo
.pytest_cache
.coverage
htmlcov/
node_modules/
.venv/
venv/
*.log
.DS_Store
Dockerfile*
docker-compose*
README.md
docs/
tests/
.claude/
.cursor/
```

**7. Generate/Update .env.example**

```bash
# Application
APP_PORT=8000
APP_ENV=development

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app
DB_PORT=5432

# Redis (if used)
# REDIS_URL=redis://redis:6379
# REDIS_PORT=6379
```

**8. Add Health Endpoint (if missing)**

Check if `/health` endpoint exists. If not, offer to create it:

**Python FastAPI:**
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Node Express:**
```typescript
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});
```

**9. Verify Configuration**

Run verification:
```bash
# Build the image
docker compose build

# Start services
docker compose up -d

# Check health
docker compose ps
curl http://localhost:8000/health
```

**10. Output Summary**

```
✅ Dockerfile created (multi-stage, non-root user)
✅ docker-compose.yml created (app + db)
✅ .dockerignore created
✅ .env.example updated

Quick Start:
  docker compose up --build     # Start everything
  docker compose logs -f app    # View logs
  docker compose down           # Stop
  docker compose down -v        # Stop + reset DB

Next: Verify with `docker compose up --build`
```

## Usage Examples

### Basic Usage
```
/dockerize
```
→ Detects stack → Generates Dockerfile + docker-compose.yml

### With Options
```
/dockerize --with-redis
```
→ Includes Redis service in docker-compose.yml

```
/dockerize --port 3000
```
→ Configures app to run on port 3000

### Update Existing
```
/dockerize --update
```
→ Updates existing Docker config without overwriting customizations

## Notes

- Always uses multi-stage builds for smaller images
- Includes health checks for all services
- Uses non-root user in containers (security best practice)
- Environment variables via .env file (never hardcoded)
- Compatible with both local development and production deployment
