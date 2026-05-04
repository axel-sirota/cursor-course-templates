# Project Context: Go Gin

## Tech Stack
- **Language**: Go 1.21+
- **Framework**: Gin Gonic
- **Database**: PostgreSQL (GORM or sqlx)
- **Testing**: `testing` package, `testify` (assertions), `mock`
- **Linting**: `golangci-lint`

## Vibe & Style
- **Coding Style**: Standard `gofmt`. Short variable names where idiomatic.
- **Architecture**: Standard Go Layout.
  - `cmd/app/` (Entrypoint)
  - `internal/handler/` (Gin Handlers)
  - `internal/service/` (Business Logic)
  - `internal/repository/` (Data Access)
  - `pkg/` (Public libraries)

## Key Rules
- **Error Handling**: Explicit `if err != nil`. No panics allowed in handlers.
- **Interfaces**: Define interfaces where usage happens (Consumer side).
- **Context**: Always propagate `context.Context` through all layers.
- **Config**: Use `viper` or standard `os.Getenv` for configuration.

## Architecture Shape
REST API — Gin HTTP server. Layered: handler → service → repository → model.
Also applicable to: CLI tools (swap handler layer for cobra commands), gRPC services (see `go-grpc` stack).

## Active Phase
- Current: Phase 0 (Skeleton)

