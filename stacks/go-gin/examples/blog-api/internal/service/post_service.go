package service

import (
	"context"
	"errors"
	"fmt"

	"github.com/example/blog-api/internal/model"
)

// ErrPostNotFound is returned when a post does not exist.
var ErrPostNotFound = errors.New("post not found")

// PostRepository is the persistence contract this service depends on.
type PostRepository interface {
	Create(ctx context.Context, post *model.Post) error
	GetByID(ctx context.Context, id string) (*model.Post, error)
	List(ctx context.Context, limit, offset int) ([]model.Post, int64, error)
	Update(ctx context.Context, post *model.Post) error
	Delete(ctx context.Context, id string) error
}

// PostService contains business logic for blog post operations.
type PostService struct {
	repo PostRepository
}

// NewPostService constructs a PostService with the given repository.
func NewPostService(repo PostRepository) *PostService {
	return &PostService{repo: repo}
}

// CreatePost validates and persists a new post.
func (s *PostService) CreatePost(ctx context.Context, title, content, authorID string) (*model.Post, error) {
	post := &model.Post{Title: title, Content: content, AuthorID: authorID}
	if err := s.repo.Create(ctx, post); err != nil {
		return nil, fmt.Errorf("post service: create: %w", err)
	}
	return post, nil
}

// GetPostByID retrieves a post by ID.
//
// It returns ErrPostNotFound if no post matches.
func (s *PostService) GetPostByID(ctx context.Context, id string) (*model.Post, error) {
	post, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, ErrPostNotFound
	}
	return post, nil
}

// ListPosts returns a page of posts and the total count.
func (s *PostService) ListPosts(ctx context.Context, limit, offset int) ([]model.Post, int64, error) {
	posts, total, err := s.repo.List(ctx, limit, offset)
	if err != nil {
		return nil, 0, fmt.Errorf("post service: list: %w", err)
	}
	return posts, total, nil
}

// UpdatePost applies partial updates to an existing post.
//
// It returns ErrPostNotFound if no post matches the given ID.
func (s *PostService) UpdatePost(ctx context.Context, id string, title, content *string) (*model.Post, error) {
	post, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, ErrPostNotFound
	}

	if title != nil {
		post.Title = *title
	}
	if content != nil {
		post.Content = *content
	}

	if err := s.repo.Update(ctx, post); err != nil {
		return nil, fmt.Errorf("post service: update: %w", err)
	}
	return post, nil
}

// DeletePost removes a post by ID.
//
// It returns ErrPostNotFound if no post matches the given ID.
func (s *PostService) DeletePost(ctx context.Context, id string) error {
	if _, err := s.repo.GetByID(ctx, id); err != nil {
		return ErrPostNotFound
	}
	if err := s.repo.Delete(ctx, id); err != nil {
		return fmt.Errorf("post service: delete: %w", err)
	}
	return nil
}
