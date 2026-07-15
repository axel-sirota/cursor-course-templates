# Chatbot Tests (Go + Gin)

E2E (httptest) and unit (table-driven, mocked repository/LLM client) tests for the chatbot domain, per
`rules/400-testing-first.mdc`.

## File: `internal/handler/chat_test.go` (E2E)

```go
package handler_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/example/chatbot-api/internal/handler"
	"github.com/example/chatbot-api/internal/model"
	"github.com/example/chatbot-api/internal/repository"
	"github.com/example/chatbot-api/internal/service"
)

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)
	m.Run()
}

func setupChatRouter(t *testing.T) *gin.Engine {
	t.Helper()

	db := setupTestDB(t) // opens a transaction, rolls back via t.Cleanup — see conftest pattern below
	chatSvc := service.NewChatService(
		repository.NewGormChatSessionRepository(db),
		repository.NewGormMessageRepository(db),
		service.MockLLMClient{}, // no real API calls in tests
	)

	r := gin.New()
	api := r.Group("/api")
	handler.RegisterChatRoutes(api, chatSvc)
	return r
}

func TestCreateSession_Success(t *testing.T) {
	router := setupChatRouter(t)

	body, _ := json.Marshal(model.CreateSessionRequest{
		UserID: "11111111-1111-1111-1111-111111111111",
		Title:  "Test Conversation",
	})
	req := httptest.NewRequest(http.MethodPost, "/api/chat/sessions", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	router.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var resp model.SessionResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, "Test Conversation", resp.Title)
	assert.NotEmpty(t, resp.SessionID)
}

func TestCreateSession_ValidationError(t *testing.T) {
	router := setupChatRouter(t)

	body, _ := json.Marshal(map[string]string{"userId": "not-a-uuid"})
	req := httptest.NewRequest(http.MethodPost, "/api/chat/sessions", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestSendMessage_Success(t *testing.T) {
	router := setupChatRouter(t)
	sessionID := createTestSession(t, router)

	body, _ := json.Marshal(model.SendMessageRequest{Content: "Hello, chatbot!"})
	req := httptest.NewRequest(http.MethodPost, "/api/chat/sessions/"+sessionID+"/messages", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	router.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var resp model.MessageResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, "assistant", resp.Role)
	assert.NotEmpty(t, resp.Content) // MockLLMClient always returns non-empty content
}

func TestSendMessage_SessionNotFound(t *testing.T) {
	router := setupChatRouter(t)

	body, _ := json.Marshal(model.SendMessageRequest{Content: "Hello"})
	req := httptest.NewRequest(http.MethodPost, "/api/chat/sessions/00000000-0000-0000-0000-000000000000/messages", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}

func TestGetSession_WithMessages(t *testing.T) {
	router := setupChatRouter(t)
	sessionID := createTestSession(t, router)
	sendTestMessage(t, router, sessionID, "First message")

	req := httptest.NewRequest(http.MethodGet, "/api/chat/sessions/"+sessionID, nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	require.Equal(t, http.StatusOK, w.Code)

	var resp model.SessionWithMessagesResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Len(t, resp.Messages, 2) // user message + assistant reply
	assert.Equal(t, "user", resp.Messages[0].Role)
	assert.Equal(t, "assistant", resp.Messages[1].Role)
}

func TestListMessages_Pagination(t *testing.T) {
	router := setupChatRouter(t)
	sessionID := createTestSession(t, router)
	sendTestMessage(t, router, sessionID, "Message 1")
	sendTestMessage(t, router, sessionID, "Message 2")

	req := httptest.NewRequest(http.MethodGet, "/api/chat/sessions/"+sessionID+"/messages?limit=2&offset=0", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	require.Equal(t, http.StatusOK, w.Code)

	var resp model.MessageListResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, 4, resp.TotalCount) // 2 user + 2 assistant messages
	assert.Len(t, resp.Messages, 2)     // limited to 2
}

// --- test helpers ---

func createTestSession(t *testing.T, router *gin.Engine) string {
	t.Helper()
	body, _ := json.Marshal(model.CreateSessionRequest{UserID: "11111111-1111-1111-1111-111111111111"})
	req := httptest.NewRequest(http.MethodPost, "/api/chat/sessions", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	require.Equal(t, http.StatusCreated, w.Code)

	var resp model.SessionResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	return resp.SessionID
}

func sendTestMessage(t *testing.T, router *gin.Engine, sessionID, content string) {
	t.Helper()
	body, _ := json.Marshal(model.SendMessageRequest{Content: content})
	req := httptest.NewRequest(http.MethodPost, "/api/chat/sessions/"+sessionID+"/messages", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	require.Equal(t, http.StatusCreated, w.Code)
}
```

## File: `internal/service/chat_service_test.go` (Unit, mocked dependencies)

```go
package service_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/example/chatbot-api/internal/model"
	"github.com/example/chatbot-api/internal/service"
)

type mockSessionRepository struct{ mock.Mock }

func (m *mockSessionRepository) Create(ctx context.Context, s *model.ChatSession) error {
	args := m.Called(ctx, s)
	return args.Error(0)
}
func (m *mockSessionRepository) GetByID(ctx context.Context, id string) (*model.ChatSession, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*model.ChatSession), args.Error(1)
}
func (m *mockSessionRepository) GetByIDWithMessages(ctx context.Context, id string) (*model.ChatSession, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*model.ChatSession), args.Error(1)
}

type mockMessageRepository struct{ mock.Mock }

func (m *mockMessageRepository) Create(ctx context.Context, msg *model.Message) error {
	args := m.Called(ctx, msg)
	return args.Error(0)
}
func (m *mockMessageRepository) ListBySession(ctx context.Context, sessionID string, limit, offset int) ([]model.Message, error) {
	args := m.Called(ctx, sessionID, limit, offset)
	return args.Get(0).([]model.Message), args.Error(1)
}
func (m *mockMessageRepository) CountBySession(ctx context.Context, sessionID string) (int64, error) {
	args := m.Called(ctx, sessionID)
	return args.Get(0).(int64), args.Error(1)
}

type stubLLMClient struct {
	response string
}

func (s stubLLMClient) Complete(ctx context.Context, messages []service.ChatMessage) (string, error) {
	return s.response, nil
}

func TestChatService_SendMessage_Success(t *testing.T) {
	sessions := new(mockSessionRepository)
	messages := new(mockMessageRepository)

	existingSession := &model.ChatSession{ID: "session-123"}
	sessions.On("GetByID", mock.Anything, "session-123").Return(existingSession, nil)
	messages.On("Create", mock.Anything, mock.AnythingOfType("*model.Message")).Return(nil)
	messages.On("ListBySession", mock.Anything, "session-123", 50, 0).Return([]model.Message{}, nil)

	svc := service.NewChatService(sessions, messages, stubLLMClient{response: "Hello, human!"})

	reply, err := svc.SendMessage(context.Background(), "session-123", "Hi there")

	require.NoError(t, err)
	assert.Equal(t, "assistant", reply.Role)
	assert.Equal(t, "Hello, human!", reply.Content)
	messages.AssertNumberOfCalls(t, "Create", 2) // user message + assistant reply
}

func TestChatService_SendMessage_SessionNotFound(t *testing.T) {
	sessions := new(mockSessionRepository)
	messages := new(mockMessageRepository)

	sessions.On("GetByID", mock.Anything, "missing").Return(nil, assert.AnError)

	svc := service.NewChatService(sessions, messages, stubLLMClient{})

	_, err := svc.SendMessage(context.Background(), "missing", "Hi")

	require.Error(t, err)
	assert.ErrorIs(t, err, service.ErrSessionNotFound)
}

func TestChatService_CreateSession_Table(t *testing.T) {
	tests := []struct {
		name    string
		userID  string
		title   string
		wantErr bool
	}{
		{name: "with title", userID: "user-1", title: "My Chat", wantErr: false},
		{name: "without title", userID: "user-1", title: "", wantErr: false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			sessions := new(mockSessionRepository)
			sessions.On("Create", mock.Anything, mock.AnythingOfType("*model.ChatSession")).Return(nil)

			svc := service.NewChatService(sessions, new(mockMessageRepository), stubLLMClient{})

			session, err := svc.CreateSession(context.Background(), tt.userID, tt.title)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Equal(t, tt.title, session.Title)
			}
		})
	}
}
```

## Test Database Setup Helper

```go
// setupTestDB opens a connection and wraps the test in a transaction that is always rolled back.
func setupTestDB(t *testing.T) *gorm.DB {
	t.Helper()

	db, err := gorm.Open(postgres.Open(testDatabaseURL()), &gorm.Config{})
	require.NoError(t, err)

	tx := db.Begin()
	t.Cleanup(func() { tx.Rollback() })
	return tx
}

func testDatabaseURL() string {
	if url := os.Getenv("DATABASE_URL_TEST"); url != "" {
		return url
	}
	return "postgresql://postgres:postgres@localhost:5432/chatbot_test?sslmode=disable"
}
```

## Running the Suite

```bash
# All chatbot tests
go test ./internal/handler/... ./internal/service/... -v

# With race detector and coverage
go test ./... -race -cover

# Just the unit tests (fast, no DB required)
go test ./internal/service/... -v
```
