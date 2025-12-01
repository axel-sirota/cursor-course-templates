# Go Gin Starter Template

Use these patterns when scaffolding the Phase 0 Skeleton.

## Modules

### go.mod
```go
module example.com/app

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    gorm.io/gorm v1.25.7
)
```

## Entry Point

### cmd/server/main.go
```go
package main

import (
    "example.com/app/internal/api"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    
    // Health Check
    r.GET("/health", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "status": "ok",
        })
    })
    
    r.Run(":8080")
}
```

