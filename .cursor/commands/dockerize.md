---
description: Containerize the application with Docker and Docker Compose
---

# Dockerize Command

Creates production-ready Docker configuration for the current project. Supports local development and prepares for deployment. Adapts to the **shape** of the active stack — a long-running web service, infrastructure-as-code, a CLI/library/batch tool, or a UI-only build — instead of assuming every project is an HTTP server.

## Execution Flow

**1. Context Check**
- Read `.cursor/context.md` to identify the **Active Stack**
- If no stack configured: "⚠️ Run @setup-stack first"
- **Determine the project shape** from the active stack's own definition (`stacks/<name>/context.md` and `stacks/<name>/rules/`), not from guessing off file extensions:
  - **SERVICE**: a long-running process that listens on a network port (e.g. `python-fastapi`, `node-express`, `go-gin`, `java-spring`).
  - **IAC**: infrastructure-as-code (e.g. `devops-terraform`). Any containerization wraps a CLI tool (`terraform`, `tflint`, `checkov`) invoked on demand — not a server that serves traffic.
  - **CLI / LIBRARY / BATCH**: a command-line tool, library, or data/batch job with no listening port.
  - **UI-ONLY**: a static frontend build artifact, served by a generic static file server or CDN — no application-level health endpoint.
  - If the active stack doesn't declare its shape explicitly, ask the user: "What does this project produce — a network service, a CLI/library, an infra-as-code tool, or a static UI build?"

**2. Detect Existing Docker Config**
- Check for existing `Dockerfile`, `docker-compose.yml`
- **If exists**: Ask "Docker config found. Update or regenerate?"
- **If missing**: Proceed to generation

**3. Analyze Application**
- **Entry point / invocation target**: Read the entry-point and manifest conventions from the active stack's own definition (`stacks/<name>/`) rather than assuming a fixed list. Documented examples:
  - Python: `main.py` / `requirements.txt` or `pyproject.toml`
  - Node: `server.ts` / `package.json`
  - Go: `main.go` / `go.mod`
  - Java (Spring): `src/main/java/**/*Application.java` (the `@SpringBootApplication` class) / `pom.xml` or `build.gradle`
  - Terraform (IAC): no app entry point or dependency manifest — root has `*.tf` files with `required_providers`/`required_version`; the "invocation target" is the `terraform` CLI itself
  - If the active stack defines none of the above, ask rather than guess
- **Database**: Check for DB connections in code or existing compose files (only relevant for SERVICE shape)
- **Port**: For SERVICE shape only, detect the configured port (default: 8000). For IAC / CLI / LIBRARY / UI-ONLY shapes, there is no listening port to detect — skip this.

**4. Generate Dockerfile**

Read the Dockerfile convention for the active stack from `stacks/<active-stack>/` (rules or a dedicated docker-template file), and branch by shape:

**If shape == SERVICE**, use the stack's convention. Documented examples for stacks that ship one:

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

**Java (Spring Boot):**
```dockerfile
# Build stage
FROM eclipse-temurin:21-jdk AS builder
WORKDIR /app
COPY . .
RUN ./mvnw -q -DskipTests package

# Runtime stage
FROM eclipse-temurin:21-jre
WORKDIR /app

RUN useradd --create-home --shell /bin/bash app
USER app

COPY --from=builder --chown=app:app /app/target/*.jar app.jar

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

CMD ["java", "-jar", "app.jar"]
```

If the active stack does not define a Dockerfile convention of its own and isn't one of the documented examples above, fall back to a minimal generic multi-stage template driven by the stack's declared build/run commands (read from `.cursor/context.md`'s Architecture Shape / stack rules), and explicitly flag: "⚠️ No Dockerfile convention defined for stack `<name>` — generated a best-effort generic template; review before use."

**If shape == IAC** (e.g. `devops-terraform`): the Dockerfile wraps the CLI, it does not serve traffic. No `EXPOSE`, no HTTP `HEALTHCHECK`.
```dockerfile
FROM hashicorp/terraform:1.9
WORKDIR /workspace

# Optional: bake in companion tooling used by the stack
# RUN apk add --no-cache python3 py3-pip && pip install checkov

COPY . .

HEALTHCHECK --interval=1m --timeout=5s --retries=2 \
  CMD terraform version || exit 1

ENTRYPOINT ["terraform"]
CMD ["--help"]
```

**If shape == CLI / LIBRARY / BATCH**: the Dockerfile wraps the binary/script entrypoint. No `EXPOSE`, no HTTP `HEALTHCHECK` (a lightweight liveness `CMD` is optional, e.g. invoking `--version`, or omit `HEALTHCHECK` entirely for one-shot batch jobs).
```dockerfile
FROM <base-image-for-active-stack-language>
WORKDIR /app
COPY . .
RUN <install-deps-per-active-stack>

ENTRYPOINT ["<binary-or-entry-script>"]
CMD ["--help"]
```

**If shape == UI-ONLY**: multi-stage build that compiles the static assets, then serves them with a generic static server.
```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**5. Generate docker-compose.yml**

- **If shape == SERVICE and a database was detected in Step 3**: generate the app+db(+redis) compose file below.
- **If shape == SERVICE with no database detected**: generate an app-only compose file — drop the `db` service and `DATABASE_URL` entirely. Do not default to Postgres for services with no DB dependency.
- **If shape != SERVICE** (IAC, CLI/LIBRARY/BATCH, UI-ONLY): ask "This project has no long-running network service — skip `docker-compose.yml` and generate only a `Dockerfile`?" Default to Dockerfile-only unless the user wants a compose file (e.g. to orchestrate a Terraform container alongside localstack, or a UI container alongside a mock API).

**Service + database template:**
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

**Service, no database template:**
```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${APP_PORT:-8000}:8000"
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

**IAC template (only if the user wants orchestration, e.g. with localstack):**
```yaml
version: "3.8"

services:
  terraform:
    build:
      context: .
      dockerfile: Dockerfile
    working_dir: /workspace
    volumes:
      - .:/workspace
    env_file:
      - .env
    entrypoint: ["terraform"]
```

**6. Generate .dockerignore**

Always include the language-agnostic entries, then add the stack-conditional block(s) that match the active stack — do not always emit the Python+Node set regardless of stack.

**Always:**
```
.git
.gitignore
.env
.env.*
*.log
.DS_Store
Dockerfile*
docker-compose*
README.md
docs/
.claude/
.cursor/
```

**Python:**
```
__pycache__
*.pyc
*.pyo
.pytest_cache
.coverage
htmlcov/
.venv/
venv/
```

**Node:**
```
node_modules/
```

**Go:**
```
bin/
```

**Java:**
```
target/
*.class
.m2/
.gradle/
build/
```

**Terraform (IAC):**
```
.terraform/
*.tfstate
*.tfstate.backup
*.tfplan
terraform_plans/
```

Tests directories (`tests/`) are excluded only where the stack builds a runtime image that doesn't need them; skip this line if the stack's Docker convention needs test fixtures at build time.

**7. Generate/Update .env.example**

- If a database was detected in Step 3 (SERVICE shape only): include `DATABASE_URL`/`POSTGRES_*`/`REDIS_URL` entries.
- If shape == SERVICE with no database: only `APP_PORT`/`APP_ENV`.
- If shape == IAC (Terraform): note "`.env.example` is likely not applicable — Terraform typically uses `*.tfvars` / `TF_VAR_*` environment variables instead; ask before generating one." If the user still wants one, populate it with `TF_VAR_*` placeholders relevant to the module, not DB/Redis vars.
- If shape == CLI / LIBRARY / BATCH / UI-ONLY: ask whether a `.env.example` is needed at all before generating one; do not assume DB/Redis vars are relevant.

**Service + database example:**
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

**IAC example (only if requested):**
```bash
# Terraform variables (TF_VAR_<name> maps to variable "<name>" in *.tf)
TF_VAR_environment=dev
TF_VAR_region=us-east-1
```

**8. Add Health Endpoint (SERVICE shape only)**

Only applies when shape == SERVICE. Check if `/health` (or the stack's declared healthcheck route) exists. If not, offer to create it:

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

**Java Spring Boot:** Spring Boot Actuator's `/actuator/health` is used by convention (enable `spring-boot-starter-actuator` if not already present) rather than a hand-rolled route.

For IAC, CLI/LIBRARY/BATCH, and UI-ONLY shapes: skip this step entirely — there is no application-level HTTP endpoint to add.

**9. Verify Configuration**

Verification method depends on shape:

**SERVICE:**
```bash
# Build the image
docker compose build

# Start services
docker compose up -d

# Check health
docker compose ps
curl http://localhost:${APP_PORT:-8000}/health
```

**IAC:**
```bash
# Build the image
docker build -t <project>-terraform .

# Verify the CLI is usable
docker run --rm <project>-terraform version
docker run --rm -v "$(pwd)":/workspace <project>-terraform plan
```

**CLI / LIBRARY / BATCH:**
```bash
# Build the image
docker build -t <project> .

# Verify the entrypoint runs
docker run --rm <project> --version
```

**UI-ONLY:**
```bash
# Build the image
docker compose build

# Start the static server
docker compose up -d

# Check it serves
curl -I http://localhost/
```

**10. Output Summary**

Tailor the summary to shape. Examples:

**SERVICE:**
```
✅ Dockerfile created (multi-stage, non-root user)
✅ docker-compose.yml created (app [+ db])
✅ .dockerignore created
✅ .env.example updated

Quick Start:
  docker compose up --build     # Start everything
  docker compose logs -f app    # View logs
  docker compose down           # Stop
  docker compose down -v        # Stop + reset DB (if a db service exists)

Next: Verify with `docker compose up --build`
```

**IAC:**
```
✅ Dockerfile created (wraps `terraform` CLI)
✅ .dockerignore created (.terraform/, *.tfstate, *.tfplan excluded)
✅ docker-compose.yml skipped (no long-running service) — or created if orchestration requested

Quick Start:
  docker build -t <project>-terraform .
  docker run --rm -v "$(pwd)":/workspace <project>-terraform plan

Next: Verify with `docker run --rm <project>-terraform version`
```

**CLI / LIBRARY / BATCH:**
```
✅ Dockerfile created (wraps entrypoint binary/script)
✅ .dockerignore created
✅ docker-compose.yml skipped (no long-running service)

Quick Start:
  docker build -t <project> .
  docker run --rm <project> --help

Next: Verify with `docker run --rm <project> --version`
```

**UI-ONLY:**
```
✅ Dockerfile created (static build → nginx)
✅ docker-compose.yml created (static server)
✅ .dockerignore created

Quick Start:
  docker compose up --build     # Start the static server
  docker compose down           # Stop

Next: Verify with `curl -I http://localhost/`
```

## Usage Examples

### Basic Usage
```
@dockerize
```
→ Detects stack and shape → Generates Dockerfile (+ docker-compose.yml if applicable)

### With Options
```
@dockerize --with-redis
```
→ Includes Redis service in docker-compose.yml (SERVICE shape only)

```
@dockerize --port 3000
```
→ Configures app to run on port 3000 (SERVICE shape only)

### Update Existing
```
@dockerize --update
```
→ Updates existing Docker config without overwriting customizations

## Notes

- Always determine project **shape** (SERVICE / IAC / CLI-LIBRARY-BATCH / UI-ONLY) from the active stack before generating anything — never assume every project is an HTTP server.
- Stack-specific Dockerfile knowledge is read from `stacks/<name>/` first; only fall back to the generic template (with an explicit warning) when the stack defines none.
- Always uses multi-stage builds for smaller images where a build step exists.
- Health checks, `EXPOSE`, and HTTP-based verification apply to SERVICE (and UI-ONLY, via `/`) shapes only — never fabricated for IAC/CLI/LIBRARY/BATCH.
- Uses non-root user in containers where the base image supports it (security best practice).
- Environment variables via `.env` file (never hardcoded) — only generated when relevant to the shape.
- Compatible with both local development and production deployment.
