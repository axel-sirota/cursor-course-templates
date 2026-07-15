package repository

import (
	"context"
	"fmt"

	"gorm.io/gorm"

	"github.com/example/blog-api/internal/model"
)

// GormCommentRepository is the GORM-backed implementation of comment persistence.
type GormCommentRepository struct {
	db *gorm.DB
}

// NewGormCommentRepository constructs a GormCommentRepository with the given connection.
func NewGormCommentRepository(db *gorm.DB) *GormCommentRepository {
	return &GormCommentRepository{db: db}
}

// Create persists a new comment.
func (r *GormCommentRepository) Create(ctx context.Context, comment *model.Comment) error {
	if err := r.db.WithContext(ctx).Create(comment).Error; err != nil {
		return fmt.Errorf("gorm comment repository: create: %w", err)
	}
	return nil
}

// ListByPost returns all comments for a post, oldest first.
func (r *GormCommentRepository) ListByPost(ctx context.Context, postID string) ([]model.Comment, error) {
	var comments []model.Comment
	err := r.db.WithContext(ctx).
		Where("post_id = ?", postID).
		Order("created_at ASC").
		Find(&comments).Error
	if err != nil {
		return nil, fmt.Errorf("gorm comment repository: list by post: %w", err)
	}
	return comments, nil
}
