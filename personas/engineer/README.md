# Engineer Persona Pack

This pack adds engineer-specific commands, subagents, hooks, MCP integrations, and rules to the Adaptive SDLC. It is installed by running `/set-persona engineer`.

## What this pack adds

**Commands:**
- `/engineer-tasks` — Decompose an `architect` plan into parallel-safe tasks with Given/When/Then acceptance criteria
- `/engineer-implement` — Execute the TDD loop: red→green→refactor, with subagent delegation at each step

**Subagents:**
- `code-reviewer` — Reviews diffs against the active stack's rules (style, architecture, testing)
- `security-auditor` — Scans for secret leaks, injection vulnerabilities, and unsafe patterns
- `test-runner` — Runs the test suite and reports failures with root cause analysis
- `verifier` — Validates "done" claims against acceptance criteria and tries edge cases

**Hooks:**
- `afterFileEdit` — Runs `lint.sh` (ruff/biome/gofmt) and `type-check.sh` (mypy/tsc/go vet) on every changed file
- `beforeShellExecution` — `block-destructive.sh` blocks `rm -rf`, force push, DROP TABLE, and similar patterns
- `stop` — `test-runner.sh` runs the full test suite at the end of every session

**MCP servers:**
- `github` — Issue and PR operations (requires `GITHUB_PAT`)
- `postgres` — Read-only database introspection (requires `DATABASE_URL`, optional)
- `sentry` — Error retrieval and analysis (requires `SENTRY_AUTH_TOKEN`, optional)
- `playwright` — Browser automation for E2E tests (no credentials needed)
- `context7` — Up-to-date library documentation (no credentials needed)

## How this pack pairs with `setup-stack`

After running `/set-persona engineer`, run `/setup-stack` to select a stack pack (Python FastAPI, Node Express, Java Spring, Go Gin, Terraform, or blank). The persona pack and the stack pack compose: persona rules sit alongside stack rules, persona subagents work with stack-specific tooling.

Designer and PM personas skip this step — they are framework-agnostic.

## Prerequisites

See `SETUP.md` for the full pre-class checklist including MCP credential setup.
