// Package middleware contains Gin middleware shared across the blog-api application.
package middleware

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
)

// Recovery recovers from any panic in a handler and returns a 500 instead of crashing the
// process. It logs the panic with structured logging.
func Recovery() gin.HandlerFunc {
	return gin.CustomRecovery(func(c *gin.Context, recovered any) {
		slog.Error("panic recovered", "error", recovered, "path", c.Request.URL.Path)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
	})
}
