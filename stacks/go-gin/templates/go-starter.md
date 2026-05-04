# Go Gin Project Scaffold

## Directory Structure

```
cmd/server/
    main.go              (≤20 lines: wire deps, start server, graceful shutdown)
internal/
    handler/
        user.go          (Gin handler struct + routes registration)
        user_test.go     (table-driven unit tests with mock service)
    service/
        user.go          (UserService interface + impl)
        user_test.go     (table-driven unit tests)
    repository/
        user.go          (UserRepository interface + postgres impl)
        user_test.go     (integration test with testcontainers, build tag)
    model/
        user.go          (domain model structs)
pkg/
    config/
        config.go        (viper/env config loading)
    db/
        postgres.go      (connection pool setup)
```

---

## `cmd/server/main.go`

```go
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/yourorg/yourapp/internal/handler"
	"github.com/yourorg/yourapp/internal/repository"
	"github.com/yourorg/yourapp/internal/service"
	"github.com/yourorg/yourapp/pkg/config"
	"github.com/yourorg/yourapp/pkg/db"
)

func main() {
	cfg := config.Load()
	pool := db.Connect(cfg.DatabaseURL)
	defer pool.Close()

	repo := repository.NewPostgresUserRepository(pool)
	svc := service.NewUserService(repo)
	h := handler.NewUserHandler(svc)

	router := h.RegisterRoutes()
	srv := &http.Server{Addr: ":" + cfg.Port, Handler: router}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("server shutdown: %v", err)
	}
}
```

---

## `internal/handler/user.go`

The handler layer handles HTTP only. It receives a `UserService` interface — defined here, at the consumer side.

```go
package handler

import (
	"context"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/yourorg/yourapp/internal/model"
)

// UserService is the interface this handler depends on.
// Defined here (consumer side), not in the service package.
type UserService interface {
	CreateUser(ctx context.Context, name, email string) (model.User, error)
	GetUser(ctx context.Context, id int64) (model.User, error)
	ListUsers(ctx context.Context) ([]model.User, error)
}

type UserHandler struct {
	svc UserService
}

func NewUserHandler(svc UserService) *UserHandler {
	return &UserHandler{svc: svc}
}

func (h *UserHandler) RegisterRoutes() *gin.Engine {
	r := gin.Default()
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})
	r.POST("/users", h.CreateUser)
	r.GET("/users/:id", h.GetUser)
	r.GET("/users", h.ListUsers)
	return r
}

func (h *UserHandler) CreateUser(c *gin.Context) {
	var req struct {
		Name  string `json:"name"  binding:"required"`
		Email string `json:"email" binding:"required,email"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	user, err := h.svc.CreateUser(c.Request.Context(), req.Name, req.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create user"})
		return
	}
	c.JSON(http.StatusCreated, user)
}

func (h *UserHandler) GetUser(c *gin.Context) {
	// parse id, call h.svc.GetUser, return JSON
}

func (h *UserHandler) ListUsers(c *gin.Context) {
	users, err := h.svc.ListUsers(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to list users"})
		return
	}
	c.JSON(http.StatusOK, users)
}
```

---

## `internal/service/user.go`

```go
package service

import (
	"context"
	"fmt"

	"github.com/yourorg/yourapp/internal/model"
)

// UserRepository is defined here at the consumer (service) side.
type UserRepository interface {
	Create(ctx context.Context, user model.User) (model.User, error)
	GetByID(ctx context.Context, id int64) (model.User, error)
	List(ctx context.Context) ([]model.User, error)
}

type userService struct {
	repo UserRepository
}

func NewUserService(repo UserRepository) *userService {
	return &userService{repo: repo}
}

func (u *userService) CreateUser(ctx context.Context, name, email string) (model.User, error) {
	user, err := u.repo.Create(ctx, model.User{Name: name, Email: email})
	if err != nil {
		return model.User{}, fmt.Errorf("creating user: %w", err)
	}
	return user, nil
}

func (u *userService) GetUser(ctx context.Context, id int64) (model.User, error) {
	user, err := u.repo.GetByID(ctx, id)
	if err != nil {
		return model.User{}, fmt.Errorf("getting user %d: %w", id, err)
	}
	return user, nil
}

func (u *userService) ListUsers(ctx context.Context) ([]model.User, error) {
	users, err := u.repo.List(ctx)
	if err != nil {
		return nil, fmt.Errorf("listing users: %w", err)
	}
	return users, nil
}
```
