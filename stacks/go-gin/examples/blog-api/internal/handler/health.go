// Package handler contains Gin HTTP handlers (the Experience/API layer).
package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/example/blog-api/internal/database"
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
		c.JSON(http.StatusOK, HealthResponse{
			Status:      "healthy",
			Database:    database.Ping(db) == nil,
			Environment: environment,
		})
	}
}
