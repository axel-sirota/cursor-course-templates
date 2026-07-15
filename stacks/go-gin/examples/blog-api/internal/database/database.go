// Package database manages the GORM connection pool and schema migration.
package database

import (
	"fmt"
	"time"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"github.com/example/blog-api/internal/model"
)

// Connect opens a GORM connection to PostgreSQL with a tuned connection pool.
func Connect(databaseURL string, debug bool) (*gorm.DB, error) {
	logLevel := logger.Silent
	if debug {
		logLevel = logger.Info
	}

	db, err := gorm.Open(postgres.Open(databaseURL), &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	})
	if err != nil {
		return nil, fmt.Errorf("database: connect: %w", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("database: get underlying sql.DB: %w", err)
	}

	sqlDB.SetMaxOpenConns(25)
	sqlDB.SetMaxIdleConns(25)
	sqlDB.SetConnMaxLifetime(5 * time.Minute)

	return db, nil
}

// AutoMigrate creates/updates tables for all domain models. Used for local development;
// production deployments should prefer versioned golang-migrate files (see migrations/).
func AutoMigrate(db *gorm.DB) error {
	if err := db.AutoMigrate(&model.User{}, &model.Post{}, &model.Comment{}); err != nil {
		return fmt.Errorf("database: automigrate: %w", err)
	}
	return nil
}

// Ping verifies the database connection is alive. Used by the health endpoint.
func Ping(db *gorm.DB) error {
	sqlDB, err := db.DB()
	if err != nil {
		return fmt.Errorf("database: get underlying sql.DB: %w", err)
	}
	return sqlDB.Ping()
}
