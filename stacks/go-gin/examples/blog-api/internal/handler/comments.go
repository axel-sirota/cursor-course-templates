package handler

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/example/blog-api/internal/model"
	"github.com/example/blog-api/internal/service"
)

// CreateComment handles POST /api/posts/:id/comments.
func CreateComment(svc *service.CommentService) gin.HandlerFunc {
	return func(c *gin.Context) {
		postID := c.Param("id")

		var req model.CreateCommentRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		comment, err := svc.CreateComment(c.Request.Context(), postID, req.Content, req.AuthorID)
		if err != nil {
			if errors.Is(err, service.ErrPostNotFound) {
				c.JSON(http.StatusNotFound, gin.H{"error": "post not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create comment"})
			return
		}

		c.JSON(http.StatusCreated, model.ToCommentResponse(comment))
	}
}

// ListComments handles GET /api/posts/:id/comments.
func ListComments(svc *service.CommentService) gin.HandlerFunc {
	return func(c *gin.Context) {
		postID := c.Param("id")

		comments, err := svc.ListComments(c.Request.Context(), postID)
		if err != nil {
			if errors.Is(err, service.ErrPostNotFound) {
				c.JSON(http.StatusNotFound, gin.H{"error": "post not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to list comments"})
			return
		}

		responses := make([]model.CommentResponse, 0, len(comments))
		for i := range comments {
			responses = append(responses, model.ToCommentResponse(&comments[i]))
		}

		c.JSON(http.StatusOK, model.CommentListResponse{
			Comments:   responses,
			TotalCount: len(responses),
		})
	}
}
