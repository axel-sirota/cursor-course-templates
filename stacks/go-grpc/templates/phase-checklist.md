# gRPC Service Phase Checklist

## Phase 0 — Skeleton

- [ ] `.proto` file written and lints clean (`buf lint`)
- [ ] `buf.yaml` and `buf.gen.yaml` present and correct
- [ ] `buf generate` succeeds, generated files committed to `gen/`
- [ ] Server skeleton implements all service methods (returning `codes.Unimplemented`)
- [ ] Health check registered (`grpc_health_v1.RegisterHealthServer`)
- [ ] `go build ./...` succeeds with no errors
- [ ] `go vet ./...` passes
- [ ] `golangci-lint run` passes

## Phase 1 — Core Implementation

- [ ] Failing unit test written before each service method implementation
- [ ] Repository interface defined in `internal/repository/`
- [ ] Mock generated with mockery for repository interface
- [ ] Service logic implemented in `internal/service/`
- [ ] gRPC status codes used correctly:
  - [ ] `codes.NotFound` for missing resources
  - [ ] `codes.InvalidArgument` for bad input
  - [ ] `codes.AlreadyExists` for duplicate creates
  - [ ] `codes.Internal` for unexpected errors (no detail leak)
- [ ] Context propagated and checked for cancellation after long operations
- [ ] `buf breaking --against .git#branch=main` passes (no proto regressions)
- [ ] All unit tests green (`go test ./internal/...`)

## Phase 2 — Integration & Hardening

- [ ] Integration tests using `bufconn` in-memory server
- [ ] Integration tests tagged `//go:build integration`
- [ ] `go test -tags integration ./...` all green
- [ ] Interceptors wired: logging (at minimum), auth if required
- [ ] Error mapping function centralized (no scattered `status.Errorf` calls)
- [ ] Deadline/context handling tested (what happens when client cancels?)
- [ ] Server reflection gated on `GRPC_REFLECTION=true` env var

## Handoff Criteria

- [ ] `go test ./...` all green
- [ ] `go test -tags integration ./...` all green
- [ ] `buf lint` passes
- [ ] `buf breaking --against .git#branch=main` passes
- [ ] `golangci-lint run` passes with zero warnings
- [ ] Health check returns `SERVING` (verified with grpcurl or grpc-health-probe)
- [ ] grpcurl smoke test documented in README:
  ```bash
  grpcurl -plaintext localhost:50051 list
  grpcurl -plaintext -d '{"name": "Alice"}' localhost:50051 {service}.v1.{Service}Service/Create{Resource}
  ```
- [ ] Docker image builds successfully (`docker build .`)
- [ ] No hardcoded credentials or secrets
