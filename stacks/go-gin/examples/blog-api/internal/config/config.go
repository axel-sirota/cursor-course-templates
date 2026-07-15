// Package config loads application configuration from environment variables.
package config

import (
	"fmt"
	"strings"

	"github.com/spf13/viper"
)

// Config holds all application configuration, loaded once at startup.
type Config struct {
	Port           string
	LogLevel       string
	DatabaseURL    string
	AllowedOrigins []string
}

// Load reads configuration from .env (if present) and the environment, validates required
// fields, and returns a populated Config.
//
// It returns an error if DATABASE_URL is missing.
func Load() (*Config, error) {
	viper.SetConfigFile(".env")
	viper.AutomaticEnv()
	_ = viper.ReadInConfig() // .env is optional; environment variables still work without it

	viper.SetDefault("PORT", "8080")
	viper.SetDefault("LOG_LEVEL", "info")
	viper.SetDefault("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080")

	cfg := &Config{
		Port:           viper.GetString("PORT"),
		LogLevel:       viper.GetString("LOG_LEVEL"),
		DatabaseURL:    viper.GetString("DATABASE_URL"),
		AllowedOrigins: strings.Split(viper.GetString("ALLOWED_ORIGINS"), ","),
	}

	if cfg.DatabaseURL == "" {
		return nil, fmt.Errorf("config: DATABASE_URL is required")
	}

	return cfg, nil
}
