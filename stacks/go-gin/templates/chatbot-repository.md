# Chatbot Repositories (Go + GORM)

GORM-backed repositories for the chatbot domain. Interfaces are declared in the consuming
`service` package (see `templates/chatbot-service.md`), not here — this file contains only the
concrete implementations, per `rules/300-go-style.mdc`'s interface-at-point-of-use idiom.

## File: `internal/repository/chat_session_repository.go`

```go
// Package repository contains GORM-backed data access implementations.
package repository

import (
	"context"
	"fmt"

	"gorm.io/gorm"

	"github.com/example/chatbot-api/internal/model"
)

// GormChatSessionRepository is the GORM-backed implementation of chat session persistence.
type GormChatSessionRepository struct {
	db *gorm.DB
}

// NewGormChatSessionRepository constructs a GormChatSessionRepository with the given connection.
func NewGormChatSessionRepository(db *gorm.DB) *GormChatSessionRepository {
	return &GormChatSessionRepository{db: db}
}

// Create persists a new chat session.
func (r *GormChatSessionRepository) Create(ctx context.Context, session *model.ChatSession) error {
	if err := r.db.WithContext(ctx).Create(session).Error; err != nil {
		return fmt.Errorf("gorm chat session repository: create: %w", err)
	}
	return nil
}

// GetByID returns the session with the given ID, without preloading messages.
func (r *GormChatSessionRepository) GetByID(ctx context.Context, id string) (*model.ChatSession, error) {
	var session model.ChatSession
	if err := r.db.WithContext(ctx).First(&session, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("gorm chat session repository: get by id: %w", err)
	}
	return &session, nil
}

// GetByIDWithMessages returns the session with the given ID, with its messages preloaded and
// ordered chronologically.
func (r *GormChatSessionRepository) GetByIDWithMessages(ctx context.Context, id string) (*model.ChatSession, error) {
	var session model.ChatSession
	err := r.db.WithContext(ctx).
		Preload("Messages", func(db *gorm.DB) *gorm.DB {
			return db.Order("messages.created_at ASC")
		}).
		First(&session, "id = ?", id).Error
	if err != nil {
		return nil, fmt.Errorf("gorm chat session repository: get by id with messages: %w", err)
	}
	return &session, nil
}
```

## File: `internal/repository/message_repository.go`

```go
package repository

import (
	"context"
	"fmt"

	"gorm.io/gorm"

	"github.com/example/chatbot-api/internal/model"
)

// GormMessageRepository is the GORM-backed implementation of message persistence.
type GormMessageRepository struct {
	db *gorm.DB
}

// NewGormMessageRepository constructs a GormMessageRepository with the given connection.
func NewGormMessageRepository(db *gorm.DB) *GormMessageRepository {
	return &GormMessageRepository{db: db}
}

// Create persists a new message.
func (r *GormMessageRepository) Create(ctx context.Context, message *model.Message) error {
	if err := r.db.WithContext(ctx).Create(message).Error; err != nil {
		return fmt.Errorf("gorm message repository: create: %w", err)
	}
	return nil
}

// ListBySession returns messages for a session, ordered chronologically, paginated.
func (r *GormMessageRepository) ListBySession(ctx context.Context, sessionID string, limit, offset int) ([]model.Message, error) {
	var messages []model.Message
	err := r.db.WithContext(ctx).
		Where("session_id = ?", sessionID).
		Order("created_at ASC").
		Limit(limit).
		Offset(offset).
		Find(&messages).Error
	if err != nil {
		return nil, fmt.Errorf("gorm message repository: list by session: %w", err)
	}
	return messages, nil
}

// CountBySession returns the total number of messages in a session (for pagination metadata).
func (r *GormMessageRepository) CountBySession(ctx context.Context, sessionID string) (int64, error) {
	var count int64
	err := r.db.WithContext(ctx).
		Model(&model.Message{}).
		Where("session_id = ?", sessionID).
		Count(&count).Error
	if err != nil {
		return 0, fmt.Errorf("gorm message repository: count by session: %w", err)
	}
	return count, nil
}
```

## Transactional Create (Session + First Message)

When creating a session and immediately persisting the first user message, wrap both writes in a
single GORM transaction so a failure never leaves an orphaned session:

```go
// CreateSessionWithFirstMessage persists a new session and its first message atomically.
func (r *GormChatSessionRepository) CreateSessionWithFirstMessage(
	ctx context.Context, session *model.ChatSession, firstMessage *model.Message,
) error {
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		if err := tx.Create(session).Error; err != nil {
			return fmt.Errorf("create session: %w", err)
		}
		firstMessage.SessionID = session.ID
		if err := tx.Create(firstMessage).Error; err != nil {
			return fmt.Errorf("create first message: %w", err)
		}
		return nil
	})
}
```

## Testing Note

Per `rules/400-testing-first.mdc` and `vibe/vibe_database.md`, these repositories are **not** unit
tested directly — they are thin GORM wrappers exercised through the E2E handler tests in
`templates/chatbot-tests.md`, each running inside a rolled-back transaction for isolation.
