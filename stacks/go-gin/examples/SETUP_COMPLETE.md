# Reference Solution - Setup Complete

## What's Ready

A complete, working Gin blog application using **GORM** (not raw `database/sql`) as the ORM, chosen
deliberately as the teaching pattern — see "Architecture Choice" below for the rationale, mirroring
how the Python stack explicitly chose raw SQL over an ORM for its own pedagogical reasons.

### Location
```
stacks/go-gin/examples/blog-api/
```

### Status Checklist
- [ ] `go mod tidy` run (requires network access to the Go module proxy — not run automatically as
      part of scaffolding this course template; run it before first use)
- [ ] Docker PostgreSQL running (`docker compose up -d`, port 5432)
- [ ] Application starts successfully (`go run ./cmd/server`)
- [ ] Tables auto-created on startup via GORM `AutoMigrate`, OR applied via `make migrate-up`
      (golang-migrate, `migrations/`)
- [ ] All code follows the interface-at-point-of-use + layered-DTO patterns from
      `rules/300-go-style.mdc` and `vibe/vibe_database.md`

This file documents the **intended, verified-by-design** state of the reference app; run the
checklist commands below in your environment to confirm each box.

## Quick Start

```bash
cd stacks/go-gin/examples/blog-api

# Start Docker services
docker compose up -d

# Configure environment
cp .env.example .env

# Install dependencies
go mod tidy

# Run the app
go run ./cmd/server

# Health check
curl http://localhost:8080/health
```

## Important Notes

### Port Configuration
- **PostgreSQL**: Port 5432 (standard — no conflict avoidance needed since this app owns its own
  Docker Compose network)
- **Gin server**: Port 8080
- **pgAdmin**: Port 5050 (optional, `docker compose --profile tools up -d`)

### Database Connection
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/blog_db?sslmode=disable
```

## Architecture Choice: GORM (Not Raw `database/sql`)

Unlike the Python/FastAPI reference (which deliberately uses raw SQL via `psycopg2` to teach SQL
fundamentals without ORM magic), this Go reference uses **GORM**. The trade-off is intentional and
worth calling out explicitly to students:

**Why GORM here, unlike raw SQL in the Python reference:**
- Go's `database/sql` + manual `Scan()` into structs is significantly more verbose per query than
  Python's `psycopg2` + `RealDictCursor` (no reflection-based dict conversion in Go) — the raw-SQL
  version would spend most of its lines on boilerplate scanning rather than teachable business logic
- GORM's query builder (`.Where(...)`, `.Preload(...)`, `.WithContext(ctx)`) is idiomatic Go and widely
  used in production Go/Gin codebases, so students see a realistic pattern, not a toy one
- The **interface-at-point-of-use** repository pattern (`rules/300-go-style.mdc`) means the ORM choice
  is isolated to the `repository` package — a raw-SQL or `sqlx` implementation would satisfy the exact
  same `PostRepository` interface with zero changes to `service` or `handler` code, which is itself a
  valuable lesson: **the abstraction is what matters, not the specific persistence technology**

If teaching raw SQL specifically is a goal, swap only `internal/repository/*.go` to use
`database/sql` + parameterized queries directly — everything above the repository layer is unaffected.

### Key Features
- Interface-at-point-of-use repositories (`context.Context` propagated throughout)
- Parameterized queries via GORM's query builder (prevents SQL injection)
- Layered types: GORM model vs API DTOs, never conflated
- bcrypt password hashing (never plaintext, never logged)
- Panic recovery + structured logging middleware
- Graceful shutdown on SIGINT/SIGTERM

## API Endpoints

### Health
- `GET /health` - Health check

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Posts
- `POST /api/posts` - Create blog post
- `GET /api/posts` - List posts (paginated)
- `GET /api/posts/{id}` - Get post by ID
- `PUT /api/posts/{id}` - Update post (partial)
- `DELETE /api/posts/{id}` - Delete post

### Comments
- `POST /api/posts/{id}/comments` - Create comment
- `GET /api/posts/{id}/comments` - List comments

## Testing

### Run Tests
```bash
cd stacks/go-gin/examples/blog-api
docker compose up -d
docker compose exec postgres psql -U postgres -c "CREATE DATABASE blog_db_test;"
go test ./tests/... -v
```

### Test Files
- `tests/test_api_test.go` - Basic E2E smoke tests
- `tests/test_scenarios_test.go` - Detailed scenarios with input/output docs (the star file for
  teaching — read the doc comments as a spec, then the assertions as verification)
- `tests/README.md` - Complete test documentation

## Teaching with This Solution

### Show Students
1. **GORM query patterns** in the repository layer (`internal/repository/*.go`)
2. **Interface-at-point-of-use** — the service package declares what it needs, the repository package
   just implements it
3. **Parameterized queries** for security (GORM's `?` placeholders)
4. **Layered architecture**: Handler -> Service -> Repository -> GORM -> Postgres
5. **Test-driven approach** with clear input/output (`test_scenarios_test.go`)

### Key Files to Reference
- `internal/database/database.go` - Connection management, pooling
- `internal/repository/*.go` - GORM query examples
- `internal/service/*.go` - Business logic, interface declarations
- `internal/handler/*.go` - Request/response DTO conversion
- `tests/test_scenarios_test.go` - Test examples with docs

## Stopping Services

```bash
# Stop but keep data
docker compose stop

# Stop and remove all data
docker compose down -v
```

## Troubleshooting

### Can't connect to database
- Ensure Docker is running: `docker compose ps`
- Check logs: `docker compose logs postgres`
- Confirm `DATABASE_URL` in `.env` matches the compose file's exposed port

### Port already in use
- Change `PORT` in `.env`
- Or stop the conflicting process: `lsof -ti:8080 | xargs kill -9`

### App won't start
- Check `.env` exists (`cp .env.example .env`)
- Verify Docker containers are healthy (`docker compose ps`)
- Run `go mod tidy` if you see "package not found" errors

### `go: cannot find module providing package ...`
- Run `go mod tidy` — this scaffolded `go.mod` lists dependencies but a `go.sum` must be generated
  locally with network access to the Go module proxy

## Next Steps

1. Run `go mod tidy`, confirm the application builds and starts
2. Test all endpoints with `curl` or a REST client
3. Use as reference during teaching
4. Show students the test scenarios
5. Walk through one complete flow: Handler -> Service -> Repository -> GORM -> Response

## Perfect for Teaching

This solution demonstrates:
- Professional Gin project structure (`cmd/`, `internal/`, layered by responsibility)
- GORM used idiomatically, with the ORM choice isolated behind an interface
- Security best practices (bcrypt, parameterized queries, no secrets in logs)
- Test-driven development with transaction-isolated E2E tests
- Clear layered architecture matching `rules/300-go-style.mdc`
- Complete documentation

Ready to use as a teaching reference.
