# Engineer Persona Pack

Ships service code behind tests in `workspaces/engineer/`, one TDD loop at a time, on one of six backend stacks.

Install with `/set-persona add engineer`, then `/setup-stack engineer` → `/architect engineer` → `/start-session engineer`. All paths below are relative to `workspaces/engineer/`.

## What this pack adds

**Commands:**
- `/engineer-tasks`: decompose the current session plan into parallel-safe tasks with Given/When/Then acceptance criteria
- `/engineer-implement`: execute the TDD loop (red→green→refactor) with subagent delegation at each step

**Subagents:**
- `code-reviewer`: reviews diffs against the active stack's rules (style, architecture, testing)
- `security-auditor`: scans for secret leaks, injection vulnerabilities, and unsafe patterns
- `test-runner`: runs the test suite and reports failures with root cause analysis
- `verifier`: validates "done" claims against acceptance criteria and tries edge cases

**Hooks** (installed to `.cursor/scripts/engineer/`, scoped to `workspaces/engineer/`):
- `afterFileEdit`: `lint.sh` (ruff/biome/gofmt) and `type-check.sh` (mypy/tsc/go vet) on every changed file
- `beforeShellExecution`: `block-destructive.sh` blocks `rm -rf`, force push, DROP TABLE, and similar patterns
- `stop`: `test-runner.sh` runs the full test suite at the end of an engineer session

**MCP servers:**
- `github`: issue and PR operations (requires `GITHUB_PAT`)
- `postgres`: read-only database introspection (requires `DATABASE_URL`, optional)
- `sentry`: error retrieval and analysis (requires `SENTRY_AUTH_TOKEN`, optional)
- `playwright`: browser automation for E2E tests (no credentials needed)
- `context7`: up-to-date library documentation (no credentials needed)

## How this pack pairs with `/setup-stack`

After `/set-persona add engineer`, run `/setup-stack engineer` and pick one of: python-fastapi (default), go-gin, go-grpc, java-spring, node-express, node-nestjs. Persona rules and stack rules both install into `.cursor/rules/engineer/` and apply only to files in `workspaces/engineer/`.

## Prerequisites

See `SETUP.md` for the pre-class checklist.
