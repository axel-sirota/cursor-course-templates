package middleware

import (
	"log/slog"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// RequestLogger logs each request with a correlation ID, method, path, status code, and latency.
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
