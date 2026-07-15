package service

import (
	"context"
	"fmt"

	"github.com/example/blog-api/internal/model"
)

// CommentRepository is the persistence contract this service depends on for comments.
type CommentRepository interface {
	Create(ctx context.Context, comment *model.Comment) error
	ListByPost(ctx context.Context, postID string) ([]model.Comment, error)
}

// PostExistenceChecker is the narrow persistence contract this service depends on to verify a
// parent post exists before creating or listing comments. Deliberately narrower than the full
// PostRepository interface (interface-at-point-of-use: only depend on what you actually call) —
// both *repository.GormPostRepository and any test double implement this trivially.
type PostExistenceChecker interface {
	GetByID(ctx context.Context, id string) (*model.Post, error)
}

// CommentService contains business logic for comment operations.
type CommentService struct {
	comments CommentRepository
	posts    PostExistenceChecker
}

// NewCommentService constructs a CommentService with the given repository and post checker.
// Pass a *repository.GormPostRepository (or any PostExistenceChecker), not a *PostService —
// this service only needs to verify the parent post exists, not the full post business logic.
func NewCommentService(comments CommentRepository, posts PostExistenceChecker) *CommentService {
	return &CommentService{comments: comments, posts: posts}
}

// CreateComment adds a comment to a post.
//
// It returns ErrPostNotFound if the parent post does not exist.
func (s *CommentService) CreateComment(ctx context.Context, postID, content, authorID string) (*model.Comment, error) {
	if _, err := s.posts.GetByID(ctx, postID); err != nil {
		return nil, ErrPostNotFound
	}

	comment := &model.Comment{PostID: postID, Content: content, AuthorID: authorID}
	if err := s.comments.Create(ctx, comment); err != nil {
		return nil, fmt.Errorf("comment service: create: %w", err)
	}
	return comment, nil
}

// ListComments returns all comments for a post.
//
// It returns ErrPostNotFound if the parent post does not exist.
func (s *CommentService) ListComments(ctx context.Context, postID string) ([]model.Comment, error) {
	if _, err := s.posts.GetByID(ctx, postID); err != nil {
		return nil, ErrPostNotFound
	}

	comments, err := s.comments.ListByPost(ctx, postID)
	if err != nil {
		return nil, fmt.Errorf("comment service: list by post: %w", err)
	}
	return comments, nil
}
