# Go Gin Phase Checklist

## Phase 0 — Skeleton

- [ ] `cmd/server/main.go` compiles and starts (returns 200 on `/health`)
- [ ] All handler routes registered (return 501 Not Implemented)
- [ ] Service interfaces defined
- [ ] Repository interfaces defined
- [ ] `go vet ./...` passes
- [ ] `golangci-lint run` passes

## Phase 1+ — Implementation

- [ ] Failing test written before implementation
- [ ] Test passes after implementation
- [ ] `errors.Is`/`errors.As` used (no string comparison)
- [ ] `context.Context` propagated through all I/O calls
- [ ] No logic in `main.go` or handler layer
- [ ] Integration test added for any repository change

## Handoff

- [ ] `go test -cover ./...` ≥ 80% on service + repository packages
- [ ] `golangci-lint run` zero warnings
- [ ] Graceful shutdown tested manually
