# Blog API Reference Solution

**TEACHER ONLY** — Complete working Gin application using GORM.

## Architecture

### Key Technologies
- **Gin**: Fast, minimal Go HTTP web framework
- **PostgreSQL**: Production database (Docker)
- **GORM**: ORM for models, queries, and migrations (AutoMigrate for dev, golang-migrate SQL files for
  production-style teaching)
- **Gin binding tags**: Request validation
- **testify + httptest**: E2E testing

### Structure
```
blog-api/
├── cmd/
│   └── server/
│       └── main.go             # Entrypoint: config, DB, middleware, routes, graceful shutdown
├── internal/
│   ├── config/
│   │   └── config.go           # Environment configuration (viper)
│   ├── database/
│   │   └── database.go         # Connection pooling, AutoMigrate, health ping
│   ├── middleware/
│   │   ├── recovery.go         # Panic recovery -> 500, structured logging
│   │   └── logging.go          # Correlation ID + request logging
│   ├── handler/
│   │   ├── health.go
│   │   ├── auth.go             # Register / Login
│   │   ├── posts.go            # CRUD for posts
│   │   ├── comments.go         # Create / list comments
│   │   └── routes.go           # Route registration
│   ├── model/
│   │   ├── user.go             # GORM model + DTOs
│   │   ├── post.go             # GORM model + DTOs
│   │   └── comment.go          # GORM model + DTOs
│   ├── repository/
│   │   ├── user_repository.go
│   │   ├── post_repository.go
│   │   └── comment_repository.go
│   └── service/
│       ├── user_service.go     # Registration, bcrypt password hashing, login
│       ├── post_service.go     # Post business logic
│       └── comment_service.go  # Comment business logic (verifies parent post exists)
├── migrations/                 # golang-migrate versioned SQL (production-style teaching)
├── tests/
│   ├── helpers_test.go         # Test DB setup, router setup
│   ├── test_api_test.go        # Basic E2E smoke tests
│   ├── test_scenarios_test.go  # Detailed scenario tests with documented input/output
│   └── README.md               # Test documentation
├── docker-compose.yml          # PostgreSQL + pgAdmin
├── Dockerfile                  # Multi-stage build, static binary, non-root user
├── Makefile                    # build/run/test/lint/quality targets
├── go.mod
└── .env.example
```

## Quick Start

### 1. Start Docker Services
```bash
cd examples/blog-api
docker compose up -d
```

This starts:
- PostgreSQL on port 5432
- pgAdmin on port 5050 (http://localhost:5050) — via `docker compose --profile tools up -d`

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults should work)
```

### 3. Install Dependencies
```bash
go mod tidy
```

### 4. Run Application
```bash
go run ./cmd/server
# or
make run
```

Visit:
- **Health Check**: http://localhost:8080/health

Gin has no built-in `/docs` UI — refer to `../../templates/openapi-template.yaml` (adapt it to this
app's exact schema) or serve a static Swagger UI container against it.

### 5. Run Tests
```bash
go test ./tests/... -v
# or
make test
```

## GORM Architecture

### Connection Management
```go
// internal/database/database.go
func Connect(databaseURL string, debug bool) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(databaseURL), &gorm.Config{...})
	// pool tuning: SetMaxOpenConns, SetMaxIdleConns, SetConnMaxLifetime
	return db, err
}
```

### Repository Pattern
```go
// internal/repository/post_repository.go
type GormPostRepository struct {
	db *gorm.DB
}

func (r *GormPostRepository) Create(ctx context.Context, post *model.Post) error {
	if err := r.db.WithContext(ctx).Create(post).Error; err != nil {
		return fmt.Errorf("gorm post repository: create: %w", err)
	}
	return nil
}
```

### Service Layer (Interface-at-Point-of-Use)
```go
// internal/service/post_service.go — interface declared here, consumer side
type PostRepository interface {
	Create(ctx context.Context, post *model.Post) error
	GetByID(ctx context.Context, id string) (*model.Post, error)
	// ...
}

type PostService struct {
	repo PostRepository
}
```

### Handler Layer (Dependency-Injecting Factory Functions)
```go
// internal/handler/posts.go
func CreatePost(svc *service.PostService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.CreatePostRequest
		if err := c.ShouldBindJSON(&req); err != nil { ... }
		post, err := svc.CreatePost(c.Request.Context(), req.Title, req.Content, req.AuthorID)
		c.JSON(http.StatusCreated, model.ToPostResponse(post))
	}
}
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Posts Table
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Comments Table
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Applied automatically via GORM `AutoMigrate` on local dev startup, or via `make migrate-up`
(golang-migrate, see `migrations/`) for production-style teaching.

## API Endpoints

### Authentication
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Login user

### Posts
- `POST /api/posts` — Create blog post
- `GET /api/posts` — List posts (paginated)
- `GET /api/posts/{id}` — Get post by ID
- `PUT /api/posts/{id}` — Update post (partial)
- `DELETE /api/posts/{id}` — Delete post

### Comments
- `POST /api/posts/{id}/comments` — Create comment
- `GET /api/posts/{id}/comments` — List comments

## Testing Strategy

### E2E Tests
All tests use a real PostgreSQL database (same as production), wrapped in a rolled-back transaction
per test for isolation:
- `tests/helpers_test.go` — DB + router setup
- `tests/test_api_test.go` — one smoke test per endpoint
- `tests/test_scenarios_test.go` — detailed scenarios with documented input/output
- `tests/README.md` — complete testing guide

## Key Patterns to Show Students

### 1. GORM with Parameterized Queries (No Raw SQL String Concatenation)
```go
r.db.WithContext(ctx).First(&post, "id = ?", id)
```
**Never build SQL with string formatting — GORM's `?` placeholders prevent injection.**

### 2. Interface-at-Point-of-Use
The `service` package declares the `PostRepository` interface it needs; the `repository` package
doesn't know or care. This makes services trivially mockable in unit tests (see
`templates/chatbot-tests.md` for the equivalent pattern applied to the chatbot domain).

### 3. Layered Types, Not Inheritance
`model.Post` (GORM) vs `model.CreatePostRequest`/`model.PostResponse` (API DTOs) are separate flat
structs — see `vibe/vibe_database.md` for why this replaces Pydantic's Base/Create/Update chain.

### 4. Dependency-Injecting Handler Factories
```go
func endpoint(svc *service.X) gin.HandlerFunc {
    return func(c *gin.Context) { /* uses svc via closure */ }
}
```

### 5. Context Propagation
`c.Request.Context()` flows through every layer down to `db.WithContext(ctx)`.

## Common Issues & Solutions

### Database Connection Errors
```bash
# Check if PostgreSQL is running
docker compose ps

# View PostgreSQL logs
docker compose logs postgres

# Restart services
docker compose restart
```

### Port Already in Use
```bash
# Change PORT in .env file
PORT=8081

# Or stop conflicting process
lsof -ti:8080 | xargs kill -9
```

### Tests Failing
```bash
# Ensure database is running
docker compose ps

# Create the test database if missing
docker compose exec postgres psql -U postgres -c "CREATE DATABASE blog_db_test;"

# Run with verbose output
go test ./tests/... -v

# Run a single test
go test ./tests/... -run TestCreatePostThenRetrieve -v
```

## pgAdmin Access

1. Start it: `docker compose --profile tools up -d`
2. Visit http://localhost:5050
3. Login:
   - Email: admin@blog.com
   - Password: admin
4. Add Server:
   - Host: `postgres` (or `host.docker.internal` on Mac/Windows)
   - Port: 5432
   - Database: blog_db
   - Username: postgres
   - Password: postgres

## Teaching Tips

### Session 1 Demo
1. Show `docker-compose.yml` (PostgreSQL setup)
2. Show `internal/database/database.go` (GORM connection + pooling)
3. Show one complete flow: handler -> service -> repository -> GORM -> Postgres
4. Run one test showing input/output (`test_scenarios_test.go`)
5. Use pgAdmin to show actual database records

### Key Points to Emphasize
- GORM with parameterized queries prevents SQL injection
- Interface-at-point-of-use makes services independently testable
- Separate GORM model and API DTOs keep the database schema from leaking into the API contract
- Service layer contains business logic; handlers only translate HTTP <-> DTO
- Context propagates from the HTTP request all the way to the database call

### Common Student Mistakes
- Building SQL with string concatenation instead of GORM's parameterized query builders
- Returning the GORM model directly as the API response (leaks internal fields, breaks camelCase JSON)
- Declaring repository interfaces in the `repository` package instead of the `service` package
- Forgetting to propagate `context.Context` (`db.WithContext(ctx)`)
- Mixing business logic into handlers

## Next Steps

After understanding this reference:
1. Walk through one endpoint completely
2. Have students trace: Request -> Handler -> Service -> Repository -> GORM -> Response
3. Show how tests validate the flow
4. Let students build a similar endpoint independently (e.g. post tags, or user profile updates)

## Stopping Services

```bash
# Stop but keep data
docker compose stop

# Stop and remove data
docker compose down -v
```
