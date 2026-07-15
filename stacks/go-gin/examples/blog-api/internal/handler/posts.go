package handler

import (
	"errors"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"

	"github.com/example/blog-api/internal/model"
	"github.com/example/blog-api/internal/service"
)

// CreatePost handles POST /api/posts.
func CreatePost(svc *service.PostService) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req model.CreatePostRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		post, err := svc.CreatePost(c.Request.Context(), req.Title, req.Content, req.AuthorID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create post"})
			return
		}

		c.JSON(http.StatusCreated, model.ToPostResponse(post))
	}
}

// GetPost handles GET /api/posts/:id.
func GetPost(svc *service.PostService) gin.HandlerFunc {
	return func(c *gin.Context) {
		postID := c.Param("id")

		post, err := svc.GetPostByID(c.Request.Context(), postID)
		if err != nil {
			if errors.Is(err, service.ErrPostNotFound) {
				c.JSON(http.StatusNotFound, gin.H{"error": "post not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		c.JSON(http.StatusOK, model.ToPostResponse(post))
	}
}

// ListPosts handles GET /api/posts.
func ListPosts(svc *service.PostService) gin.HandlerFunc {
	return func(c *gin.Context) {
		limit, offset := parsePagination(c)

		posts, total, err := svc.ListPosts(c.Request.Context(), limit, offset)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to list posts"})
			return
		}

		responses := make([]model.PostResponse, 0, len(posts))
		for i := range posts {
			responses = append(responses, model.ToPostResponse(&posts[i]))
		}

		c.JSON(http.StatusOK, model.PostListResponse{
			Posts:      responses,
			TotalCount: int(total),
			HasMore:    int64(offset+limit) < total,
		})
	}
}

// UpdatePost handles PUT /api/posts/:id.
func UpdatePost(svc *service.PostService) gin.HandlerFunc {
	return func(c *gin.Context) {
		postID := c.Param("id")

		var req model.UpdatePostRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		post, err := svc.UpdatePost(c.Request.Context(), postID, req.Title, req.Content)
		if err != nil {
			if errors.Is(err, service.ErrPostNotFound) {
				c.JSON(http.StatusNotFound, gin.H{"error": "post not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		c.JSON(http.StatusOK, model.ToPostResponse(post))
	}
}

// DeletePost handles DELETE /api/posts/:id.
func DeletePost(svc *service.PostService) gin.HandlerFunc {
	return func(c *gin.Context) {
		postID := c.Param("id")

		if err := svc.DeletePost(c.Request.Context(), postID); err != nil {
			if errors.Is(err, service.ErrPostNotFound) {
				c.JSON(http.StatusNotFound, gin.H{"error": "post not found"})
				return
			}
			c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
			return
		}

		c.Status(http.StatusNoContent)
	}
}

// parsePagination reads limit/offset query parameters with sane defaults and bounds.
func parsePagination(c *gin.Context) (limit, offset int) {
	limit, offset = 20, 0
	if l, err := strconv.Atoi(c.Query("limit")); err == nil && l > 0 && l <= 100 {
		limit = l
	}
	if o, err := strconv.Atoi(c.Query("offset")); err == nil && o >= 0 {
		offset = o
	}
	return limit, offset
}
