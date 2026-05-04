# Development Lifecycle: Go gRPC

## Shared Foundations
This stack follows the shared workflows defined in:
- `stacks/shared/vibe_git_workflow.md` — branch, commit, PR, and merge conventions
- `stacks/shared/vibe_session_workflow.md` — session structure, handoff format, context management

Read those first. This document adds gRPC-specific lifecycle steps layered on top.

---

## gRPC-Specific Lifecycle

### Step 1: Proto Design (before any Go code)
Write the `.proto` file. This is a separate, reviewable step — not just boilerplate.

Checklist before proceeding:
- [ ] Package name follows `{service}.v1` convention
- [ ] `option go_package` set correctly
- [ ] All message field numbers are unique and correct
- [ ] `buf lint` passes
- [ ] Proto reviewed and approved (team sign-off or self-review for solo projects)

**Do not write Go implementation code until the proto is approved.** The proto is the contract. Changing it after implementation begins creates rework.

### Step 2: Generate Code
```bash
buf generate
```

Commit the generated files in `gen/`. Generated code is a build artifact that must be in version control for:
- Reproducible builds without requiring protoc/buf in CI
- Code review visibility into what changed
- IDE support without running generation

### Step 3: Implement Skeleton (Phase 0)
Implement all server methods returning `codes.Unimplemented`. Wire up health check and server. Verify `go build ./...` succeeds.

This creates a deployable (if non-functional) service with correct structure before any business logic.

### Step 4: TDD Implementation (Phase 1+)
For each RPC method:
1. Write failing unit test in `internal/service/{service}_test.go`
2. Implement service logic until test passes
3. Run `go vet ./...` and `golangci-lint run`
4. Commit

### Step 5: Integration Tests
Write `bufconn`-based integration tests tagged `//go:build integration`. These test the full gRPC stack (serialization, interceptors, error mapping) without a real network.

```bash
go test -tags integration ./...
```

### Step 6: Breaking Change Check
Before any PR:
```bash
buf breaking --against '.git#branch=main'
```

This is non-negotiable after v1. If you need a breaking change, the options are:
1. Make it additive (preferred)
2. Create a new major version package (`{service}/v2`)
3. Coordinate a synchronized deploy with all consumers

---

## buf generate is Part of the Build
Unlike REST where you write handler code directly, gRPC has a generation step. Treat `buf generate` as part of your build cycle, not a one-time setup. Run it whenever `.proto` files change.

CI should verify that generated files are up to date:
```bash
buf generate
git diff --exit-code gen/   # Fails if generated files are stale
```

---

## Breaking Change Policy
- **Before v1.0**: breaking changes acceptable with team coordination
- **After v1.0**: additive-only. All proto changes must pass `buf breaking`.
- **Field numbers**: never reuse, ever. Use `reserved` to mark retired numbers.
- **New major version**: create `{service}/v2` package. Run both versions simultaneously during migration. Deprecate v1 after all consumers migrate.
