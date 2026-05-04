package users

import (
	"errors"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

// UserHandler holds route handlers for the users resource.
// It depends on the UserService interface, defined at the consumer side.
type UserHandler struct {
	svc UserService
}

// NewUserHandler creates a new UserHandler.
func NewUserHandler(svc UserService) *UserHandler {
	return &UserHandler{svc: svc}
}

// RegisterRoutes registers all user routes on the given engine and returns it.
func (h *UserHandler) RegisterRoutes(r *gin.Engine) {
	r.POST("/users", h.CreateUser)
	r.GET("/users/:id", h.GetUser)
	r.GET("/users", h.ListUsers)
}

// CreateUser handles POST /users.
func (h *UserHandler) CreateUser(c *gin.Context) {
	var req struct {
		Name  string `json:"name"  binding:"required"`
		Email string `json:"email" binding:"required,email"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := h.svc.CreateUser(c.Request.Context(), req.Name, req.Email)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create user"})
		return
	}
	c.JSON(http.StatusCreated, user)
}

// GetUser handles GET /users/:id.
func (h *UserHandler) GetUser(c *gin.Context) {
	id, err := strconv.ParseInt(c.Param("id"), 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid user id"})
		return
	}

	user, err := h.svc.GetUser(c.Request.Context(), id)
	if err != nil {
		if errors.Is(err, ErrUserNotFound) {
			c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get user"})
		return
	}
	c.JSON(http.StatusOK, user)
}

// ListUsers handles GET /users.
func (h *UserHandler) ListUsers(c *gin.Context) {
	users, err := h.svc.ListUsers(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to list users"})
		return
	}
	c.JSON(http.StatusOK, users)
}

// ErrUserNotFound is returned when a user does not exist.
var ErrUserNotFound = errors.New("user not found")
