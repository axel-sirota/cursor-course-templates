# Database Management Vibe Coding Guide (Go + GORM)

## Purpose & Scope

This guide provides rules, patterns, and instructions for AI coding assistants (Claude Code, Cursor,
etc.) working on database-related tasks in Go/Gin projects using GORM with the Repository Pattern.
Reference this document when implementing GORM models, repositories, services, or migration tasks.

**Related Documents:**
- [Gin Boilerplate Guide](vibe_gin_boilerplate.md) - For project structure and DTO conventions
- [Go Style Rules](../rules/300-go-style.mdc) - For interface-at-point-of-use and error wrapping idioms

**When to use this guide:**
- Creating GORM models and repositories from migrations
- Implementing CRUD operations for database tables
- Working with PostgreSQL schemas
- Managing database migrations across environments
- Creating services that use multiple repositories

## Project Architecture Quick Reference

### Core Principles
1. **Repository Pattern**: Each aggregate has its own repository type with CRUD operations
2. **Layered Types, Not Inheritance**: GORM model (DB) and API DTOs (request/response) are separate,
   flat structs — Go has no Pydantic-style `Base -> Full -> Create/Update` inheritance chain
3. **Service Layer**: Complex operations and cross-table logic live in services, not repositories
4. **Interface-at-Point-of-Use**: Repository interfaces are declared in the `service` package that
   consumes them, not in the `repository` package that implements them
5. **Migration-Driven**: Schema changes are managed through `golang-migrate` (production-grade) or
   GORM `AutoMigrate` (fast, course/prototype-grade) — pick one per project and stay consistent
6. **Centralized `*gorm.DB`**: A single connection pool, opened once at startup, injected into every
   repository via constructor

### Environment Structure (golang-migrate option)
```
migrations/
├── 000001_create_users_table.up.sql
├── 000001_create_users_table.down.sql
├── 000002_create_posts_table.up.sql
└── 000002_create_posts_table.down.sql
```

### Module Directory Structure
```
internal/
├── model/
│   └── post.go              # GORM model + API DTOs + converter functions
├── repository/
│   └── post_repository.go   # Concrete GORM implementation, no interface declared here
└── service/
    ├── post_service.go       # Interface declared here (consumer side) + business logic
    └── post_service_test.go  # Unit tests with mocked repository
```

### The Two-Struct Model (replaces Pydantic's Base/Full/Create/Update)

```
model/post.go structure:
├── Post                   # GORM model — DB layer, struct tags, json:"-" to prevent API leakage
├── CreatePostRequest       # API request DTO — json + binding tags
├── UpdatePostRequest       # API request DTO — pointer fields for partial updates
└── PostResponse            # API response DTO — json tags, camelCase keys
    + ToPostResponse(p *Post) PostResponse   # explicit converter function
```

### Benefits of This Layering
1. **Type Safety**: Each struct has exactly the fields relevant to its role
2. **Clear Separation**: DB concerns (GORM tags) never leak into JSON, and vice versa
3. **Flexibility**: Different structs for create vs update (e.g. `UpdatePostRequest` uses pointer
   fields so "not provided" and "explicitly set to zero value" are distinguishable)
4. **Explicit Conversion**: `ToPostResponse()` makes the DB->API boundary a visible, testable function
   instead of an implicit serialization rule
5. **Centralized `*gorm.DB`**: A single pool reduces connection overhead and simplifies transactions

### Data Flow Pattern
```
Gin Handler -> Service -> Repository -> gorm.DB -> PostgreSQL
     |            |            |
  Request DTO  Service Input  GORM Model
     ^            ^            ^
Response DTO <- Service <- Repository <- PostgreSQL
```

**Key Flow:**
1. **Handler** binds the camelCase JSON request into a Request DTO
2. **Handler** converts the DTO into whatever input shape the service expects
3. **Service** applies business rules, calls the repository with a GORM model
4. **Repository** persists/reads via `*gorm.DB`, returns GORM models or errors
5. **Service** returns the GORM model (or a service-level result type) to the handler
6. **Handler** converts the GORM model to a Response DTO via `ToXResponse()`

## Mandatory Rules

### 1. Repository Access Control
- **NEVER** call a repository directly from a handler — always go through a service
- **ALWAYS** declare the repository interface in the `service` package (consumer side)
- **ALWAYS** return GORM model pointers or errors from repository methods, never raw `map[string]any`

### 2. Struct Definition
- **ALWAYS** use separate, flat structs: GORM model vs Request DTO(s) vs Response DTO
- **ALWAYS** tag GORM models with `json:"-"` (or omit `json` tags entirely) so they can never
  accidentally serialize as an API response
- **ALWAYS** tag DTOs with `json:"camelCaseName"` to match the OpenAPI contract
- **ALWAYS** use Gin `binding:"..."` tags on Request DTOs for structural validation
- **NEVER** use a GORM model as a `c.JSON()` response body directly

### 3. Repository Implementation
- **ALWAYS** implement only the CRUD methods actually needed by the current session (YAGNI)
- **ALWAYS** accept `context.Context` as the first parameter and use `db.WithContext(ctx)`
- **ALWAYS** wrap errors with `fmt.Errorf("...: %w", err)` for context
- **NEVER** perform business-rule validation in the repository — that's the service's job
- **ALWAYS** use the injected `*gorm.DB`, never open a new connection per repository

### 4. Migration Management
- **ALWAYS** create migrations with `golang-migrate` for anything beyond a course prototype
- **ALWAYS** pair every `.up.sql` with a `.down.sql`
- **ALWAYS** test migrations locally before considering a phase complete
- **NEVER** hand-edit an already-applied migration file — create a new one instead

### 5. Testing Strategy
- **NEVER** unit test repositories directly (they're thin GORM wrappers) — exercise them via E2E tests
- **ALWAYS** unit test services with a mocked repository (`testify/mock` or a hand-written fake)
- **ALWAYS** test business logic, error handling, and DTO<->model conversions in services

## Task Implementation Guide

### Create Model and Repository from Migration

**Command**: "Based on `<link to migration file>` create model and repository for `{table_name}`"

**Implementation Steps:**

1. **Analyze the migration file** to understand the table structure:
```sql
-- migrations/000001_create_users_table.up.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

2. **Create the GORM model + DTOs** in `internal/model/user.go`:
```go
package model

import "time"

// User is the GORM model representing the users table.
type User struct {
	ID        string    `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
	Email     string    `gorm:"uniqueIndex;not null"`
	FullName  string    `gorm:"not null"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

// TableName pins the table name explicitly (GORM would otherwise pluralize "User" to "users" anyway,
// but being explicit avoids surprises).
func (User) TableName() string { return "users" }

// CreateUserRequest is the API request body for user registration.
type CreateUserRequest struct {
	Email    string `json:"email" binding:"required,email"`
	FullName string `json:"fullName" binding:"required"`
}

// UserResponse is the API response body representing a user.
type UserResponse struct {
	UserID    string `json:"userId"`
	Email     string `json:"email"`
	FullName  string `json:"fullName"`
	CreatedAt string `json:"createdAt"`
}

// ToUserResponse converts a GORM User model to its API response DTO.
func ToUserResponse(u *User) UserResponse {
	return UserResponse{
		UserID:    u.ID,
		Email:     u.Email,
		FullName:  u.FullName,
		CreatedAt: u.CreatedAt.Format(time.RFC3339),
	}
}
```

3. **Create the repository** in `internal/repository/user_repository.go`:
```go
package repository

import (
	"context"
	"fmt"

	"gorm.io/gorm"

	"github.com/example/my_project/internal/model"
)

// GormUserRepository is the GORM-backed implementation of user persistence.
type GormUserRepository struct {
	db *gorm.DB
}

// NewGormUserRepository constructs a GormUserRepository with the given connection.
func NewGormUserRepository(db *gorm.DB) *GormUserRepository {
	return &GormUserRepository{db: db}
}

// Create persists a new user.
func (r *GormUserRepository) Create(ctx context.Context, user *model.User) error {
	if err := r.db.WithContext(ctx).Create(user).Error; err != nil {
		return fmt.Errorf("gorm user repository: create: %w", err)
	}
	return nil
}

// GetByEmail returns the user with the given email, or gorm.ErrRecordNotFound wrapped.
func (r *GormUserRepository) GetByEmail(ctx context.Context, email string) (*model.User, error) {
	var user model.User
	if err := r.db.WithContext(ctx).First(&user, "email = ?", email).Error; err != nil {
		return nil, fmt.Errorf("gorm user repository: get by email: %w", err)
	}
	return &user, nil
}
```

4. **Declare the interface in the consuming service** — `internal/service/user_service.go`:
```go
package service

import "context"

// UserRepository is the persistence contract this service depends on.
// Declared here (consumer side), not in the repository package.
type UserRepository interface {
	Create(ctx context.Context, user *model.User) error
	GetByEmail(ctx context.Context, email string) (*model.User, error)
}

type UserService struct {
	repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
	return &UserService{repo: repo}
}
```

`*repository.GormUserRepository` satisfies `service.UserRepository` implicitly — no explicit
`implements` declaration is needed in Go.

### Find and Use an Existing Model

**Command**: "Use `{ModelName}` model to get `{ModelName}` objects"

**Implementation Steps:**

1. **Search for the existing model**:
```bash
grep -rn "type ModelName struct" internal/model/
```

2. **Check whether a service already exists** for it:
```bash
grep -rln "ModelName" internal/service/
```

3. **If a service exists**, use it directly:
```go
svc := service.NewUserService(repo)
user, err := svc.GetUserByEmail(ctx, email)
```

4. **If no service exists**, propose creating one following the pattern above.

## Code Templates

### GORM Model + DTO Template
```go
package model

import "time"

// {ModelName} is the GORM model representing the {table_name} table.
type {ModelName} struct {
	ID        string    `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
	Name      string    `gorm:"not null"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

func ({ModelName}) TableName() string { return "{table_name}" }

// Create{ModelName}Request is the API request body for creating a {model_name}.
type Create{ModelName}Request struct {
	Name string `json:"name" binding:"required,min=1,max=200"`
}

// {ModelName}Response is the API response body representing a {model_name}.
type {ModelName}Response struct {
	{ModelName}ID string `json:"{modelNameCamel}Id"`
	Name          string `json:"name"`
	CreatedAt     string `json:"createdAt"`
}

// To{ModelName}Response converts a GORM {ModelName} model to its API response DTO.
func To{ModelName}Response(m *{ModelName}) {ModelName}Response {
	return {ModelName}Response{
		{ModelName}ID: m.ID,
		Name:          m.Name,
		CreatedAt:     m.CreatedAt.Format(time.RFC3339),
	}
}
```

### Repository Template
```go
package repository

import (
	"context"
	"fmt"

	"gorm.io/gorm"

	"github.com/example/my_project/internal/model"
)

type Gorm{ModelName}Repository struct {
	db *gorm.DB
}

func NewGorm{ModelName}Repository(db *gorm.DB) *Gorm{ModelName}Repository {
	return &Gorm{ModelName}Repository{db: db}
}

func (r *Gorm{ModelName}Repository) Create(ctx context.Context, m *model.{ModelName}) error {
	if err := r.db.WithContext(ctx).Create(m).Error; err != nil {
		return fmt.Errorf("gorm {model_name} repository: create: %w", err)
	}
	return nil
}

func (r *Gorm{ModelName}Repository) GetByID(ctx context.Context, id string) (*model.{ModelName}, error) {
	var m model.{ModelName}
	if err := r.db.WithContext(ctx).First(&m, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("gorm {model_name} repository: get by id: %w", err)
	}
	return &m, nil
}

func (r *Gorm{ModelName}Repository) List(ctx context.Context, limit, offset int) ([]model.{ModelName}, error) {
	var items []model.{ModelName}
	if err := r.db.WithContext(ctx).Limit(limit).Offset(offset).Find(&items).Error; err != nil {
		return nil, fmt.Errorf("gorm {model_name} repository: list: %w", err)
	}
	return items, nil
}

func (r *Gorm{ModelName}Repository) Update(ctx context.Context, m *model.{ModelName}) error {
	if err := r.db.WithContext(ctx).Save(m).Error; err != nil {
		return fmt.Errorf("gorm {model_name} repository: update: %w", err)
	}
	return nil
}

func (r *Gorm{ModelName}Repository) Delete(ctx context.Context, id string) error {
	if err := r.db.WithContext(ctx).Delete(&model.{ModelName}{}, "id = ?", id).Error; err != nil {
		return fmt.Errorf("gorm {model_name} repository: delete: %w", err)
	}
	return nil
}
```

### Service Template
```go
package service

import (
	"context"
	"fmt"

	"github.com/example/my_project/internal/model"
)

// {ModelName}Repository is the persistence contract this service depends on.
type {ModelName}Repository interface {
	Create(ctx context.Context, m *model.{ModelName}) error
	GetByID(ctx context.Context, id string) (*model.{ModelName}, error)
	List(ctx context.Context, limit, offset int) ([]model.{ModelName}, error)
}

// {ModelName}Service contains business logic for {model_name} operations.
type {ModelName}Service struct {
	repo {ModelName}Repository
}

// New{ModelName}Service constructs a {ModelName}Service with the given repository.
func New{ModelName}Service(repo {ModelName}Repository) *{ModelName}Service {
	return &{ModelName}Service{repo: repo}
}

// Create{ModelName} validates and persists a new {model_name}.
func (s *{ModelName}Service) Create{ModelName}(ctx context.Context, name string) (*model.{ModelName}, error) {
	m := &model.{ModelName}{Name: name}
	if err := s.repo.Create(ctx, m); err != nil {
		return nil, fmt.Errorf("{model_name} service: create: %w", err)
	}
	return m, nil
}

// Get{ModelName}ByID retrieves a {model_name} by its ID.
func (s *{ModelName}Service) Get{ModelName}ByID(ctx context.Context, id string) (*model.{ModelName}, error) {
	m, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("{model_name} service: get by id: %w", err)
	}
	return m, nil
}
```

### GORM Model vs API DTO — Side by Side

**CRITICAL**: A GORM model and its API DTOs serve different purposes and must be kept separate:

**GORM Model** (in `internal/model/`):
- Represents the database table structure
- Struct tags describe DB column mapping (`gorm:"..."`), not JSON
- Includes DB-specific fields (`ID`, `CreatedAt`, `UpdatedAt`)
- NEVER returned directly from a handler

**API DTOs** (in `internal/model/`, same package but distinct structs):
- Represent API request/response structure
- `json:"camelCase"` tags matching the OpenAPI contract
- May include computed fields, nested objects, or aggregated data
- Include `binding:"..."` validation tags (on request DTOs)

```go
// GORM model — internal/model/user.go
type User struct {
	ID       string `gorm:"type:uuid;primaryKey"`
	Email    string `gorm:"uniqueIndex"`
	FullName string
}

// API request DTO
type UserRequest struct {
	Email    string `json:"email" binding:"required,email"`
	FullName string `json:"fullName" binding:"required"`
}

// API response DTO
type UserResponse struct {
	UserID   string `json:"userId"`
	Email    string `json:"email"`
	FullName string `json:"fullName"`
}
```

**Handler using both:**
```go
func CreateUser(svc *service.UserService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.UserRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		user, err := svc.CreateUser(c.Request.Context(), req.Email, req.FullName)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		c.JSON(http.StatusCreated, model.ToUserResponse(user)) // GORM model -> API response
	}
}
```

## Testing Strategy

### Repository Testing Philosophy

**Why NOT unit test repositories directly:**
- Repositories are thin, straightforward GORM wrappers
- Testing them in isolation would essentially test GORM itself
- E2E tests (see `rules/400-testing-first.mdc`) already exercise them through the full stack in a
  transaction that rolls back — that coverage is sufficient

**Focus unit testing on services instead:**
- Services contain the real business logic
- Services handle DTO<->model conversions and validation
- Services orchestrate multiple repository calls
- Services implement error handling

### Service Testing with a Mocked Repository

```go
package service_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/example/my_project/internal/model"
	"github.com/example/my_project/internal/service"
)

type mockUserRepository struct {
	mock.Mock
}

func (m *mockUserRepository) Create(ctx context.Context, user *model.User) error {
	args := m.Called(ctx, user)
	return args.Error(0)
}

func TestUserService_CreateUser_Success(t *testing.T) {
	repo := new(mockUserRepository)
	repo.On("Create", mock.Anything, mock.AnythingOfType("*model.User")).Return(nil)

	svc := service.NewUserService(repo)

	user, err := svc.CreateUser(context.Background(), "test@example.com", "Test User")

	require.NoError(t, err)
	assert.Equal(t, "test@example.com", user.Email)
	repo.AssertExpectations(t)
}
```

### Integration Testing

**When you DO need real-database testing** — use a transaction that always rolls back:

```go
//go:build integration

package repository_test

func TestGormUserRepository_Create_Integration(t *testing.T) {
	db := setupTestDB(t) // opens tx, t.Cleanup rolls it back

	repo := repository.NewGormUserRepository(db)
	user := &model.User{Email: "integration@example.com", FullName: "Integration Test"}

	err := repo.Create(context.Background(), user)
	require.NoError(t, err)
	assert.NotEmpty(t, user.ID)
}
```

Run with: `go test ./... -tags=integration -v`

### Test Organization

```
internal/
├── model/
│   └── user.go
├── repository/
│   └── user_repository.go        # Not directly unit tested
└── service/
    ├── user_service.go
    └── user_service_test.go      # Unit tests with mocked repository
```

## Migration Workflow

### Development Workflow (golang-migrate)
1. **Create a migration**:
```bash
migrate create -ext sql -dir migrations -seq create_users_table
```

2. **Edit the generated files**:
```sql
-- migrations/000001_create_users_table.up.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
```sql
-- migrations/000001_create_users_table.down.sql
DROP TABLE users;
```

3. **Apply the migration locally**:
```bash
migrate -database "$DATABASE_URL" -path migrations up
```

4. **Test rollback**:
```bash
migrate -database "$DATABASE_URL" -path migrations down 1
```

### GORM AutoMigrate Alternative (faster for course/prototype work)
```go
if err := db.AutoMigrate(&model.User{}, &model.Post{}); err != nil {
    log.Fatalf("automigrate failed: %v", err)
}
```

AutoMigrate is faster to iterate with but does not generate reviewable, reversible migration files —
prefer `golang-migrate` once the schema stabilizes or the course wants to teach production practices.

## Validation Checklist

Before completing any database task, verify:

### Architecture Compliance
- [ ] Repository not called directly from a handler
- [ ] Repository interface declared in the `service` package (consumer side)
- [ ] GORM model and API DTOs are separate, flat structs (no inheritance mimicry)
- [ ] `context.Context` propagated via `db.WithContext(ctx)`
- [ ] Service layer exists for business logic
- [ ] API DTOs use camelCase JSON tags with proper `binding` validation
- [ ] Converter functions (`ToXResponse`) used to cross the DB<->API boundary

### Code Quality
- [ ] Errors wrapped with `fmt.Errorf("...: %w", err)`
- [ ] Doc comments for all exported types and methods
- [ ] `gofmt -l .` clean, `golangci-lint run` clean

### Testing
- [ ] Service unit tests with a mocked repository
- [ ] Business logic and error handling scenarios tested
- [ ] No direct unit tests for repositories (covered via E2E)

### Database Design
- [ ] Migration files follow the `golang-migrate` naming convention (or AutoMigrate is documented)
- [ ] Table structure matches the GORM model's tags
- [ ] Proper indexes and constraints
- [ ] Timestamp fields for audit trail

## Common Anti-Patterns to Avoid

### Don't Do This
```go
// Calling the repository directly from a handler
func BadCreateUser(c *gin.Context) {
	repo := repository.NewGormUserRepository(db) // ❌ bypasses the service layer
	repo.Create(c.Request.Context(), &model.User{...})
}

// Using a single struct for both GORM and API
type User struct {
	ID       string `gorm:"primaryKey" json:"userId"` // ❌ mixed concerns
	Email    string `gorm:"uniqueIndex" json:"email"`
}

// Returning the GORM model directly from a handler
func badGetUser(c *gin.Context) {
	user, _ := userRepo.GetByID(c.Request.Context(), id)
	c.JSON(http.StatusOK, user) // ❌ leaks DB structure and snake_case-style gorm internals
}

// Declaring the interface next to its implementation
package repository

type UserRepository interface { // ❌ should live in the service package instead
	Create(ctx context.Context, u *model.User) error
}

// Swallowing errors
func badCreate(db *gorm.DB, u *model.User) {
	db.Create(u) // ❌ error return value ignored entirely
}
```

### Do This Instead
```go
// Service-mediated access
func GoodCreateUser(svc *service.UserService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.UserRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()}) // ✅ through the service
			return
		}
		user, err := svc.CreateUser(c.Request.Context(), req.Email, req.FullName)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}
		c.JSON(http.StatusCreated, model.ToUserResponse(user)) // ✅ converted DTO
	}
}

// Separate GORM model and DTOs
type User struct {
	ID    string `gorm:"primaryKey"`
	Email string `gorm:"uniqueIndex"`
}

type UserResponse struct {
	UserID string `json:"userId"`
	Email  string `json:"email"`
}

// Interface at point of use
package service

type UserRepository interface { // ✅ declared where it's consumed
	Create(ctx context.Context, u *model.User) error
}

// Checked, wrapped errors
func goodCreate(ctx context.Context, db *gorm.DB, u *model.User) error {
	if err := db.WithContext(ctx).Create(u).Error; err != nil {
		return fmt.Errorf("create user: %w", err) // ✅ checked and wrapped
	}
	return nil
}
```

## Troubleshooting

### Common Issues

**"cannot import cycle"**
- The repository interface belongs in `service`, not `repository` — check you didn't import
  `service` from `repository` (that would be backwards and create a cycle)

**"record not found" errors**
- `gorm.ErrRecordNotFound` is returned by `First()`/`Take()`/`Last()` when no row matches — check with
  `errors.Is(err, gorm.ErrRecordNotFound)`, don't string-match

**"column does not exist"**
- The GORM struct tag doesn't match the actual column name — check `gorm:"column:..."` overrides or
  confirm the migration ran

**"pq: extension pgcrypto does not exist"**
- `gen_random_uuid()` requires the `pgcrypto` extension: `CREATE EXTENSION IF NOT EXISTS pgcrypto;`
  in your first migration, or use `uuid-ossp`'s `uuid_generate_v4()` instead

### Quick Fixes

**Fix model field types**: Match PostgreSQL column types exactly (`VARCHAR` -> `string`, `TIMESTAMPTZ`
-> `time.Time`, `UUID` -> `string` with `gorm:"type:uuid"`)
**Add missing imports**: `time`, `context`, `fmt` are the most common misses
**Fix converter functions**: Handle zero-value time.Time and empty strings explicitly
**Add error handling**: Wrap every `.Error` check from GORM calls

## Environment-Specific Notes

### Development Environment
- Uses local Docker Compose PostgreSQL (`docker compose up -d`)
- `AutoMigrate` or `migrate up` run manually or at `main()` startup (dev-only)
- `logger.Info` GORM log level for visibility into generated SQL

### Production Environment
- Uses a managed PostgreSQL instance (RDS, Cloud SQL, etc.)
- Migrations applied via a dedicated CI/CD step (`migrate -path migrations -database $DATABASE_URL up`),
  never automatically inside `main()`
- `logger.Silent` or `logger.Error` GORM log level
- Connection pool tuned (`SetMaxOpenConns`, `SetConnMaxLifetime`) for the target Postgres tier
