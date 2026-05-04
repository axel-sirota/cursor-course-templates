package users

import (
	"context"
	"fmt"
)

// UserService defines the business operations for users.
// Defined here at the consumer (handler) side.
type UserService interface {
	CreateUser(ctx context.Context, name, email string) (User, error)
	GetUser(ctx context.Context, id int64) (User, error)
	ListUsers(ctx context.Context) ([]User, error)
}

type userService struct {
	repo UserRepository
}

// NewUserService creates a new UserService backed by the given UserRepository.
func NewUserService(repo UserRepository) UserService {
	return &userService{repo: repo}
}

func (u *userService) CreateUser(ctx context.Context, name, email string) (User, error) {
	if name == "" {
		return User{}, fmt.Errorf("name is required")
	}
	if email == "" {
		return User{}, fmt.Errorf("email is required")
	}

	user, err := u.repo.Create(ctx, User{Name: name, Email: email})
	if err != nil {
		return User{}, fmt.Errorf("creating user: %w", err)
	}
	return user, nil
}

func (u *userService) GetUser(ctx context.Context, id int64) (User, error) {
	if id <= 0 {
		return User{}, fmt.Errorf("id must be positive")
	}

	user, err := u.repo.GetByID(ctx, id)
	if err != nil {
		return User{}, fmt.Errorf("getting user %d: %w", id, err)
	}
	return user, nil
}

func (u *userService) ListUsers(ctx context.Context) ([]User, error) {
	users, err := u.repo.List(ctx)
	if err != nil {
		return nil, fmt.Errorf("listing users: %w", err)
	}
	return users, nil
}
