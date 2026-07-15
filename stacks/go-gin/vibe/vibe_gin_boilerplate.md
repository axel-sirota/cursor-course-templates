# Gin Project Boilerplate Guide

## Purpose

This guide provides step-by-step instructions for creating a complete Gin project boilerplate with
configuration, database integration, and modular structure. After following this guide, you'll have a
working API that starts with `go run ./cmd/server` and follows idiomatic Go conventions with
`gofmt`, `go vet`, and `golangci-lint`.

## Quick Start Checklist

- [ ] Initialize the Go module and install dependencies
- [ ] Copy `.env.example` to `.env` and configure
- [ ] Run `go run ./cmd/server`
- [ ] Test the API at http://localhost:8080/health

## Project Structure

```
project_name/
├── .env.example
├── .env                     # Not in git
├── .gitignore
├── .golangci.yml
├── go.mod
├── go.sum
├── Makefile
├── cmd/
│   └── server/
│       └── main.go          # Single entry point
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── database/
│   │   └── database.go
│   ├── middleware/
│   │   ├── cors.go
│   │   ├── logging.go
│   │   └── recovery.go
│   ├── handler/
│   │   ├── health.go
│   │   ├── health_test.go
│   │   ├── auth.go
│   │   └── routes.go
│   ├── model/
│   │   └── user.go
│   ├── repository/
│   │   └── user_repository.go
│   └── service/
│       ├── auth_service.go
│       └── auth_service_test.go
└── pkg/
    └── .gitkeep              # Reserved for genuinely reusable, externally-importable code
```

## Create Complete Project Structure

**Step-by-step file creation** (copy each file exactly as shown):

### 1. Create Directory Structure
```bash
mkdir my_project && cd my_project
mkdir -p cmd/server internal/config internal/database internal/middleware \
  internal/handler internal/model internal/repository internal/service pkg
```

### 2. Module & Dependencies

**Initialize the module:**
```bash
go mod init github.com/example/my_project
```

**Add dependencies:**
```bash
go get github.com/gin-gonic/gin@v1.10.0
go get github.com/gin-contrib/cors@v1.7.2
go get gorm.io/gorm@v1.25.10
go get gorm.io/driver/postgres@v1.5.9
go get github.com/spf13/viper@v1.19.0
go get github.com/google/uuid@v1.6.0
go get github.com/stretchr/testify@v1.9.0
go mod tidy
```

**.env.example**
```
# Server
PORT=8080
LOG_LEVEL=info

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/your_database?sslmode=disable

# JWT (if auth is used)
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**.gitignore**
```
# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib
main
server
/bin/
/dist/

# Test artifacts
*.test
*.out
coverage.out
coverage.html

# Environment
.env
.env.local

# Go workspace
go.work
go.work.sum

# Vendoring
vendor/

# IDE / OS
.vscode/
.idea/
.DS_Store
```

### 3. Core Configuration Files

**internal/config/config.go**
```go
// Package config loads application configuration from environment variables.
package config

import (
	"fmt"
	"strings"

	"github.com/spf13/viper"
)

// Config holds all application configuration, loaded once at startup.
type Config struct {
	Port                        string
	LogLevel                    string
	DatabaseURL                 string
	JWTSecretKey                string
	JWTAccessTokenExpireMinutes int
	AllowedOrigins               []string
}

// Load reads configuration from .env (if present) and the environment,
// validates required fields, and returns a populated Config.
//
// It returns an error if a required variable (DATABASE_URL) is missing.
func Load() (*Config, error) {
	viper.SetConfigFile(".env")
	viper.AutomaticEnv()
	_ = viper.ReadInConfig() // .env is optional; environment variables still work without it

	viper.SetDefault("PORT", "8080")
	viper.SetDefault("LOG_LEVEL", "info")
	viper.SetDefault("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
	viper.SetDefault("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080")

	cfg := &Config{
		Port:                         viper.GetString("PORT"),
		LogLevel:                     viper.GetString("LOG_LEVEL"),
		DatabaseURL:                  viper.GetString("DATABASE_URL"),
		JWTSecretKey:                 viper.GetString("JWT_SECRET_KEY"),
		JWTAccessTokenExpireMinutes:  viper.GetInt("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"),
		AllowedOrigins:               strings.Split(viper.GetString("ALLOWED_ORIGINS"), ","),
	}

	if cfg.DatabaseURL == "" {
		return nil, fmt.Errorf("config: DATABASE_URL is required")
	}

	return cfg, nil
}
```

**internal/database/database.go**
```go
// Package database manages the GORM connection pool and migrations.
package database

import (
	"fmt"
	"time"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// Connect opens a GORM connection to PostgreSQL with a tuned connection pool.
//
// It returns an error if the connection cannot be established.
func Connect(databaseURL string, debug bool) (*gorm.DB, error) {
	logLevel := logger.Silent
	if debug {
		logLevel = logger.Info
	}

	db, err := gorm.Open(postgres.Open(databaseURL), &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	})
	if err != nil {
		return nil, fmt.Errorf("database: connect: %w", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("database: get underlying sql.DB: %w", err)
	}

	sqlDB.SetMaxOpenConns(25)
	sqlDB.SetMaxIdleConns(25)
	sqlDB.SetConnMaxLifetime(5 * time.Minute)

	return db, nil
}

// Ping verifies the database connection is alive. Used by the health endpoint.
func Ping(db *gorm.DB) error {
	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("database: get underlying sql.DB: %w", err)
	}
	return sqlDB.Ping()
}
```

### 4. Middleware Files

**internal/middleware/recovery.go**
```go
// Package middleware contains Gin middleware shared across the application.
package middleware

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
)

// Recovery recovers from any panic in a handler and returns a 500 instead of
// crashing the process. It logs the panic with structured logging.
func Recovery() gin.HandlerFunc {
	return gin.CustomRecovery(func(c *gin.Context, recovered any) {
		slog.Error("panic recovered", "error", recovered, "path", c.Request.URL.Path)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
	})
}
```

**internal/middleware/logging.go**
```go
package middleware

import (
	"log/slog"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// RequestLogger logs each request with a correlation ID, method, path,
// status code, and latency using structured logging.
func RequestLogger() gin.HandlerFunc {
	return func(c *gin.Context) {
		correlationID := uuid.NewString()
		c.Set("correlation_id", correlationID)
		c.Writer.Header().Set("X-Correlation-ID", correlationID)

		start := time.Now()
		c.Next()
		latency := time.Since(start)

		slog.Info("request completed",
			"correlation_id", correlationID,
			"method", c.Request.Method,
			"path", c.Request.URL.Path,
			"status", c.Writer.Status(),
			"latency_ms", latency.Milliseconds(),
		)
	}
}
```

**internal/middleware/cors.go**
```go
package middleware

import (
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

// CORS configures cross-origin resource sharing for the given allowed origins.
func CORS(allowedOrigins []string) gin.HandlerFunc {
	return cors.New(cors.Config{
		AllowOrigins:     allowedOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	})
}
```

### 5. Handler Files

**internal/handler/health.go**
```go
// Package handler contains Gin HTTP handlers (the Experience/API layer).
package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/example/my_project/internal/database"
)

// HealthResponse is the API response body for the health check endpoint.
type HealthResponse struct {
	Status      string `json:"status"`
	Database    bool   `json:"database"`
	Environment string `json:"environment"`
}

// HealthCheck returns a HealthResponse describing service and database status.
func HealthCheck(db *gorm.DB, environment string) gin.HandlerFunc {
	return func(c *gin.Context) {
		dbHealthy := database.Ping(db) == nil

		c.JSON(http.StatusOK, HealthResponse{
			Status:      "healthy",
			Database:    dbHealthy,
			Environment: environment,
		})
	}
}
```

**internal/handler/routes.go**
```go
package handler

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/example/my_project/internal/service"
)

// RegisterRoutes wires all handlers into the given router, injecting their
// dependencies via factory functions (no global state).
func RegisterRoutes(r *gin.Engine, db *gorm.DB, environment string, authSvc *service.AuthService) {
	r.GET("/health", HealthCheck(db, environment))

	api := r.Group("/api")
	{
		auth := api.Group("/auth")
		{
			auth.POST("/register", Register(authSvc))
			auth.POST("/login", Login(authSvc))
		}
	}
}
```

### 6. Main Application File

**cmd/server/main.go**
```go
// Command server is the entrypoint for the API. It wires configuration,
// database, middleware, and routes, then serves HTTP with graceful shutdown.
package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"

	"github.com/example/my_project/internal/config"
	"github.com/example/my_project/internal/database"
	"github.com/example/my_project/internal/handler"
	"github.com/example/my_project/internal/middleware"
	"github.com/example/my_project/internal/repository"
	"github.com/example/my_project/internal/service"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		slog.Error("failed to load config", "error", err)
		os.Exit(1)
	}

	db, err := database.Connect(cfg.DatabaseURL, cfg.LogLevel == "debug")
	if err != nil {
		slog.Error("failed to connect to database", "error", err)
		os.Exit(1)
	}

	userRepo := repository.NewGormUserRepository(db)
	authSvc := service.NewAuthService(userRepo, cfg.JWTSecretKey)

	if cfg.LogLevel != "debug" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.New()
	r.Use(middleware.Recovery())
	r.Use(middleware.RequestLogger())
	r.Use(middleware.CORS(cfg.AllowedOrigins))

	handler.RegisterRoutes(r, db, cfg.LogLevel, authSvc)

	srv := &http.Server{
		Addr:              ":" + cfg.Port,
		Handler:           r,
		ReadHeaderTimeout: 5 * time.Second,
	}

	go func() {
		slog.Info("server starting", "port", cfg.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("server failed", "error", err)
			os.Exit(1)
		}
	}()

	// Graceful shutdown on SIGINT/SIGTERM
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	slog.Info("shutting down server")
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		slog.Error("server forced to shutdown", "error", err)
	}

	slog.Info("server exited cleanly")
}
```

### 7. Makefile

```makefile
.PHONY: build run test lint fmt vet quality tidy

build:
	go build -o bin/server ./cmd/server

run:
	go run ./cmd/server

test:
	go test ./... -v -race -cover

lint:
	golangci-lint run

fmt:
	gofmt -w .
	goimports -w .

vet:
	go vet ./...

tidy:
	go mod tidy

quality: fmt vet lint test
	@echo "All quality checks passed!"
```

### 8. Test Files

**Test organization**: colocated `_test.go` files next to the code they test (idiomatic Go, unlike a
separate `tests/` tree).

**internal/handler/health_test.go**
```go
package handler_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"

	"github.com/example/my_project/internal/handler"
)

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)
	m.Run()
}

func TestHealthCheck(t *testing.T) {
	r := gin.New()
	r.GET("/health", handler.HealthCheck(testDB(t), "test"))

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.Contains(t, w.Body.String(), `"status":"healthy"`)
}
```

## Usage Instructions

### 1. Create Project and Module
```bash
mkdir my_project && cd my_project
go mod init github.com/example/my_project
go get github.com/gin-gonic/gin@v1.10.0 gorm.io/gorm@v1.25.10 gorm.io/driver/postgres@v1.5.9
go mod tidy
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Application
```bash
# Start development server
go run ./cmd/server

# Or run tests
go test ./... -v
```

### 4. Test the API
- Health check: `GET /health`
- Register: `POST /api/auth/register`
- Login: `POST /api/auth/login`

Gin has no built-in `/docs` UI — refer to `openapi.yaml` directly, or serve it via a static Swagger UI
container / `swaggo/swag` if interactive docs are needed.

## API Guidelines

### Request/Response DTOs
Use camelCase JSON tags on flat Go structs — there is no Pydantic-style inheritance chain:

```go
type CreatePostRequest struct {
	Title    string `json:"title" binding:"required,min=1,max=200"`
	Content  string `json:"content" binding:"required"`
	AuthorID string `json:"authorId" binding:"required,uuid"`
}
```

### Adding Protected Endpoints
```go
func RequireAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := c.GetHeader("Authorization")
		if token == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing authorization header"})
			return
		}
		// validate token, set user in context
		c.Next()
	}
}

protected := api.Group("/posts")
protected.Use(RequireAuth())
protected.POST("", handler.CreatePost(postSvc))
```

### Error Handling
```go
if post == nil {
	c.JSON(http.StatusNotFound, gin.H{"error": "post not found"})
	return
}
```

## Code Quality & Error Prevention

### Development Tools Setup

**Install golangci-lint** (once per machine):
```bash
go install github.com/golangci-lint/golangci-lint/cmd/golangci-lint@latest
```

**.golangci.yml** — see `rules/001-environment-setup.mdc` for the full baseline config.

### Usage Commands

**Manual quality checks (run before every phase transition):**
```bash
make quality
# Or individually:
gofmt -l .              # Formatting check
go vet ./...             # Suspicious constructs
golangci-lint run        # Full lint suite
go test ./... -race -cover  # Tests with race detector and coverage
```

### CI Integration Example

```yaml
- name: Set up Go
  uses: actions/setup-go@v5
  with:
    go-version: '1.23'

- name: Build
  run: go build ./...

- name: Vet
  run: go vet ./...

- name: Lint
  uses: golangci/golangci-lint-action@v6

- name: Test
  run: go test ./... -race -cover
```

## Next Steps

After creating the boilerplate:

1. **Configure Database**: Update `.env` with your database credentials
2. **Add Modules**: Create new handler/service/repository/model sets following this pattern
3. **Database Models**: Create GORM models and migrations (`vibe/vibe_database.md`)
4. **Production Setup**: Configure deployment settings, TLS termination, etc.

## Troubleshooting

**"package not found" errors**: Run `go mod tidy` to resolve missing dependencies.
**Database connection fails**: Check `DATABASE_URL` in `.env` and that Postgres is running (`docker compose ps`).
**CORS errors**: Add your frontend URL to `ALLOWED_ORIGINS` in `.env`.
**"undefined: gin.CustomRecovery"**: Ensure `gin-gonic/gin` is pinned to `v1.9+`.
