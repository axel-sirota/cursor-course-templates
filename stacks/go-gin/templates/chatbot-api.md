# Chatbot API Handlers (Go + Gin)

Gin handlers for the chatbot domain, following the dependency-injecting factory-function pattern from
`rules/500-implementation.mdc`.

## File: `internal/handler/chat.go`

```go
// Package handler contains Gin HTTP handlers (the Experience/API layer).
package handler

import (
	"errors"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	"github.com/example/chatbot-api/internal/model"
	"github.com/example/chatbot-api/internal/service"
)

// CreateSession handles POST /api/chat/sessions.
func CreateSession(svc *service.ChatService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.CreateSessionRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		session, err := svc.CreateSession(c.Request.Context(), req.UserID, req.Title)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create session"})
			return
		}

		c.JSON(http.StatusCreated, model.ToSessionResponse(session))
	}
}

// GetSession handles GET /api/chat/sessions/:id.
func GetSession(svc *service.ChatService) gin.HandlerFunc {
	return func(c *gin.Context) {
		sessionID := c.Param("id")

		session, err := svc.GetSessionWithMessages(c.Request.Context(), sessionID)
		if err != nil {
			if errors.Is(err, service.ErrSessionNotFound) {
				c.JSON(http.StatusNotFound, gin.H{"error": "session not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		c.JSON(http.StatusOK, model.ToSessionWithMessagesResponse(session))
	}
}

// SendMessage handles POST /api/chat/sessions/:id/messages.
func SendMessage(svc *service.ChatService) gin.HandlerFunc {
	return func(c *gin.Context) {
		sessionID := c.Param("id")

		var req model.SendMessageRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		reply, err := svc.SendMessage(c.Request.Context(), sessionID, req.Content)
		if err != nil {
			if errors.Is(err, service.ErrSessionNotFound) {
				c.JSON(http.StatusNotFound, gin.H{"error": "session not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get assistant reply"})
			return
		}

		c.JSON(http.StatusCreated, model.ToMessageResponse(reply))
	}
}

// ListMessages handles GET /api/chat/sessions/:id/messages.
func ListMessages(svc *service.ChatService) gin.HandlerFunc {
	return func(c *gin.Context) {
		sessionID := c.Param("id")

		limit, offset := parsePagination(c)

		messages, total, err := svc.ListMessages(c.Request.Context(), sessionID, limit, offset)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to list messages"})
			return
		}

		responses := make([]model.MessageResponse, 0, len(messages))
		for i := range messages {
			responses = append(responses, model.ToMessageResponse(&messages[i]))
		}

		c.JSON(http.StatusOK, model.MessageListResponse{
			Messages:   responses,
			TotalCount: int(total),
		})
	}
}

// parsePagination reads limit/offset query parameters with sane defaults and bounds.
func parsePagination(c *gin.Context) (limit, offset int) {
	limit = 20
	offset = 0

	if l, err := strconv.Atoi(c.Query("limit")); err == nil && l > 0 && l <= 100 {
		limit = l
	}
	if o, err := strconv.Atoi(c.Query("offset")); err == nil && o >= 0 {
		offset = o
	}
	return limit, offset
}
```

## File: `internal/handler/routes_chat.go`

```go
package handler

import (
	"github.com/gin-gonic/gin"

	"github.com/example/chatbot-api/internal/service"
)

// RegisterChatRoutes wires all chat handlers into the given router group.
func RegisterChatRoutes(api *gin.RouterGroup, chatSvc *service.ChatService) {
	sessions := api.Group("/chat/sessions")
	{
		sessions.POST("", CreateSession(chatSvc))
		sessions.GET("/:id", GetSession(chatSvc))
		sessions.POST("/:id/messages", SendMessage(chatSvc))
		sessions.GET("/:id/messages", ListMessages(chatSvc))
	}
}
```

## Phase 0 Mock Handlers (for the skeleton session)

Before the real service exists, Phase 0 uses mock responses directly, matching the OpenAPI contract:

```go
// CreateSession — MOCK IMPLEMENTATION (Phase 0).
func CreateSessionMock(c *gin.Context) {
	var req model.CreateSessionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, model.SessionResponse{
		SessionID: "mock-session-123",
		UserID:    req.UserID,
		Title:     req.Title,
		CreatedAt: "2024-01-01T00:00:00Z",
	})
}

// SendMessage — MOCK IMPLEMENTATION (Phase 0), always returns the same mock reply.
func SendMessageMock(c *gin.Context) {
	var req model.SendMessageRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, model.MessageResponse{
		MessageID: "mock-message-456",
		SessionID: c.Param("id"),
		Role:      "assistant",
		Content:   "This is a mock assistant response.",
		CreatedAt: "2024-01-01T00:00:00Z",
	})
}
```

Note these Phase 0 mocks are replaced session-by-session in Phase 1+ following
`rules/301-endpoint-phase.mdc`, exactly like the generic mock-to-real pattern — the chatbot domain
introduces no special-casing to that workflow.
