package repository

import (
	"context"
	"fmt"

	"gorm.io/gorm"

	"github.com/example/blog-api/internal/model"
)

// GormPostRepository is the GORM-backed implementation of post persistence.
type GormPostRepository struct {
	db *gorm.DB
}

// NewGormPostRepository constructs a GormPostRepository with the given connection.
func NewGormPostRepository(db *gorm.DB) *GormPostRepository {
	return &GormPostRepository{db: db}
}

// Create persists a new post.
func (r *GormPostRepository) Create(ctx context.Context, post *model.Post) error {
	if err := r.db.WithContext(ctx).Create(post).Error; err != nil {
		return fmt.Errorf("gorm post repository: create: %w", err)
	}
	return nil
}

// GetByID returns the post with the given ID.
func (r *GormPostRepository) GetByID(ctx context.Context, id string) (*model.Post, error) {
	var post model.Post
	if err := r.db.WithContext(ctx).First(&post, "id = ?", id).Error; err != nil {
		return nil, fmt.Errorf("gorm post repository: get by id: %w", err)
	}
	return &post, nil
}

// List returns a page of posts ordered by most recent first, plus the total count.
func (r *GormPostRepository) List(ctx context.Context, limit, offset int) ([]model.Post, int64, error) {
	var posts []model.Post
	if err := r.db.WithContext(ctx).Order("created_at DESC").Limit(limit).Offset(offset).Find(&posts).Error; err != nil {
		return nil, 0, fmt.Errorf("gorm post repository: list: %w", err)
	}

	var total int64
	if err := r.db.WithContext(ctx).Model(&model.Post{}).Count(&total).Error; err != nil {
		return nil, 0, fmt.Errorf("gorm post repository: count: %w", err)
	}

	return posts, total, nil
}

// Update saves changes to an existing post.
func (r *GormPostRepository) Update(ctx context.Context, post *model.Post) error {
	if err := r.db.WithContext(ctx).Save(post).Error; err != nil {
		return fmt.Errorf("gorm post repository: update: %w", err)
	}
	return nil
}

// Delete removes a post by ID.
func (r *GormPostRepository) Delete(ctx context.Context, id string) error {
	if err := r.db.WithContext(ctx).Delete(&model.Post{}, "id = ?", id).Error; err != nil {
		return fmt.Errorf("gorm post repository: delete: %w", err)
	}
	return nil
}
