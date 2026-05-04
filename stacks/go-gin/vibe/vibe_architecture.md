# Go Architecture Vibe

## Why Go

Go's concurrency model (goroutines + channels) enables high-throughput servers without the complexity of thread management. Static binary deployment means no runtime dependencies, no JVM, no interpreter — just a single binary. Cold start is sub-millisecond. Memory footprint is a fraction of JVM-based services.

**Choose Go over Java when**: startup time matters (lambdas, containers), binary portability is required (ship a single file), or memory footprint needs to be minimal (run many instances cheaply).

**Choose Go over Node when**: CPU-bound work is involved, high concurrency without async/await complexity is needed, or static typing at compile time is a hard requirement.

## Architecture Shapes in Go

All shapes use the same `internal/` discipline.

- **REST API** (this stack): `cmd/server/` → `internal/handler/` → `internal/service/` → `internal/repository/`
- **gRPC service** (see `go-grpc` stack): swap handler layer for gRPC server generated from proto files
- **CLI tool**: swap handler layer for cobra commands; service + repository layers remain unchanged
- **Library/SDK**: no `cmd/` needed; only `pkg/` with public API and `internal/` for implementation details

## Layer Responsibilities

| Layer | Responsibility | Forbidden |
|-------|---------------|-----------|
| handler | HTTP protocol: parse request, call service, write response | Business logic, database access |
| service | Business rules, orchestration | HTTP types, direct I/O |
| repository | I/O: database queries, external API calls | Business rules, HTTP types |

Crossing these lines is the most common Go architecture mistake. The test: if you can run the service layer tests without starting an HTTP server, your layers are clean.

## Interface Design

Go interfaces are implicit — a type satisfies an interface just by having the right methods. No `implements` keyword.

Key principles:
- Keep interfaces small. 1–3 methods is common; a one-method interface is not unusual — it's idiomatic.
- Define interfaces at the consumer side (in the package that uses them, not the package that provides them).
- This enables swapping implementations without changing the consuming package — and makes mocking trivial.

```go
// In handler package — consumer side
type UserService interface {
    CreateUser(ctx context.Context, name, email string) (model.User, error)
}
```

## Error Handling Philosophy

Errors are values in Go. They are not exceptions — they don't unwind the stack. This is a feature.

- **Propagate with context**: `fmt.Errorf("creating user: %w", err)` — each layer adds context
- **Log at the boundary**: only log where you handle the error (top of the call stack). Don't log at every layer — you'll get duplicate log lines with no additional information.
- **Don't double-log**: if you log an error, don't return it. If you return it, don't log it.
- **Sentinel errors**: define domain errors with `errors.New` and check with `errors.Is` — never compare error strings.
