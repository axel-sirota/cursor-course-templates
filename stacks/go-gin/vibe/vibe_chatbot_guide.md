# Chatbot Domain Guide (Go + Gin)

## Purpose

This guide walks through implementing a chatbot feature — chat sessions and messages — on the
Go/Gin stack, as a worked domain example alongside the phase-based workflow. It complements
`vibe_gin_boilerplate.md` and `vibe_database.md` with domain-specific entity design and an LLM client
abstraction idiomatic to Go.

Companion templates:
- `templates/chatbot-api.md` — Gin handlers/routes
- `templates/chatbot-models.md` — GORM models + API DTOs
- `templates/chatbot-repository.md` — repositories (interface-at-point-of-use)
- `templates/chatbot-service.md` — business logic + LLM client integration
- `templates/chatbot-tests.md` — table-driven and httptest-based tests
- `templates/chatbot-requirements.md` — go.mod dependency list

## Domain Overview

### Entities

**ChatSession**
- Represents a single conversation between a user and the chatbot
- Has many `Message`s
- Tracks creation time and (optionally) a title/summary

**Message**
- Belongs to a `ChatSession`
- Has a `Role` (`user` or `assistant`)
- Has `Content` (the text of the message)
- Ordered by `CreatedAt` within a session

### Entity Relationship

```
ChatSession (1) ──── (N) Message
```

### GORM Model Sketch

```go
// ChatSession is the GORM model representing a conversation.
type ChatSession struct {
    ID        string    `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
    UserID    string    `gorm:"type:uuid;not null;index"`
    Title     string
    CreatedAt time.Time
    UpdatedAt time.Time
    Messages  []Message `gorm:"foreignKey:SessionID"`
}

// Message is the GORM model representing a single message within a session.
type Message struct {
    ID        string    `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
    SessionID string    `gorm:"type:uuid;not null;index"`
    Role      string    `gorm:"not null"` // "user" or "assistant"
    Content   string    `gorm:"not null"`
    CreatedAt time.Time
}
```

See `templates/chatbot-models.md` for the full model + DTO set.

## API Surface

```
POST   /api/chat/sessions              Create a new chat session
GET    /api/chat/sessions/:id          Get a session with its messages
POST   /api/chat/sessions/:id/messages Send a message, get the assistant's reply
GET    /api/chat/sessions/:id/messages List messages in a session
```

See `templates/chatbot-api.md` for full handler implementations.

## LLM Client Abstraction

Go idiom: define a small interface for the LLM client at the point of use (the service layer), with a
mock implementation for local development/testing and a real implementation behind a build tag or
runtime config flag.

```go
// internal/service/llm_client.go

// LLMClient is the interface the chat service depends on for generating replies.
type LLMClient interface {
    Complete(ctx context.Context, messages []ChatMessage) (string, error)
}

// ChatMessage is a role/content pair sent to the LLM client.
type ChatMessage struct {
    Role    string
    Content string
}

// MockLLMClient returns a canned response — used in Phase 0 skeleton and in tests.
type MockLLMClient struct{}

func (MockLLMClient) Complete(ctx context.Context, messages []ChatMessage) (string, error) {
    return "This is a mock assistant response. Implement a real LLMClient for production.", nil
}
```

A real implementation (e.g. calling OpenAI or Anthropic's HTTP API) implements the same interface and
is swapped in via configuration — the service code never changes:

```go
// HTTPLLMClient calls a real LLM provider's chat completion endpoint over HTTP.
type HTTPLLMClient struct {
    apiKey     string
    httpClient *http.Client
    baseURL    string
}

func NewHTTPLLMClient(apiKey string) *HTTPLLMClient {
    return &HTTPLLMClient{
        apiKey:     apiKey,
        httpClient: &http.Client{Timeout: 30 * time.Second},
        baseURL:    "https://api.openai.com/v1",
    }
}

func (c *HTTPLLMClient) Complete(ctx context.Context, messages []ChatMessage) (string, error) {
    // Build request body, POST to c.baseURL+"/chat/completions" with c.apiKey as Bearer auth,
    // parse the response, return the assistant's text or a wrapped error.
    // Omitted here for brevity — see templates/chatbot-service.md for the full implementation.
    return "", nil
}
```

## Session-Based Build Order

Following the standard phase workflow (`rules/100-architect-phase.mdc` through
`rules/301-endpoint-phase.mdc`):

- **Phase 0 (Skeleton)**: Mock handlers for all four chatbot endpoints, `MockLLMClient` wired in
- **Phase 1**: `POST /api/chat/sessions` — create session (GORM model + repository + service)
- **Phase 2**: `POST /api/chat/sessions/:id/messages` — send message, get a reply (real or mock
  `LLMClient`, persists both the user message and the assistant reply)
- **Phase 3**: `GET /api/chat/sessions/:id` — read a session with its messages (`Preload("Messages")`)
- **Phase 4**: `GET /api/chat/sessions/:id/messages` — paginated message list

## Key Teaching Points

1. **Interface-at-point-of-use for the LLM client**: the service depends on `LLMClient`, not a
   concrete OpenAI/Anthropic SDK type — this is the same idiom as `PostRepository` in
   `rules/300-go-style.mdc`, applied to an external API dependency instead of a database.
2. **Mock-first development**: `MockLLMClient` lets Phase 0 and early tests run with zero external API
   calls or API keys — this mirrors the Python stack's `MockLLMClient` pattern but with Go's implicit
   interface satisfaction instead of an ABC.
3. **GORM `Preload` for the has-many relationship**: fetching a session with its messages is one query
   via `db.Preload("Messages").First(&session, "id = ?", id)`, not a manual join.
4. **Ordering messages**: always `ORDER BY created_at ASC` when loading a session's messages so the
   conversation renders in the right order — GORM's `Preload` supports custom ordering via
   `Preload("Messages", func(db *gorm.DB) *gorm.DB { return db.Order("messages.created_at ASC") })`.

## Next Steps

1. Read `templates/chatbot-models.md` for the full GORM model + DTO definitions
2. Read `templates/chatbot-repository.md` for the repository implementations
3. Read `templates/chatbot-service.md` for the service layer + LLM client wiring
4. Read `templates/chatbot-api.md` for the Gin handlers
5. Read `templates/chatbot-tests.md` for the test suite
6. Read `templates/chatbot-requirements.md` for the exact go.mod dependencies needed
