# Docker Containerization Guide (Node.js)

This guide covers Docker containerization patterns for Express/Fastify/NestJS applications following the vibe coding methodology.

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

## File Overview

### Dockerfile

Multi-stage build pattern for Node.js:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Runtime
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

Key features:

- **Alpine base**: Small image size
- **Non-root user**: Security best practice
- **Health check**: Using wget (available in alpine)
- **NODE_ENV=production**: Proper production mode

### docker-compose.yml

Local development setup:

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app
      - /app/node_modules  # Preserve container node_modules

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

## Common Commands

| Command | What It Does |
|---------|--------------|
| `docker compose up --build` | Build and start all services |
| `docker compose up -d` | Start in background |
| `docker compose logs -f app` | Follow app logs |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop and reset volumes (DB) |
| `docker compose exec app /bin/sh` | Shell into container |

## Development vs Production

### Development (with hot reload)

```yaml
volumes:
  - .:/app
  - /app/node_modules  # Important: preserve container modules
command: npm run dev
```

### Production

```yaml
# No volume mount - use built image
command: node dist/server.js
```

## Package Manager Variants

### npm

```dockerfile
COPY package*.json ./
RUN npm ci --only=production
```

### yarn

```dockerfile
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile --production
```

### pnpm

```dockerfile
RUN npm install -g pnpm
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Port already in use" | Change port in `.env` or stop other containers |
| "Module not found" | Run `docker compose build --no-cache app` |
| "node_modules conflicts" | Add `/app/node_modules` to volumes |
| "Permission denied" | Check USER directive in Dockerfile |

## Best Practices

1. **Use alpine images**: `node:20-alpine` for smaller size
2. **Multi-stage builds**: Separate build and runtime
3. **Preserve node_modules**: Use anonymous volume in development
4. **Non-root user**: Security requirement
5. **Health checks**: Always include them
6. **.dockerignore**: Exclude node_modules, .git, tests
