package users

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

// mockUserService is a hand-written mock for UserService.
// In a real project, generate this with: mockery --name=UserService
type mockUserService struct {
	createUserFn func(ctx context.Context, name, email string) (User, error)
	getUserFn    func(ctx context.Context, id int64) (User, error)
	listUsersFn  func(ctx context.Context) ([]User, error)
}

func (m *mockUserService) CreateUser(ctx context.Context, name, email string) (User, error) {
	return m.createUserFn(ctx, name, email)
}

func (m *mockUserService) GetUser(ctx context.Context, id int64) (User, error) {
	return m.getUserFn(ctx, id)
}

func (m *mockUserService) ListUsers(ctx context.Context) ([]User, error) {
	return m.listUsersFn(ctx)
}

func setupRouter(svc UserService) *gin.Engine {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	h := NewUserHandler(svc)
	h.RegisterRoutes(r)
	return r
}

func TestCreateUser(t *testing.T) {
	fixedTime := time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC)

	tests := []struct {
		name           string
		requestBody    map[string]string
		mockFn         func(ctx context.Context, name, email string) (User, error)
		expectedStatus int
		expectedBody   map[string]interface{}
	}{
		{
			name:        "success",
			requestBody: map[string]string{"name": "Alice", "email": "alice@example.com"},
			mockFn: func(ctx context.Context, name, email string) (User, error) {
				return User{ID: 1, Name: name, Email: email, CreatedAt: fixedTime}, nil
			},
			expectedStatus: http.StatusCreated,
			expectedBody:   map[string]interface{}{"id": float64(1), "name": "Alice", "email": "alice@example.com"},
		},
		{
			name:           "missing name",
			requestBody:    map[string]string{"email": "alice@example.com"},
			mockFn:         nil,
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:           "missing email",
			requestBody:    map[string]string{"name": "Alice"},
			mockFn:         nil,
			expectedStatus: http.StatusBadRequest,
		},
		{
			name:        "invalid email format",
			requestBody: map[string]string{"name": "Alice", "email": "not-an-email"},
			mockFn:      nil,
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			svc := &mockUserService{}
			if tc.mockFn != nil {
				svc.createUserFn = tc.mockFn
			}

			r := setupRouter(svc)
			body, _ := json.Marshal(tc.requestBody)
			req := httptest.NewRequest(http.MethodPost, "/users", bytes.NewBuffer(body))
			req.Header.Set("Content-Type", "application/json")
			w := httptest.NewRecorder()

			r.ServeHTTP(w, req)

			assert.Equal(t, tc.expectedStatus, w.Code)
			if tc.expectedBody != nil {
				var got map[string]interface{}
				err := json.Unmarshal(w.Body.Bytes(), &got)
				assert.NoError(t, err)
				for k, v := range tc.expectedBody {
					assert.Equal(t, v, got[k])
				}
			}
		})
	}
}

func TestGetUser(t *testing.T) {
	fixedTime := time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC)

	tests := []struct {
		name           string
		urlParam       string
		mockFn         func(ctx context.Context, id int64) (User, error)
		expectedStatus int
	}{
		{
			name:     "success",
			urlParam: "/users/1",
			mockFn: func(ctx context.Context, id int64) (User, error) {
				return User{ID: 1, Name: "Alice", Email: "alice@example.com", CreatedAt: fixedTime}, nil
			},
			expectedStatus: http.StatusOK,
		},
		{
			name:     "not found",
			urlParam: "/users/999",
			mockFn: func(ctx context.Context, id int64) (User, error) {
				return User{}, ErrUserNotFound
			},
			expectedStatus: http.StatusNotFound,
		},
		{
			name:           "invalid id",
			urlParam:       "/users/abc",
			mockFn:         nil,
			expectedStatus: http.StatusBadRequest,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			svc := &mockUserService{}
			if tc.mockFn != nil {
				svc.getUserFn = tc.mockFn
			}

			r := setupRouter(svc)
			req := httptest.NewRequest(http.MethodGet, tc.urlParam, nil)
			w := httptest.NewRecorder()

			r.ServeHTTP(w, req)

			assert.Equal(t, tc.expectedStatus, w.Code)
		})
	}
}

func TestListUsers(t *testing.T) {
	fixedTime := time.Date(2024, 1, 1, 0, 0, 0, 0, time.UTC)

	tests := []struct {
		name           string
		mockFn         func(ctx context.Context) ([]User, error)
		expectedStatus int
		expectedCount  int
	}{
		{
			name: "returns list",
			mockFn: func(ctx context.Context) ([]User, error) {
				return []User{
					{ID: 1, Name: "Alice", Email: "alice@example.com", CreatedAt: fixedTime},
					{ID: 2, Name: "Bob", Email: "bob@example.com", CreatedAt: fixedTime},
				}, nil
			},
			expectedStatus: http.StatusOK,
			expectedCount:  2,
		},
		{
			name: "returns empty list",
			mockFn: func(ctx context.Context) ([]User, error) {
				return []User{}, nil
			},
			expectedStatus: http.StatusOK,
			expectedCount:  0,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			svc := &mockUserService{listUsersFn: tc.mockFn}

			r := setupRouter(svc)
			req := httptest.NewRequest(http.MethodGet, "/users", nil)
			w := httptest.NewRecorder()

			r.ServeHTTP(w, req)

			assert.Equal(t, tc.expectedStatus, w.Code)

			var got []map[string]interface{}
			err := json.Unmarshal(w.Body.Bytes(), &got)
			assert.NoError(t, err)
			assert.Len(t, got, tc.expectedCount)
		})
	}
}
