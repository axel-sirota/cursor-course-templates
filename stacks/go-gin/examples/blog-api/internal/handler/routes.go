package handler

import (
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"

	"github.com/example/blog-api/internal/service"
)

// RegisterRoutes wires all handlers into the given router, injecting their dependencies via
// factory functions (no global state).
func RegisterRoutes(
	r *gin.Engine,
	db *gorm.DB,
	environment string,
	userSvc *service.UserService,
	postSvc *service.PostService,
	commentSvc *service.CommentService,
) {
	r.GET("/health", HealthCheck(db, environment))

	api := r.Group("/api")
	{
		auth := api.Group("/auth")
		{
			auth.POST("/register", Register(userSvc))
			auth.POST("/login", Login(userSvc))
		}

		posts := api.Group("/posts")
		{
			posts.POST("", CreatePost(postSvc))
			posts.GET("", ListPosts(postSvc))
			posts.GET("/:id", GetPost(postSvc))
			posts.PUT("/:id", UpdatePost(postSvc))
			posts.DELETE("/:id", DeletePost(postSvc))

			posts.POST("/:id/comments", CreateComment(commentSvc))
			posts.GET("/:id/comments", ListComments(commentSvc))
		}
	}
}
