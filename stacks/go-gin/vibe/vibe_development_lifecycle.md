# Go Development Lifecycle Vibe

## The Go Session Loop

Every coding session follows this loop:

1. **Read context**: review `context.md`, active phase, open tasks
2. **Write failing test**: write the test first — watch it fail
3. **Implement**: write the minimum code to make the test pass
4. **Green**: confirm the test passes
5. **Refactor**: clean up without breaking the test
6. **Verify**: `go vet ./...` + `golangci-lint run`
7. **Commit**: `go mod tidy`, then commit with a meaningful message

Never skip steps. Never write implementation before a failing test.

## Feature Branch Flow

- Branch from `main` for every feature: `git checkout -b feat/user-creation`
- One feature per branch — keep PRs small and reviewable
- PR requires green CI before merge: vet → lint → unit tests → integration tests
- Delete branch after merge

## Commit Conventions

Use conventional commit prefixes:

| Prefix | Use case |
|--------|----------|
| `feat:` | new capability |
| `fix:` | bug fix |
| `refactor:` | code change that neither fixes a bug nor adds a feature |
| `test:` | adding or updating tests only |
| `chore:` | dependency updates, build config, non-code changes |

Examples:
- `feat: add user creation endpoint`
- `fix: handle missing user with 404 instead of 500`
- `test: add table-driven tests for user service`
- `chore: update gin to v1.9.1`

## PR Discipline

A good PR description explains WHY, not what. The diff shows what changed. The description explains the reasoning.

PR checklist:
- [ ] Links to the issue it closes
- [ ] Explains why this approach was chosen
- [ ] Tests added or updated
- [ ] `go test -cover ./...` shows ≥80% on changed packages
- [ ] `golangci-lint run` zero warnings

## Dependency Management

- Run `go mod tidy` before every commit — removes unused dependencies, adds missing ones
- Pin indirect dependencies explicitly when they have security implications
- Audit with `govulncheck ./...` before releases
- Prefer the standard library over adding dependencies; add a dependency only when the benefit clearly outweighs the cost of the additional dependency
