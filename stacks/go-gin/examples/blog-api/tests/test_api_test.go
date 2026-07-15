// Basic E2E smoke tests — one straightforward test per endpoint. See test_scenarios_test.go for
// detailed, documented input/output scenarios used when teaching E2E testing.
package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/example/blog-api/internal/model"
)

func TestHealthCheck(t *testing.T) {
	router := setupRouter(t)

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
	assert.Contains(t, w.Body.String(), `"status":"healthy"`)
}

func TestRegister(t *testing.T) {
	router := setupRouter(t)

	body, _ := json.Marshal(model.RegisterRequest{
		Email: "smoke-register@example.com", Password: "securepass123", FullName: "Smoke Test",
	})
	req := httptest.NewRequest(http.MethodPost, "/api/auth/register", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)
}

func TestLogin(t *testing.T) {
	router := setupRouter(t)
	registerTestUser(t, router, "smoke-login@example.com", "securepass123")

	body, _ := json.Marshal(model.LoginRequest{Email: "smoke-login@example.com", Password: "securepass123"})
	req := httptest.NewRequest(http.MethodPost, "/api/auth/login", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

func TestCreatePost(t *testing.T) {
	router := setupRouter(t)
	authorID := registerTestUser(t, router, "smoke-post-author@example.com", "securepass123")

	body, _ := json.Marshal(model.CreatePostRequest{Title: "Smoke Post", Content: "Content", AuthorID: authorID})
	req := httptest.NewRequest(http.MethodPost, "/api/posts", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)
}

func TestGetPost(t *testing.T) {
	router := setupRouter(t)
	postID := createTestPost(t, router)

	req := httptest.NewRequest(http.MethodGet, "/api/posts/"+postID, nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

func TestCreateComment(t *testing.T) {
	router := setupRouter(t)
	postID := createTestPost(t, router)
	authorID := registerTestUser(t, router, "smoke-comment-author@example.com", "securepass123")

	body, _ := json.Marshal(model.CreateCommentRequest{Content: "Nice post!", AuthorID: authorID})
	req := httptest.NewRequest(http.MethodPost, "/api/posts/"+postID+"/comments", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusCreated, w.Code)
}

func TestListComments(t *testing.T) {
	router := setupRouter(t)
	postID := createTestPost(t, router)

	req := httptest.NewRequest(http.MethodGet, "/api/posts/"+postID+"/comments", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)
}

// --- shared test helpers ---

func registerTestUser(t *testing.T, router http.Handler, email, password string) (userID string) {
	t.Helper()
	body, _ := json.Marshal(model.RegisterRequest{Email: email, Password: password, FullName: "Test User"})
	req := httptest.NewRequest(http.MethodPost, "/api/auth/register", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	require.Equal(t, http.StatusCreated, w.Code)

	var resp model.AuthResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	return resp.User.UserID
}

func createTestPost(t *testing.T, router http.Handler) (postID string) {
	t.Helper()
	authorID := registerTestUser(t, router, "post-fixture-author@example.com", "securepass123")

	body, _ := json.Marshal(model.CreatePostRequest{Title: "Fixture Post", Content: "Fixture content", AuthorID: authorID})
	req := httptest.NewRequest(http.MethodPost, "/api/posts", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)
	require.Equal(t, http.StatusCreated, w.Code)

	var resp model.PostResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	return resp.PostID
}
