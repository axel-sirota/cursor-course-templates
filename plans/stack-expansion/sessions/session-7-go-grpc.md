# Session 7 — New Stack: `go-grpc`

**Phase:** 3 — Group A (engineer persona)
**Parallel with:** Sessions 8–12
**Depends on:** Sessions 1–6 complete (pattern established)
**Client fit:** Intuit (internal services), any team doing service-to-service communication

## Architecture Shape
gRPC Service — Protocol Buffers contract-first. Binary transport, strongly typed, bidirectional streaming. Not REST. No JSON by default.

---

## Files to Create

```
stacks/go-grpc/
├── context.md
├── rules/
│   ├── 000-grpc-workflow.mdc
│   ├── 100-grpc-architecture.mdc
│   ├── 200-grpc-testing.mdc
│   ├── 300-go-style.mdc            (same as go-gin 300, copy)
│   └── 500-docker-go-grpc.mdc
├── templates/
│   ├── grpc-starter.md
│   ├── phase-checklist.md
│   ├── golangci.yml
│   └── proto/
│       └── service.proto           (example proto template)
├── vibe/
│   ├── vibe_architecture.md
│   └── vibe_development_lifecycle.md   (references stacks/shared/)
└── examples/
    └── users-service/
        ├── proto/users.proto
        ├── server/main.go
        ├── internal/service/users.go
        ├── internal/service/users_test.go
        └── buf.yaml
```

---

## File Specifications

### `context.md`

```markdown
# Project Context: Go gRPC

## Tech Stack
- Language: Go 1.22+
- Transport: gRPC (google.golang.org/grpc v1.6x)
- Schema: Protocol Buffers v3 (google.golang.org/protobuf)
- Proto tooling: buf (preferred over raw protoc)
- Database: PostgreSQL (sqlx or pgx/v5)
- Testing: testing + testify + gomock (for interface mocks)
- Linting: golangci-lint

## Architecture Shape
gRPC Service — contract-first via .proto files. Binary transport. Not REST.
Use for: internal service-to-service communication, high-throughput APIs, streaming data.
Use REST (go-gin stack) for: external-facing APIs, browser clients, webhook receivers.

## Vibe & Style
- Coding Style: gofmt. Short idiomatic names.
- Architecture: proto first → generate → implement. Never write gRPC boilerplate by hand.
- Pattern: proto defines the contract; Go implements the server interface generated from proto.

## Key Rules
- Proto file is the source of truth. Never modify generated code.
- Use buf for proto linting and code generation (not raw protoc).
- Implement grpc_health_v1 health check on every service.
- Use interceptors (not middleware) for cross-cutting concerns (logging, auth, tracing).
- Always propagate context.Context as first argument.

## Active Phase
- Current: Phase 0 (Skeleton)
```

### `rules/000-grpc-workflow.mdc`

- **Proto first**: write `.proto` file before any Go code. Get proto reviewed before implementing.
- **`buf generate` not `protoc`**: use `buf.yaml` and `buf.gen.yaml` for all code generation. Commit generated files.
- **TDD**: write failing test against the service interface → implement → green.
- **CI gate**: `buf lint` → `buf breaking` → `go vet` → `golangci-lint` → `go test ./...`.
- **Breaking change detection**: `buf breaking --against .git#branch=main` in CI. Proto breaking changes require a new major version or backwards-compatible addition only.

### `rules/100-grpc-architecture.mdc`

- **Project structure**: `proto/` (source), `gen/` (generated — committed), `internal/service/` (business logic), `cmd/server/main.go` (wire + start).
- **Server implementation**: implement the generated `{Service}Server` interface in `internal/service/`. Zero gRPC types in service logic — use domain types. Map at the handler layer (generated server method implementations).
- **Interceptors for cross-cutting concerns**: auth, logging, rate limiting, tracing go in gRPC interceptors (unary + stream). Not in service business logic.
- **Health check**: every gRPC service registers `grpc_health_v1.RegisterHealthServer(s, healthServer)`. Required for Kubernetes liveness probes.
- **Reflection**: register `reflection.Register(s)` in non-production for grpcurl debugging. Disable in production.
- **Error handling**: return `status.Errorf(codes.NotFound, "user %d not found", id)`. Map domain errors to gRPC status codes consistently. Use a central error mapping function.
- **Deadlines**: always check `ctx.Err()` after long operations. Propagate deadlines; never ignore context cancellation.

### `rules/200-grpc-testing.mdc`

- **Unit test service logic**: test `internal/service/` with plain Go tests. No gRPC involved — call service methods directly.
- **Integration test with bufconn**: use `google.golang.org/grpc/test/bufconn` to create an in-memory gRPC server for integration tests. No network required.
- **Table-driven tests**: all test cases in `[]struct{name, input, wantErr}` format.
- **Mock dependencies**: generate mocks with `mockery` for all repository interfaces.
- **Proto conformance**: `buf breaking` in CI ensures no backwards-incompatible proto changes sneak in.

### `templates/grpc-starter.md`

Scaffold showing:
```
proto/
    {service}.proto      (service + message definitions)
    buf.yaml             (module config)
    buf.gen.yaml         (generation config: go + grpc plugins)
gen/
    {package}/
        {service}_grpc.pb.go
        {service}.pb.go
internal/
    service/
        {service}.go     (implements generated Server interface)
        {service}_test.go
cmd/server/
    main.go              (wire deps, register services, start server with graceful shutdown)
```

Include example `buf.yaml`:
```yaml
version: v1
modules:
  - path: proto
lint:
  use:
    - DEFAULT
breaking:
  use:
    - FILE
```

Include example `buf.gen.yaml`:
```yaml
version: v1
plugins:
  - plugin: go
    out: gen
    opt: paths=source_relative
  - plugin: go-grpc
    out: gen
    opt: paths=source_relative
```

### `templates/proto/service.proto`

```proto
syntax = "proto3";
package {service}.v1;
option go_package = "github.com/{org}/{repo}/gen/{service}/v1;{service}v1";

import "google/protobuf/timestamp.proto";

service {Service}Service {
  rpc Create{Resource} (Create{Resource}Request) returns (Create{Resource}Response);
  rpc Get{Resource}    (Get{Resource}Request)    returns (Get{Resource}Response);
  rpc List{Resources}  (List{Resources}Request)  returns (List{Resources}Response);
}

message {Resource} {
  string id    = 1;
  string name  = 2;
  google.protobuf.Timestamp created_at = 3;
}

message Create{Resource}Request  { string name = 1; }
message Create{Resource}Response { {Resource} {resource} = 1; }
message Get{Resource}Request     { string id = 1; }
message Get{Resource}Response    { {Resource} {resource} = 1; }
message List{Resources}Request   { int32 page_size = 1; string page_token = 2; }
message List{Resources}Response  { repeated {Resource} {resources} = 1; string next_page_token = 2; }
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] `.proto` file lints clean (`buf lint`)
- [ ] `buf generate` succeeds, generated files committed
- [ ] Server registers all service methods (return `codes.Unimplemented`)
- [ ] Health check registered
- [ ] `go build ./...` succeeds

**Phase 1+ — Implementation:**
- [ ] Failing unit test written before service logic
- [ ] gRPC status codes used correctly (NotFound, InvalidArgument, Internal, etc.)
- [ ] Context propagated and checked for cancellation
- [ ] `buf breaking` passes (no proto regressions)

**Handoff:**
- [ ] `go test -tags integration ./...` all green
- [ ] `buf lint` + `buf breaking` pass
- [ ] Health check returns SERVING
- [ ] grpcurl smoke test documented in README

### `vibe/vibe_architecture.md`

- **When gRPC over REST**: internal service-to-service (no browser), high throughput, streaming, strongly typed contracts shared across teams. REST wins for external/browser APIs.
- **Proto as contract**: the `.proto` file is the API contract. Treat it like a public interface — backwards compatibility matters. Field numbers are sacred (never reuse).
- **buf vs protoc**: buf handles linting, breaking change detection, plugin management. Use buf. Only use raw protoc if buf is unavailable.
- **Streaming patterns**: unary (request/response) is the default. Server-streaming for large result sets. Client-streaming for bulk uploads. Bidirectional for real-time.
- **Go gRPC vs connect-go**: connect-go (from Buf) supports both gRPC and HTTP/1.1 from one service. Consider it when you need browser compatibility. Standard gRPC for pure service-to-service.

### `vibe/vibe_development_lifecycle.md`

References `stacks/shared/vibe_git_workflow.md` and `stacks/shared/vibe_session_workflow.md`.

Adds gRPC-specific:
- Proto review is a separate step before implementation — get proto approved before writing Go
- `buf generate` is part of the build, not a one-time setup
- Breaking change policy: additive-only after first release

### `examples/users-service/`

Five files showing a complete gRPC service:
- `proto/users.proto` — UserService with CreateUser, GetUser, ListUsers
- `buf.yaml` — module config
- `server/main.go` — wire service, register health check + reflection, start with graceful shutdown
- `internal/service/users.go` — implements `pb.UserServiceServer`; uses repository interface
- `internal/service/users_test.go` — table-driven tests using bufconn in-memory server

---

## Acceptance Criteria

- [ ] `ls stacks/go-grpc/rules/` shows 5 files
- [ ] `ls stacks/go-grpc/templates/` shows `grpc-starter.md`, `phase-checklist.md`, `golangci.yml`, `proto/service.proto`
- [ ] `ls stacks/go-grpc/vibe/` shows 2 docs
- [ ] `ls stacks/go-grpc/examples/users-service/` shows 5 files
- [ ] `context.md` Architecture Shape = "gRPC Service"
- [ ] `rules/100-grpc-architecture.mdc` contains health check rule
- [ ] `templates/proto/service.proto` contains `option go_package`
- [ ] `vibe_architecture.md` contains "When gRPC over REST" decision section
