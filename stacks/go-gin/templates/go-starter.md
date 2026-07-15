# Go Gin Starter Template

Quick-reference boilerplate for scaffolding the Phase 0 Skeleton. For the full walkthrough with
middleware, config loading, graceful shutdown, and Makefile, see `vibe/vibe_gin_boilerplate.md`.

## Module

### go.mod
```go
module github.com/example/app

go 1.23

require (
    github.com/gin-gonic/gin v1.10.0
    gorm.io/gorm v1.25.10
    gorm.io/driver/postgres v1.5.9
)
```

Initialize with:
```bash
go mod init github.com/example/app
go get github.com/gin-gonic/gin@v1.10.0
go get gorm.io/gorm@v1.25.10
go get gorm.io/driver/postgres@v1.5.9
go mod tidy
```

## Minimal Entry Point

### cmd/server/main.go
```go
package main

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    // Health Check
    r.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "status": "ok",
        })
    })

    r.Run(":8080")
}
```

Run it:
```bash
go run ./cmd/server
curl http://localhost:8080/health
```

## Minimal Mock Handler Pattern (Phase 0)

```go
type CreateItemRequest struct {
    Name string `json:"name" binding:"required"`
}

type ItemResponse struct {
    ItemID string `json:"itemId"`
    Name   string `json:"name"`
}

func main() {
    r := gin.Default()

    r.GET("/health", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"status": "ok"})
    })

    r.POST("/api/items", func(c *gin.Context) {
        var req CreateItemRequest
        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        c.JSON(http.StatusCreated, ItemResponse{ItemID: "mock-123", Name: req.Name})
    })

    r.Run(":8080")
}
```

## Next Steps

Once the Phase 0 skeleton is working:
1. Split `main.go` into `cmd/server/main.go` + `internal/handler/` + `internal/config/` following
   `vibe/vibe_gin_boilerplate.md`
2. Add `.golangci.yml` and `.env.example` per `rules/001-environment-setup.mdc`
3. Add `docker-compose.yml` from `templates/docker-compose-template.yaml`
4. Begin Phase 1 implementation per `rules/301-endpoint-phase.mdc`
