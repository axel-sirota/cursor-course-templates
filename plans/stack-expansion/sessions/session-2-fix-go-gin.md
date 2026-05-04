# Session 2 — Fix `go-gin` (STUB → COMPLETE)

**Phase:** 1
**Parallel with:** Sessions 1, 3–6
**Depends on:** nothing
**Next:** Session 13 (after all phase 1+2 done)

## Current state
```
stacks/go-gin/
├── context.md                  ← missing Architecture Shape
├── rules/
│   ├── go-standards.mdc        ← no numeric prefix, mixes concerns
│   └── 500-docker-go.mdc
├── templates/
│   ├── Dockerfile
│   └── go-starter.md           ← 10-line main.go only
└── vibe/
    └── vibe_docker.md
```
No `examples/`.

---

## Files to Create / Update

```
stacks/go-gin/
├── context.md                          ← UPDATE (add Architecture Shape)
├── rules/
│   ├── 000-go-workflow.mdc             ← NEW
│   ├── 100-go-architecture.mdc         ← NEW
│   ├── 200-go-testing.mdc              ← NEW
│   ├── 300-go-style.mdc                ← NEW
│   ├── 400-go-standards.mdc            ← RENAME from go-standards.mdc (keep content, add prefix)
│   └── 500-docker-go.mdc               ← keep as-is
├── templates/
│   ├── go-starter.md                   ← UPDATE (expand: handler + service + repo + interface)
│   ├── phase-checklist.md              ← NEW
│   └── golangci.yml                    ← NEW
├── vibe/
│   ├── vibe_architecture.md            ← NEW
│   └── vibe_development_lifecycle.md   ← NEW
└── examples/
    └── users-resource/
        ├── handler_test.go
        ├── handler.go
        ├── service.go
        ├── repository.go
        └── model.go
```

---

## File Specifications

### `context.md` addition

Add section:
```markdown
## Architecture Shape
REST API — Gin HTTP server. Layered: handler → service → repository → model.
Also applicable to: CLI tools (swap handler layer for cobra commands), gRPC services (see `go-grpc` stack).
```

### `rules/000-go-workflow.mdc`

Frontmatter: `description: Go development workflow and phase discipline`, `alwaysApply: true`

Rules:
- **TDD loop**: Write failing test → implement until green → refactor. Never write implementation without a failing test first.
- **Build tags**: Use `//go:build integration` tag to separate fast unit tests from slow integration tests. `go test ./...` runs only unit tests. `go test -tags integration ./...` runs all.
- **CI gate**: `go vet ./...` → `golangci-lint run` → `go test ./...` → `go test -tags integration ./...`. All must pass.
- **Module hygiene**: `go mod tidy` before every commit. No unused imports or dependencies.
- **Feature branches**: one branch per feature; PR requires passing CI gate.

### `rules/100-go-architecture.mdc`

Frontmatter: `description: Go project structure and design patterns`, `alwaysApply: true`

Rules:
- **Standard layout**: `cmd/{appname}/main.go` (entrypoint only, ≤20 lines), `internal/` (private app code), `pkg/` (public reusable code). Never put logic in `main.go`.
- **Layer separation**: handler layer handles HTTP only (parse request, call service, write response). No business logic in handlers. No HTTP types in services.
- **Consumer-side interfaces**: Define interfaces in the package that uses them, not the package that implements them. Keep interfaces small (1–3 methods).
- **Context propagation**: `context.Context` is always the first argument of every function that does I/O. Never store context in a struct.
- **Error wrapping**: Use `fmt.Errorf("doing X: %w", err)` for all error chains. Define sentinel errors with `errors.New`. Use `errors.Is` / `errors.As` for checking, never string comparison.
- **Graceful shutdown**: HTTP server must listen for `os.Signal` (SIGTERM, SIGINT) and call `server.Shutdown(ctx)` with a timeout context.

### `rules/200-go-testing.mdc`

Frontmatter: `description: Go testing patterns`, `alwaysApply: true`

Rules:
- **Table-driven tests**: All unit tests use `[]struct{ name, input, expected }` table format with `t.Run(tc.name, ...)`.
- **testify**: Use `github.com/stretchr/testify/assert` for assertions. Never `if got != want { t.Fatal(...) }`.
- **Mock generation**: Use `github.com/vektra/mockery/v2` to generate mocks from interfaces. Never hand-write mocks.
- **Testcontainers**: Integration tests that touch Postgres use `github.com/testcontainers/testcontainers-go`. No mocked databases for integration tests.
- **Test file placement**: `handler_test.go` alongside `handler.go` in same package (white-box) for unit tests. `integration/` subdirectory for integration tests with build tag.
- **Coverage**: `go test -cover ./...` must show ≥80% on business logic packages (`internal/service/`, `internal/repository/`).

### `rules/300-go-style.mdc`

Frontmatter: `description: Go code style and naming conventions`, `alwaysApply: true`

Rules:
- **Formatting**: `gofmt` (enforced by golangci-lint). Never commit unformatted code.
- **Naming**: Short, descriptive variable names. Single-letter receivers (`u *UserService` → receiver `u`). Acronyms all-caps: `userID`, `httpClient`, `sqlDB`.
- **Error strings**: lowercase, no punctuation at end. `"failed to connect to database"` not `"Failed to connect to database."`.
- **Package names**: short, lowercase, no underscores, no `util` or `helpers`. Name by what it provides, not what it contains.
- **No naked returns**: never use named return values with bare `return`. Always explicit.
- **Exported vs unexported**: only export what callers genuinely need. Default to unexported.

### `templates/go-starter.md` (UPDATE)

Expand to show full project scaffold:
```
cmd/server/
    main.go          (≤20 lines: wire deps, start server, graceful shutdown)
internal/
    handler/
        user.go      (Gin handler struct + routes registration)
        user_test.go (table-driven unit tests with mock service)
    service/
        user.go      (UserService interface + impl)
        user_test.go (table-driven unit tests)
    repository/
        user.go      (UserRepository interface + postgres impl)
        user_test.go (integration test with testcontainers, build tag)
    model/
        user.go      (domain model structs)
pkg/
    config/
        config.go    (viper/env config loading)
    db/
        postgres.go  (connection pool setup)
```
Include `main.go` content showing graceful shutdown pattern.
Include `handler/user.go` showing Gin handler + service injection via interface.
Include `service/user.go` showing the UserService interface defined at consumer (handler) side.

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] `cmd/server/main.go` compiles and starts (returns 200 on `/health`)
- [ ] All handler routes registered (return 501 Not Implemented)
- [ ] Service interfaces defined
- [ ] Repository interfaces defined
- [ ] `go vet ./...` passes
- [ ] `golangci-lint run` passes

**Phase 1+ — Implementation:**
- [ ] Failing test written before implementation
- [ ] Test passes after implementation
- [ ] `errors.Is`/`errors.As` used (no string comparison)
- [ ] `context.Context` propagated through all I/O calls
- [ ] No logic in `main.go` or handler layer
- [ ] Integration test added for any repository change

**Handoff:**
- [ ] `go test -cover ./...` ≥ 80% on service + repository packages
- [ ] `golangci-lint run` zero warnings
- [ ] Graceful shutdown tested manually

### `templates/golangci.yml`

```yaml
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - unused
    - gosimple
    - ineffassign
    - gofmt
    - goimports
    - revive
    - exhaustive
    - wrapcheck
linters-settings:
  wrapcheck:
    ignorePackageGlobs:
      - "github.com/gin-gonic/gin"
```

### `vibe/vibe_architecture.md`

Sections:
- **Why Go**: concurrency model (goroutines), static binary deployment, sub-millisecond cold start, strong typing without JVM overhead. Choose Go over Java when startup time, binary portability, or memory footprint matters. Choose Go over Node when CPU work or high concurrency without I/O is the bottleneck.
- **Architecture shapes in Go**: REST API (this stack), gRPC service (see `go-grpc`), CLI tool (swap handler for cobra), library/SDK (no cmd/ needed). Each shape uses the same `internal/` discipline.
- **Layer responsibilities**: handler = HTTP protocol only; service = business rules, no I/O; repository = I/O only, no business rules. Crossing these lines is the most common Go architecture mistake.
- **Interface design**: Go interfaces are implicit. Keep them small. Define them where they're used (consumer side). A one-method interface is not unusual — it's idiomatic.
- **Error handling philosophy**: errors are values; propagate with context using `%w`; only log at the boundary where you handle (not where you detect). Don't double-log.

### `vibe/vibe_development_lifecycle.md`

Sections:
- **The Go session loop**: read context → write failing test → implement → green → refactor → `go vet` + lint → commit
- **Feature branch flow**: branch from `main`, one feature per branch, PR requires green CI
- **Commit conventions**: `feat:`, `fix:`, `refactor:`, `test:`, `chore:` prefixes
- **PR discipline**: PR description explains WHY, not what. Link to issue. Tests added.
- **Dependency management**: `go mod tidy` always; pin indirect deps; audit with `govulncheck`

### `examples/users-resource/`

Five files showing a complete, working CRUD handler → service → repository chain:
- `model.go`: `User` struct (ID, Name, Email, CreatedAt)
- `repository.go`: `UserRepository` interface (Create, GetByID, List) + `postgresUserRepository` implementing it
- `service.go`: `UserService` interface (CreateUser, GetUser, ListUsers) + `userService` implementing it; takes `UserRepository` interface
- `handler.go`: `UserHandler` struct; takes `UserService` interface; registers `/users` POST, GET `/users/:id`, GET `/users`
- `handler_test.go`: table-driven tests for all 3 routes using mock service (mockery-generated)

---

## Acceptance Criteria

- [ ] `ls stacks/go-gin/rules/` shows 6 files (000–500)
- [ ] `ls stacks/go-gin/templates/` shows `go-starter.md`, `phase-checklist.md`, `golangci.yml`, `Dockerfile`
- [ ] `ls stacks/go-gin/vibe/` shows 2 docs
- [ ] `ls stacks/go-gin/examples/users-resource/` shows 5 `.go` files
- [ ] `rules/100-go-architecture.mdc` contains "context.Context is always the first argument"
- [ ] `rules/200-go-testing.mdc` contains "table-driven tests"
- [ ] `vibe/vibe_architecture.md` contains "Choose Go over Java when" decision guidance
- [ ] `go-starter.md` shows multi-layer scaffold (cmd/, internal/, pkg/)
