// Package service contains business logic, orchestrating repositories.
package service

import (
	"context"
	"errors"
	"fmt"

	"golang.org/x/crypto/bcrypt"

	"github.com/example/blog-api/internal/model"
)

// ErrUserAlreadyExists is returned when registering an email that is already taken.
var ErrUserAlreadyExists = errors.New("user already exists")

// ErrInvalidCredentials is returned when login credentials do not match.
var ErrInvalidCredentials = errors.New("invalid credentials")

// UserRepository is the persistence contract this service depends on.
type UserRepository interface {
	Create(ctx context.Context, user *model.User) error
	GetByEmail(ctx context.Context, email string) (*model.User, error)
	GetByID(ctx context.Context, id string) (*model.User, error)
}

// UserService contains business logic for user registration and authentication.
type UserService struct {
	repo UserRepository
}

// NewUserService constructs a UserService with the given repository.
func NewUserService(repo UserRepository) *UserService {
	return &UserService{repo: repo}
}

// Register creates a new user with a bcrypt-hashed password.
//
// It returns ErrUserAlreadyExists if the email is already registered.
func (s *UserService) Register(ctx context.Context, email, password, fullName string) (*model.User, error) {
	if _, err := s.repo.GetByEmail(ctx, email); err == nil {
		return nil, ErrUserAlreadyExists
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, fmt.Errorf("user service: hash password: %w", err)
	}

	user := &model.User{
		Email:        email,
		PasswordHash: string(hash),
		FullName:     fullName,
	}
	if err := s.repo.Create(ctx, user); err != nil {
		return nil, fmt.Errorf("user service: create: %w", err)
	}

	return user, nil
}

// Login verifies credentials and returns the matching user.
//
// It returns ErrInvalidCredentials if the email is unknown or the password doesn't match.
func (s *UserService) Login(ctx context.Context, email, password string) (*model.User, error) {
	user, err := s.repo.GetByEmail(ctx, email)
	if err != nil {
		return nil, ErrInvalidCredentials
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password)); err != nil {
		return nil, ErrInvalidCredentials
	}

	return user, nil
}
