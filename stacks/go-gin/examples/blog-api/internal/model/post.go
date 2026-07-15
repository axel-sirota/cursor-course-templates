package model

import "time"

// Post is the GORM model representing the posts table.
type Post struct {
	ID        string `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
	Title     string `gorm:"not null"`
	Content   string `gorm:"not null"`
	AuthorID  string `gorm:"type:uuid;not null;index"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

// TableName pins the table name explicitly.
func (Post) TableName() string { return "posts" }

// CreatePostRequest is the API request body for creating a post.
type CreatePostRequest struct {
	Title    string `json:"title" binding:"required,min=1,max=200"`
	Content  string `json:"content" binding:"required,min=1,max=10000"`
	AuthorID string `json:"authorId" binding:"required,uuid"`
}

// UpdatePostRequest is the API request body for updating a post. Pointer fields distinguish
// "not provided" from "explicitly set to empty" for partial updates.
type UpdatePostRequest struct {
	Title   *string `json:"title" binding:"omitempty,min=1,max=200"`
	Content *string `json:"content" binding:"omitempty,min=1,max=10000"`
}

// PostResponse is the API response body representing a post.
type PostResponse struct {
	PostID    string  `json:"postId"`
	Title     string  `json:"title"`
	Content   string  `json:"content"`
	AuthorID  string  `json:"authorId"`
	CreatedAt string  `json:"createdAt"`
	UpdatedAt *string `json:"updatedAt,omitempty"`
}

// PostListResponse is the API response body for a paginated list of posts.
type PostListResponse struct {
	Posts      []PostResponse `json:"posts"`
	TotalCount int            `json:"totalCount"`
	HasMore    bool           `json:"hasMore"`
}

// ToPostResponse converts a GORM Post model to its API response DTO.
func ToPostResponse(p *Post) PostResponse {
	resp := PostResponse{
		PostID:    p.ID,
		Title:     p.Title,
		Content:   p.Content,
		AuthorID:  p.AuthorID,
		CreatedAt: p.CreatedAt.Format(time.RFC3339),
	}
	if !p.UpdatedAt.IsZero() {
		updated := p.UpdatedAt.Format(time.RFC3339)
		resp.UpdatedAt = &updated
	}
	return resp
}
