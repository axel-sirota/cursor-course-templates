// Package tests contains black-box E2E tests for the blog-api reference application,
// exercising the full stack (handler -> service -> repository -> real PostgreSQL) through the
// HTTP interface only.
package tests

import (
	"os"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/require"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/example/blog-api/internal/database"
	"github.com/example/blog-api/internal/handler"
	"github.com/example/blog-api/internal/repository"
	"github.com/example/blog-api/internal/service"
)

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)
	os.Exit(m.Run())
}

// setupTestDB opens a connection to the test database and wraps the test in a transaction that
// is always rolled back on cleanup, so tests never leave residue and can run in any order.
func setupTestDB(t *testing.T) *gorm.DB {
	t.Helper()

	dsn := os.Getenv("DATABASE_URL_TEST")
	if dsn == "" {
		dsn = "postgresql://postgres:postgres@localhost:5432/blog_db_test?sslmode=disable"
	}

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	require.NoError(t, err, "connect to test database (is docker compose up -d running?)")

	require.NoError(t, database.AutoMigrate(db))

	tx := db.Begin()
	t.Cleanup(func() { tx.Rollback() })
	return tx
}

// setupRouter wires a real Gin router against the given test-transaction database.
func setupRouter(t *testing.T) *gin.Engine {
	t.Helper()

	db := setupTestDB(t)

	postRepo := repository.NewGormPostRepository(db)

	userSvc := service.NewUserService(repository.NewGormUserRepository(db))
	postSvc := service.NewPostService(postRepo)
	commentSvc := service.NewCommentService(repository.NewGormCommentRepository(db), postRepo)

	r := gin.New()
	handler.RegisterRoutes(r, db, "test", userSvc, postSvc, commentSvc)
	return r
}
