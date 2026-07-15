# Chatbot Service Layer (Go + Gin)

Business logic for the chatbot domain: session creation, sending a message and getting a reply, and
listing session history. Repository interfaces are declared here (consumer side), per
`rules/300-go-style.mdc`.

## File: `internal/service/chat_service.go`

```go
// Package service contains business logic, orchestrating repositories and external clients.
package service

import (
	"context"
	"errors"
	"fmt"

	"github.com/example/chatbot-api/internal/model"
)

// ErrSessionNotFound is returned when a chat session does not exist.
var ErrSessionNotFound = errors.New("chat session not found")

// SessionRepository is the persistence contract this service depends on for sessions.
type SessionRepository interface {
	Create(ctx context.Context, session *model.ChatSession) error
	GetByID(ctx context.Context, id string) (*model.ChatSession, error)
	GetByIDWithMessages(ctx context.Context, id string) (*model.ChatSession, error)
}

// MessageRepository is the persistence contract this service depends on for messages.
type MessageRepository interface {
	Create(ctx context.Context, message *model.Message) error
	ListBySession(ctx context.Context, sessionID string, limit, offset int) ([]model.Message, error)
	CountBySession(ctx context.Context, sessionID string) (int64, error)
}

// ChatMessage is a role/content pair sent to the LLM client.
type ChatMessage struct {
	Role    string
	Content string
}

// LLMClient is the interface this service depends on for generating assistant replies.
// See vibe/vibe_chatbot_guide.md for the mock and real implementations.
type LLMClient interface {
	Complete(ctx context.Context, messages []ChatMessage) (string, error)
}

// ChatService contains business logic for chat sessions and messages.
type ChatService struct {
	sessions SessionRepository
	messages MessageRepository
	llm      LLMClient
}

// NewChatService constructs a ChatService with the given dependencies.
func NewChatService(sessions SessionRepository, messages MessageRepository, llm LLMClient) *ChatService {
	return &ChatService{sessions: sessions, messages: messages, llm: llm}
}

// CreateSession creates a new chat session for the given user.
func (s *ChatService) CreateSession(ctx context.Context, userID, title string) (*model.ChatSession, error) {
	session := &model.ChatSession{UserID: userID, Title: title}
	if err := s.sessions.Create(ctx, session); err != nil {
		return nil, fmt.Errorf("chat service: create session: %w", err)
	}
	return session, nil
}

// GetSessionWithMessages retrieves a session along with its full, ordered message history.
func (s *ChatService) GetSessionWithMessages(ctx context.Context, sessionID string) (*model.ChatSession, error) {
	session, err := s.sessions.GetByIDWithMessages(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("chat service: get session with messages: %w: %w", ErrSessionNotFound, err)
	}
	return session, nil
}

// SendMessage persists the user's message, calls the LLM client for a reply, persists the
// assistant's reply, and returns it.
//
// It returns ErrSessionNotFound if the session does not exist.
func (s *ChatService) SendMessage(ctx context.Context, sessionID, content string) (*model.Message, error) {
	session, err := s.sessions.GetByID(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("chat service: send message: %w: %w", ErrSessionNotFound, err)
	}

	userMessage := &model.Message{
		SessionID: session.ID,
		Role:      string(model.RoleUser),
		Content:   content,
	}
	if err := s.messages.Create(ctx, userMessage); err != nil {
		return nil, fmt.Errorf("chat service: persist user message: %w", err)
	}

	history, err := s.messages.ListBySession(ctx, session.ID, 50, 0)
	if err != nil {
		return nil, fmt.Errorf("chat service: load history: %w", err)
	}

	llmMessages := make([]ChatMessage, 0, len(history))
	for _, m := range history {
		llmMessages = append(llmMessages, ChatMessage{Role: m.Role, Content: m.Content})
	}

	replyContent, err := s.llm.Complete(ctx, llmMessages)
	if err != nil {
		return nil, fmt.Errorf("chat service: llm completion: %w", err)
	}

	assistantMessage := &model.Message{
		SessionID: session.ID,
		Role:      string(model.RoleAssistant),
		Content:   replyContent,
	}
	if err := s.messages.Create(ctx, assistantMessage); err != nil {
		return nil, fmt.Errorf("chat service: persist assistant message: %w", err)
	}

	return assistantMessage, nil
}

// ListMessages returns a paginated list of messages for a session, plus the total count.
func (s *ChatService) ListMessages(ctx context.Context, sessionID string, limit, offset int) ([]model.Message, int64, error) {
	messages, err := s.messages.ListBySession(ctx, sessionID, limit, offset)
	if err != nil {
		return nil, 0, fmt.Errorf("chat service: list messages: %w", err)
	}

	total, err := s.messages.CountBySession(ctx, sessionID)
	if err != nil {
		return nil, 0, fmt.Errorf("chat service: count messages: %w", err)
	}

	return messages, total, nil
}
```

## File: `internal/service/llm_client.go`

```go
package service

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// MockLLMClient returns a canned response — used in Phase 0 skeleton and in tests, so no API key
// or network access is required to develop or test the chatbot feature.
type MockLLMClient struct{}

// Complete returns a fixed mock response regardless of input.
func (MockLLMClient) Complete(ctx context.Context, messages []ChatMessage) (string, error) {
	return "This is a mock assistant response. Configure a real LLMClient for production.", nil
}

// HTTPLLMClient calls a real LLM provider's chat completion endpoint over HTTP.
type HTTPLLMClient struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
}

// NewHTTPLLMClient constructs an HTTPLLMClient with a 30-second request timeout.
func NewHTTPLLMClient(apiKey, baseURL string) *HTTPLLMClient {
	return &HTTPLLMClient{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

type completionRequest struct {
	Model    string        `json:"model"`
	Messages []ChatMessage `json:"messages"`
}

type completionResponse struct {
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
}

// Complete sends the conversation history to the LLM provider and returns the assistant's reply.
func (c *HTTPLLMClient) Complete(ctx context.Context, messages []ChatMessage) (string, error) {
	reqBody, err := json.Marshal(completionRequest{Model: "gpt-4o-mini", Messages: messages})
	if err != nil {
		return "", fmt.Errorf("http llm client: marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/chat/completions", bytes.NewReader(reqBody))
	if err != nil {
		return "", fmt.Errorf("http llm client: build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.apiKey)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("http llm client: request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("http llm client: unexpected status %d: %s", resp.StatusCode, body)
	}

	var result completionResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("http llm client: decode response: %w", err)
	}
	if len(result.Choices) == 0 {
		return "", fmt.Errorf("http llm client: no choices in response")
	}

	return result.Choices[0].Message.Content, nil
}
```

## Wiring in `cmd/server/main.go`

```go
var llmClient service.LLMClient
if cfg.OpenAIAPIKey != "" {
    llmClient = service.NewHTTPLLMClient(cfg.OpenAIAPIKey, "https://api.openai.com/v1")
} else {
    llmClient = service.MockLLMClient{} // Phase 0 / local dev without an API key
}

chatSvc := service.NewChatService(
    repository.NewGormChatSessionRepository(db),
    repository.NewGormMessageRepository(db),
    llmClient,
)
```

This is the same pattern as swapping a repository implementation — the service depends on the
`LLMClient` interface, never on `*HTTPLLMClient` or `MockLLMClient` directly, so tests and Phase 0
skeletons never need real API credentials.
