# Docker Containerization Guide (Go)

This guide covers Docker containerization patterns for Gin/Echo/Chi applications following the vibe coding methodology.

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

- `Dockerfile` - Multi-stage build (compile to static binary)
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

Multi-stage build for Go (smallest possible image):

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o main .

# Runtime stage (minimal)
FROM alpine:3.18
WORKDIR /app

RUN apk --no-cache add ca-certificates
RUN adduser -D -g '' app
USER app

COPY --from=builder /app/main .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

CMD ["./main"]
```

Key features:

- **Static binary**: `CGO_ENABLED=0` for no external dependencies
- **Alpine runtime**: Tiny image (~10MB total)
- **Stripped binary**: `-ldflags="-s -w"` removes debug info
- **CA certificates**: For HTTPS calls

### Even Smaller: Scratch Image

For the absolute smallest image:

```dockerfile
FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/main /main
CMD ["/main"]
```

Note: Scratch has no shell or debugging tools.

### docker-compose.yml

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8080:8080"
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

## Build Flags

### Standard Build

```dockerfile
RUN CGO_ENABLED=0 GOOS=linux go build -o main .
```

### Optimized Build (smaller binary)

```dockerfile
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o main .
```

- `-s`: Omit symbol table
- `-w`: Omit DWARF debugging info

## Common Commands

| Command | What It Does |
|---------|--------------|
| `docker compose up --build` | Build and start all services |
| `docker compose logs -f app` | Follow app logs |
| `docker compose down -v` | Stop and reset database |
| `go build -o main .` | Build locally |

## Development with Hot Reload

For development, use [air](https://github.com/cosmtrek/air):

### Dockerfile.dev

```dockerfile
FROM golang:1.21-alpine
WORKDIR /app
RUN go install github.com/cosmtrek/air@latest
COPY go.mod go.sum ./
RUN go mod download
CMD ["air"]
```

### docker-compose.override.yml

```yaml
services:
  app:
    build:
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
    command: air
```

## Health Endpoint Examples

### Gin

```go
r.GET("/health", func(c *gin.Context) {
    c.JSON(200, gin.H{"status": "healthy"})
})
```

### Echo

```go
e.GET("/health", func(c echo.Context) error {
    return c.JSON(200, map[string]string{"status": "healthy"})
})
```

### Chi

```go
r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"status":"healthy"}`))
})
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "exec format error" | Add `GOOS=linux` to build command |
| "certificate errors" | Add `ca-certificates` in alpine stage |
| "port already in use" | Change port in `.env` or stop other containers |
| "file not found" (scratch) | Ensure binary path is correct |

## Best Practices

1. **Static binary**: Always use `CGO_ENABLED=0`
2. **Alpine or scratch**: Smallest possible runtime
3. **Strip binary**: Use `-ldflags="-s -w"`
4. **CA certificates**: Include for HTTPS
5. **Non-root user**: Security requirement (not in scratch)
6. **Health checks**: Always include them

## Image Size Comparison

| Base Image | Approximate Size |
|------------|------------------|
| golang:1.21 | ~800MB |
| golang:1.21-alpine | ~250MB |
| alpine:3.18 + binary | ~15MB |
| scratch + binary | ~8MB |
