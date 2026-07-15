# Chatbot Dependencies (go.mod)

Go module dependency list for the chatbot domain example, on top of the base
`vibe/vibe_gin_boilerplate.md` dependencies. All versions pinned per
`rules/001-environment-setup.mdc` (never `@latest` in committed code).

## Install Commands

```bash
# Core web framework
go get github.com/gin-gonic/gin@v1.10.0
go get github.com/gin-contrib/cors@v1.7.2

# Database (GORM + PostgreSQL driver)
go get gorm.io/gorm@v1.25.10
go get gorm.io/driver/postgres@v1.5.9

# Configuration
go get github.com/spf13/viper@v1.19.0

# UUIDs (used for correlation IDs, test fixtures)
go get github.com/google/uuid@v1.6.0

# Testing
go get github.com/stretchr/testify@v1.9.0

# Tidy the module graph after adding all of the above
go mod tidy
```

## Resulting `go.mod` (excerpt)

```go
module github.com/example/chatbot-api

go 1.23

require (
	github.com/gin-contrib/cors v1.7.2
	github.com/gin-gonic/gin v1.10.0
	github.com/google/uuid v1.6.0
	github.com/spf13/viper v1.19.0
	github.com/stretchr/testify v1.9.0
	gorm.io/driver/postgres v1.5.9
	gorm.io/gorm v1.25.10
)
```

## Notes on Each Dependency

| Package | Purpose | Why this one |
|---|---|---|
| `gin-gonic/gin` | HTTP router/framework | Fast, minimal, the stack's chosen framework |
| `gin-contrib/cors` | CORS middleware | Official Gin-maintained CORS middleware |
| `gorm.io/gorm` | ORM | Idiomatic Go ORM with a good migration/relation story |
| `gorm.io/driver/postgres` | PostgreSQL driver for GORM | Official GORM Postgres driver (wraps `pgx`) |
| `spf13/viper` | Configuration loading | Reads `.env` + environment variables uniformly |
| `google/uuid` | UUID generation | Standard, widely-used UUID library for correlation IDs |
| `stretchr/testify` | Assertions + mocks | `assert`/`require`/`mock` — the stack's testing toolkit |

## No LLM SDK Dependency Required

The chatbot's `LLMClient` interface (see `templates/chatbot-service.md`) is implemented with the
standard library's `net/http` for the real HTTP-calling implementation, and a zero-dependency
`MockLLMClient` for Phase 0/tests. This intentionally avoids pulling in a heavyweight, frequently
-changing provider SDK — Go's standard library is enough to make one HTTP POST and parse JSON. If a
specific provider's official Go SDK is required later, add it explicitly and pin its version the same
way as everything else above.

## Optional: golang-migrate CLI (not a go.mod dependency)

If using `golang-migrate` for schema migrations (see `templates/chatbot-models.md`), install the CLI
tool separately — it is not imported by the application code:

```bash
brew install golang-migrate
# or
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest
```
