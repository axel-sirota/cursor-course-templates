package handler

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/example/blog-api/internal/model"
	"github.com/example/blog-api/internal/service"
)

// Register handles POST /api/auth/register.
func Register(svc *service.UserService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.RegisterRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		user, err := svc.Register(c.Request.Context(), req.Email, req.Password, req.FullName)
		if err != nil {
			if errors.Is(err, service.ErrUserAlreadyExists) {
				c.JSON(http.StatusBadRequest, gin.H{"error": "user already exists"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "registration failed"})
			return
		}

		c.JSON(http.StatusCreated, model.AuthResponse{
			Message: "Registration successful",
			User:    model.ToUserResponse(user),
		})
	}
}

// Login handles POST /api/auth/login.
func Login(svc *service.UserService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.LoginRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		user, err := svc.Login(c.Request.Context(), req.Email, req.Password)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
			return
		}

		c.JSON(http.StatusOK, model.AuthResponse{
			Message: "Login successful",
			User:    model.ToUserResponse(user),
		})
	}
}
