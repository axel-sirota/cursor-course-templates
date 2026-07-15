# Go/Gin Stack Examples — Teacher Index

This folder contains complete, working reference applications demonstrating the go-gin stack's
phase-based workflow, rules, and vibe guides in practice.

## What's Here

### blog-api/

A complete working Gin blog application: user registration/login, posts (full CRUD), and comments.

**Features implemented:**
- User registration and login with bcrypt password hashing
- Blog post CRUD (create, read, list with pagination, partial update, delete)
- Comments (create, list) scoped to a parent post
- Health check endpoint with database connectivity check
- Structured logging with correlation IDs (`internal/middleware/logging.go`)
- Panic recovery middleware (`internal/middleware/recovery.go`)
- Graceful shutdown on SIGINT/SIGTERM
- GORM connection pooling
- Both GORM `AutoMigrate` (dev convenience) and `golang-migrate` versioned SQL files
  (`migrations/`, production-style teaching) for the same schema

**Quick start:**
```bash
cd examples/blog-api
docker compose up -d
cp .env.example .env
go mod tidy
go run ./cmd/server
```

**Structure summary:** mirrors `vibe/vibe_gin_boilerplate.md` — `cmd/server/`, `internal/{config,
database, middleware, handler, model, repository, service}/`. See `blog-api/README.md` for the full
architecture walkthrough.

**Phases implemented (if teaching phase-by-phase):**
- Phase 0: Skeleton — all endpoints scaffolded (superseded here by the complete reference; use this
  app's git history or `rules/200-skeleton-phase.mdc` to demonstrate what Phase 0 alone would look
  like with mock handlers)
- Phase 1: Auth (register/login)
- Phase 2: Posts CRUD
- Phase 3: Comments

**Testing:**
```bash
cd examples/blog-api
docker compose up -d
docker compose exec postgres psql -U postgres -c "CREATE DATABASE blog_db_test;"
go test ./tests/... -v
```
See `blog-api/tests/README.md` for the full testing guide.

## How to Use This With Students

1. Have students read `stacks/go-gin/context.md` and `rules/000-core-workflow.mdc` first
2. Walk through `blog-api/README.md`'s architecture section live
3. Demo one full request flow: `curl` a request -> show the handler -> service -> repository ->
   database round trip in the code
4. Run `go test ./tests/... -v` and show a scenario test's doc comment as a spec, then its assertions
   as the verification
5. Have students extend the app with a new small feature (e.g. post tags) following
   `rules/301-endpoint-phase.mdc`'s session workflow

## Related Domain Example

The chatbot domain cluster (`vibe/vibe_chatbot_guide.md` + `templates/chatbot-*.md`) is a second,
smaller worked example focused on a different pattern: an external API dependency
(`LLMClient` interface) instead of a second database entity relationship. Use it after `blog-api/` to
show that the same interface-at-point-of-use idiom applies beyond just repositories.
