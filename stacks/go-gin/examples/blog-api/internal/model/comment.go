package model

import "time"

// Comment is the GORM model representing the comments table.
type Comment struct {
	ID        string `gorm:"type:uuid;primaryKey;default:gen_random_uuid()"`
	PostID    string `gorm:"type:uuid;not null;index"`
	Content   string `gorm:"not null"`
	AuthorID  string `gorm:"type:uuid;not null"`
	CreatedAt time.Time
}

// TableName pins the table name explicitly.
func (Comment) TableName() string { return "comments" }

// CreateCommentRequest is the API request body for creating a comment.
type CreateCommentRequest struct {
	Content  string `json:"content" binding:"required,min=1,max=1000"`
	AuthorID string `json:"authorId" binding:"required,uuid"`
}

// CommentResponse is the API response body representing a comment.
type CommentResponse struct {
	CommentID string `json:"commentId"`
	PostID    string `json:"postId"`
	Content   string `json:"content"`
	AuthorID  string `json:"authorId"`
	CreatedAt string `json:"createdAt"`
}

// CommentListResponse is the API response body for a list of comments.
type CommentListResponse struct {
	Comments   []CommentResponse `json:"comments"`
	TotalCount int               `json:"totalCount"`
}

// ToCommentResponse converts a GORM Comment model to its API response DTO.
func ToCommentResponse(c *Comment) CommentResponse {
	return CommentResponse{
		CommentID: c.ID,
		PostID:    c.PostID,
		Content:   c.Content,
		AuthorID:  c.AuthorID,
		CreatedAt: c.CreatedAt.Format(time.RFC3339),
	}
}
