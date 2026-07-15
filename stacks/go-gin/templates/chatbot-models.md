# Chatbot Models (Go + GORM)

GORM models (DB layer) and API DTOs (request/response layer) for the chatbot domain. Following the
Go idiom described in `vibe/vibe_database.md`: flat, separate structs per role — no inheritance chain.

## File: `internal/model/chat_session.go`

```go
package model

import "time"

// ChatSession is the GORM model representing a conversation between a user and the chatbot.
type ChatSession struct {
	ID        string    `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
	UserID    string    `gorm:"type:uuid;not null;index"`
	Title     string    `gorm:"default:''"`
	CreatedAt time.Time
	UpdatedAt time.Time
	Messages  []Message `gorm:"foreignKey:SessionID"`
}

// TableName pins the table name explicitly.
func (ChatSession) TableName() string { return "chat_sessions" }

// CreateSessionRequest is the API request body for creating a chat session.
type CreateSessionRequest struct {
	UserID string `json:"userId" binding:"required,uuid"`
	Title  string `json:"title" binding:"omitempty,max=200"`
}

// SessionResponse is the API response body representing a chat session (without messages).
type SessionResponse struct {
	SessionID string `json:"sessionId"`
	UserID    string `json:"userId"`
	Title     string `json:"title"`
	CreatedAt string `json:"createdAt"`
}

// SessionWithMessagesResponse is the API response body for a session including its messages.
type SessionWithMessagesResponse struct {
	SessionID string            `json:"sessionId"`
	UserID    string            `json:"userId"`
	Title     string            `json:"title"`
	CreatedAt string            `json:"createdAt"`
	Messages  []MessageResponse `json:"messages"`
}

// ToSessionResponse converts a GORM ChatSession model to its API response DTO (no messages).
func ToSessionResponse(s *ChatSession) SessionResponse {
	return SessionResponse{
		SessionID: s.ID,
		UserID:    s.UserID,
		Title:     s.Title,
		CreatedAt: s.CreatedAt.Format(time.RFC3339),
	}
}

// ToSessionWithMessagesResponse converts a GORM ChatSession (with Messages preloaded) to its full
// API response DTO, including the ordered list of messages.
func ToSessionWithMessagesResponse(s *ChatSession) SessionWithMessagesResponse {
	messages := make([]MessageResponse, 0, len(s.Messages))
	for _, m := range s.Messages {
		messages = append(messages, ToMessageResponse(&m))
	}

	return SessionWithMessagesResponse{
		SessionID: s.ID,
		UserID:    s.UserID,
		Title:     s.Title,
		CreatedAt: s.CreatedAt.Format(time.RFC3339),
		Messages:  messages,
	}
}
```

## File: `internal/model/message.go`

```go
package model

import "time"

// MessageRole enumerates who authored a message.
type MessageRole string

const (
	RoleUser      MessageRole = "user"
	RoleAssistant MessageRole = "assistant"
)

// Message is the GORM model representing a single message within a chat session.
type Message struct {
	ID        string    `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
	SessionID string    `gorm:"type:uuid;not null;index"`
	Role      string    `gorm:"not null"`
	Content   string    `gorm:"not null"`
	CreatedAt time.Time
}

// TableName pins the table name explicitly.
func (Message) TableName() string { return "messages" }

// SendMessageRequest is the API request body for sending a user message.
type SendMessageRequest struct {
	Content string `json:"content" binding:"required,min=1,max=4000"`
}

// MessageResponse is the API response body representing a single message.
type MessageResponse struct {
	MessageID string `json:"messageId"`
	SessionID string `json:"sessionId"`
	Role      string `json:"role"`
	Content   string `json:"content"`
	CreatedAt string `json:"createdAt"`
}

// MessageListResponse is the API response body for a paginated list of messages.
type MessageListResponse struct {
	Messages   []MessageResponse `json:"messages"`
	TotalCount int               `json:"totalCount"`
}

// ToMessageResponse converts a GORM Message model to its API response DTO.
func ToMessageResponse(m *Message) MessageResponse {
	return MessageResponse{
		MessageID: m.ID,
		SessionID: m.SessionID,
		Role:      m.Role,
		Content:   m.Content,
		CreatedAt: m.CreatedAt.Format(time.RFC3339),
	}
}
```

## Why Not Pydantic-Style Inheritance?

The Python/FastAPI stack layers models as `Base -> Full -> Create/Update`. Go has no idiomatic
equivalent — struct embedding exists but is rarely used this way, because:

1. It obscures which fields are actually settable per operation (embedding leaks all parent fields)
2. Go's json/gorm tag system works best on flat structs — embedding complicates tag resolution
3. Explicit, flat structs plus an explicit `ToXResponse()` converter function make the DB<->API
   boundary a visible, grep-able, testable point in the code — exactly the kind of explicitness Go
   favors over implicit magic

If two structs genuinely share many fields, extract a small named struct and embed it — but default to
flat, independent structs per operation unless duplication becomes a real maintenance burden.

## Migration (golang-migrate)

```sql
-- migrations/000010_create_chat_tables.up.sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_session_created ON messages(session_id, created_at);
```

```sql
-- migrations/000010_create_chat_tables.down.sql
DROP TABLE messages;
DROP TABLE chat_sessions;
```
