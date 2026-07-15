// Package repository contains GORM-backed data access implementations.
package repository

import (
	"context"
	"fmt"

	"gorm.io/gorm"

	"github.com/example/blog-api/internal/model"
)

// GormUserRepository is the GORM-backed implementation of user persistence.
type GormUserRepository struct {
	db *gorm.DB
}

// NewGormUserRepository constructs a GormUserRepository with the given connection.
func NewGormUserRepository(db *gorm.DB) *GormUserRepository {
	return &GormUserRepository{db: db}
}

// Create persists a new user.
func (r *GormUserRepository) Create(ctx context.Context, user *model.User) error {
	if err := r.db.WithContext(ctx).Create(user).Error; err != nil {
		return fmt.Errorf("gorm user repository: create: %w", err)
	}
	return nil
}

// GetByEmail returns the user with the given email.
func (r *GormUserRepository) GetByEmail(ctx context.Context, email string) (*model.User, error) {
	var user model.User
	if err := r.db.WithContext(ctx).First(&user, "email = ?", email).Error; err != nil {
		return nil, fmt.Errorf("gorm user repository: get by email: %w", err)
	}
	return &user, nil
}

// GetByID returns the user with the given ID.
func (r *GormUserRepository) GetByID(ctx context.Context, id string) (*model.User, error) {
	var user model.User
	if err := r.db.WithContext(ctx).First(&user, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("gorm user repository: get by id: %w", err)
	}
	return &user, nil
}
