// Test Scenarios with Expected Input/Output
// Use these as examples when teaching students about E2E testing in Go.
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

// --- Authentication Scenarios ---

// TestRegisterNewUserSuccess
//
// Scenario: Register a new user successfully
//
// Input:
//
//	POST /api/auth/register
//	{"email": "johndoe@example.com", "password": "secure123", "fullName": "John Doe"}
//
// Expected Output:
//
//	Status: 201
//	{"message": "Registration successful", "user": {"userId": "<uuid>", "email": "...", ...}}
func TestRegisterNewUserSuccess(t *testing.T) {
	router := setupRouter(t)

	body, _ := json.Marshal(model.RegisterRequest{
		Email: "johndoe@example.com", Password: "secure123", FullName: "John Doe",
	})
	req := httptest.NewRequest(http.MethodPost, "/api/auth/register", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	require.Equal(t, http.StatusCreated, w.Code)

	var resp model.AuthResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, "Registration successful", resp.Message)
	assert.Equal(t, "johndoe@example.com", resp.User.Email)
	assert.Len(t, resp.User.UserID, 36) // UUID format
}

// TestRegisterDuplicateEmail
//
// Scenario: Try to register with an already-taken email
//
// Input:
//
//	First:  POST /api/auth/register {"email": "dup@example.com", ...}
//	Second: POST /api/auth/register {"email": "dup@example.com", ...}
//
// Expected Output:
//
//	First:  201 success
//	Second: 400 error with message about the user already existing
func TestRegisterDuplicateEmail(t *testing.T) {
	router := setupRouter(t)

	body, _ := json.Marshal(model.RegisterRequest{Email: "dup@example.com", Password: "pass1234", FullName: "First"})
	req1 := httptest.NewRequest(http.MethodPost, "/api/auth/register", bytes.NewBuffer(body))
	req1.Header.Set("Content-Type", "application/json")
	w1 := httptest.NewRecorder()
	router.ServeHTTP(w1, req1)
	require.Equal(t, http.StatusCreated, w1.Code)

	req2 := httptest.NewRequest(http.MethodPost, "/api/auth/register", bytes.NewBuffer(body))
	req2.Header.Set("Content-Type", "application/json")
	w2 := httptest.NewRecorder()
	router.ServeHTTP(w2, req2)

	assert.Equal(t, http.StatusBadRequest, w2.Code)
	assert.Contains(t, w2.Body.String(), "already exists")
}

// TestLoginSuccess
//
// Scenario: Login with correct credentials
//
// Input:
//
//	Setup: Register user email="alice@example.com" password="wonderland1"
//	Then:  POST /api/auth/login {"email": "alice@example.com", "password": "wonderland1"}
//
// Expected Output:
//
//	Status: 200
//	{"message": "Login successful", "user": {...}}
func TestLoginSuccess(t *testing.T) {
	router := setupRouter(t)
	registerTestUser(t, router, "alice@example.com", "wonderland1")

	body, _ := json.Marshal(model.LoginRequest{Email: "alice@example.com", Password: "wonderland1"})
	req := httptest.NewRequest(http.MethodPost, "/api/auth/login", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	require.Equal(t, http.StatusOK, w.Code)
	var resp model.AuthResponse
	require.NoError(t, json.Unmarshal(w.Body.Bytes(), &resp))
	assert.Equal(t, "Login successful", resp.Message)
}

// TestLoginWrongPassword
//
// Scenario: Login with an incorrect password
//
// Input:
//
//	Setup: Register user email="bob@example.com" password="correct123"
//	Then:  POST /api/auth/login {"email": "bob@example.com", "password": "wrong123"}
//
// Expected Output:
//
//	Status: 401
//	{"error": "invalid credentials"}
func TestLoginWrongPassword(t *testing.T) {
	router := setupRouter(t)
	registerTestUser(t, router, "bob@example.com", "correct123")

	body, _ := json.Marshal(model.LoginRequest{Email: "bob@example.com", Password: "wrong123"})
	req := httptest.NewRequest(http.MethodPost, "/api/auth/login", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

// --- Post Scenarios ---

// TestCreatePostThenRetrieve
//
// Scenario: Create a post, then retrieve it by ID and confirm all fields round-trip correctly
//
// Input:
//
//	Setup: Register author
//	POST /api/posts {"title": "My First Post", "content": "Hello, world!", "authorId": "<uuid>"}
//	Then: GET /api/posts/{postId}
//
// Expected Output:
//
//	POST: 201, response includes generated postId and createdAt
//	GET: 200, response matches the created post exactly
func TestCreatePostThenRetrieve(t *testing.T) {
	router := setupRouter(t)
	authorID := registerTestUser(t, router, "author-scenario@example.com", "securepass123")

	createBody, _ := json.Marshal(model.CreatePostRequest{
		Title: "My First Post", Content: "Hello, world!", AuthorID: authorID,
	})
	createReq := httptest.NewRequest(http.MethodPost, "/api/posts", bytes.NewBuffer(createBody))
	createReq.Header.Set("Content-Type", "application/json")
	createW := httptest.NewRecorder()
	router.ServeHTTP(createW, createReq)
	require.Equal(t, http.StatusCreated, createW.Code)

	var created model.PostResponse
	require.NoError(t, json.Unmarshal(createW.Body.Bytes(), &created))
	assert.NotEmpty(t, created.PostID)
	assert.NotEmpty(t, created.CreatedAt)

	getReq := httptest.NewRequest(http.MethodGet, "/api/posts/"+created.PostID, nil)
	getW := httptest.NewRecorder()
	router.ServeHTTP(getW, getReq)
	require.Equal(t, http.StatusOK, getW.Code)

	var fetched model.PostResponse
	require.NoError(t, json.Unmarshal(getW.Body.Bytes(), &fetched))
	assert.Equal(t, created.PostID, fetched.PostID)
	assert.Equal(t, "My First Post", fetched.Title)
	assert.Equal(t, "Hello, world!", fetched.Content)
}

// TestGetNonexistentPost
//
// Scenario: Request a post ID that does not exist
//
// Input:
//
//	GET /api/posts/00000000-0000-0000-0000-000000000000
//
// Expected Output:
//
//	Status: 404
//	{"error": "post not found"}
func TestGetNonexistentPost(t *testing.T) {
	router := setupRouter(t)

	req := httptest.NewRequest(http.MethodGet, "/api/posts/00000000-0000-0000-0000-000000000000", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
	assert.Contains(t, w.Body.String(), "post not found")
}

// TestUpdatePostPartial
//
// Scenario: Update only the title of an existing post, leaving content unchanged
//
// Input:
//
//	Setup: Create post with title="Original", content="Original content"
//	PUT /api/posts/{id} {"title": "Updated Title"}
//
// Expected Output:
//
//	Status: 200
//	Response: title="Updated Title", content="Original content" (unchanged)
func TestUpdatePostPartial(t *testing.T) {
	router := setupRouter(t)
	postID := createTestPost(t, router)

	newTitle := "Updated Title"
	updateBody, _ := json.Marshal(model.UpdatePostRequest{Title: &newTitle})
	updateReq := httptest.NewRequest(http.MethodPut, "/api/posts/"+postID, bytes.NewBuffer(updateBody))
	updateReq.Header.Set("Content-Type", "application/json")
	updateW := httptest.NewRecorder()
	router.ServeHTTP(updateW, updateReq)

	require.Equal(t, http.StatusOK, updateW.Code)
	var updated model.PostResponse
	require.NoError(t, json.Unmarshal(updateW.Body.Bytes(), &updated))
	assert.Equal(t, "Updated Title", updated.Title)
	assert.Equal(t, "Fixture content", updated.Content) // unchanged
}

// TestDeletePostThenGetReturns404
//
// Scenario: Delete a post, then confirm it can no longer be retrieved
//
// Input:
//
//	Setup: Create post
//	DELETE /api/posts/{id}
//	Then: GET /api/posts/{id}
//
// Expected Output:
//
//	DELETE: 204 (no body)
//	GET: 404
func TestDeletePostThenGetReturns404(t *testing.T) {
	router := setupRouter(t)
	postID := createTestPost(t, router)

	deleteReq := httptest.NewRequest(http.MethodDelete, "/api/posts/"+postID, nil)
	deleteW := httptest.NewRecorder()
	router.ServeHTTP(deleteW, deleteReq)
	require.Equal(t, http.StatusNoContent, deleteW.Code)

	getReq := httptest.NewRequest(http.MethodGet, "/api/posts/"+postID, nil)
	getW := httptest.NewRecorder()
	router.ServeHTTP(getW, getReq)
	assert.Equal(t, http.StatusNotFound, getW.Code)
}

// --- Comment Scenarios ---

// TestCreateCommentOnNonexistentPost
//
// Scenario: Try to comment on a post that doesn't exist
//
// Input:
//
//	Setup: Register author
//	POST /api/posts/00000000-0000-0000-0000-000000000000/comments {"content": "...", "authorId": "<uuid>"}
//
// Expected Output:
//
//	Status: 404
//	{"error": "post not found"}
func TestCreateCommentOnNonexistentPost(t *testing.T) {
	router := setupRouter(t)
	authorID := registerTestUser(t, router, "comment-scenario-author@example.com", "securepass123")

	body, _ := json.Marshal(model.CreateCommentRequest{Content: "Nice post!", AuthorID: authorID})
	req := httptest.NewRequest(http.MethodPost, "/api/posts/00000000-0000-0000-0000-000000000000/comments", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNotFound, w.Code)
}

// TestListCommentsOrderedChronologically
//
// Scenario: Multiple comments on a post are returned in creation order
//
// Input:
//
//	Setup: Create post, add 2 comments in sequence ("First!" then "Second!")
//	GET /api/posts/{id}/comments
//
// Expected Output:
//
//	Status: 200
//	{"comments": [{"content": "First!"}, {"content": "Second!"}], "totalCount": 2}
func TestListCommentsOrderedChronologically(t *testing.T) {
	router := setupRouter(t)
	postID := createTestPost(t, router)
	authorID := registerTestUser(t, router, "commenter@example.com", "securepass123")

	for _, content := range []string{"First!", "Second!"} {
		body, _ := json.Marshal(model.CreateCommentRequest{Content: content, AuthorID: authorID})
		req := httptest.NewRequest(http.MethodPost, "/api/posts/"+postID+"/comments", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		require.Equal(t, http.StatusCreated, w.Code)
	}

	listReq := httptest.NewRequest(http.MethodGet, "/api/posts/"+postID+"/comments", nil)
	listW := httptest.NewRecorder()
	router.ServeHTTP(listW, listReq)
	require.Equal(t, http.StatusOK, listW.Code)

	var resp model.CommentListResponse
	require.NoError(t, json.Unmarshal(listW.Body.Bytes(), &resp))
	require.Len(t, resp.Comments, 2)
	assert.Equal(t, "First!", resp.Comments[0].Content)
	assert.Equal(t, "Second!", resp.Comments[1].Content)
	assert.Equal(t, 2, resp.TotalCount)
}
