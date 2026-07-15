// Package model contains GORM models (DB layer) and API DTOs (request/response layer).
package model

import "time"

// User is the GORM model representing the users table.
type User struct {
	ID           string `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
	Email        string `gorm:"uniqueIndex;not null"`
	PasswordHash string `gorm:"not null"`
	FullName     string `gorm:"not null"`
	CreatedAt    time.Time
}

// TableName pins the table name explicitly.
func (User) TableName() string { return "users" }

// RegisterRequest is the API request body for user registration.
type RegisterRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=8"`
	FullName string `json:"fullName" binding:"required"`
}

// LoginRequest is the API request body for authentication.
type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
}

// AuthResponse is the API response body for register/login.
type AuthResponse struct {
	Message string       `json:"message"`
	User    UserResponse `json:"user"`
}

// UserResponse is the API response body representing a user (never includes PasswordHash).
type UserResponse struct {
	UserID    string `json:"userId"`
	Email     string `json:"email"`
	FullName  string `json:"fullName"`
	CreatedAt string `json:"createdAt"`
}

// ToUserResponse converts a GORM User model to its API response DTO.
func ToUserResponse(u *User) UserResponse {
	return UserResponse{
		UserID:    u.ID,
		Email:     u.Email,
		FullName:  u.FullName,
		CreatedAt: u.CreatedAt.Format(time.RFC3339),
	}
}
