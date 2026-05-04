# Session 2 — Phase A: Engineer Commands, Agents, Scripts, Hooks, MCP, Rule

**Phase:** A (Engineer persona pack)
**Goal:** All functional files for engineer persona — everything that gets installed into `.cursor/` and `.claude/` at runtime.
**Depends on:** Session 1 (directory scaffold must exist)
**Next session:** Session 3 (designer scaffold)

---

## Files to Create

```
personas/engineer/
├── commands/
│   ├── engineer-tasks.md
│   └── engineer-implement.md
├── agents/
│   ├── code-reviewer.md
│   ├── security-auditor.md
│   ├── test-runner.md
│   └── verifier.md
├── scripts/
│   ├── lint.sh
│   ├── type-check.sh
│   ├── test-runner.sh
│   └── block-destructive.sh
├── hooks.json
├── mcp.json
└── rules/
    └── 000-engineer-workflow.mdc
```

---

## File Specifications

### `commands/engineer-tasks.md`

**Purpose:** Decompose an `architect` plan into parallel-safe tasks ready for `engineer-implement`.

Steps:
1. Read `docs/plan-{feature}.md` (ask if multiple plans exist)
2. Identify task boundaries: one task per endpoint/function, per test file, per migration
3. For each task declare: `id`, `title`, `acceptance` (Given/When/Then), `touched_files`, `depends_on`
4. Detect file conflicts — tasks touching same file marked sequential
5. Output `docs/tasks-{feature}.md`: summary table + per-task detail sections

Output schema: summary table (id, title, depends_on, parallel-safe?) + detail sections (acceptance criteria, touched files, suggested subagent for review).

### `commands/engineer-implement.md`

**Purpose:** Execute TDD loop on a tasks file from `engineer-tasks`. Delegates to subagents.

For each task in dependency order:
1. **Red** — write failing test asserting acceptance criteria
2. **Run** — invoke `test-runner` subagent, confirm failure is expected
3. **Green** — write minimum implementation to pass
4. **Run** — invoke `test-runner`, confirm pass + no regression
5. **Audit** — if task touches auth/DB/external I/O, invoke `security-auditor`; address Critical findings before continuing
6. **Verify** — invoke `verifier` against original acceptance criteria
7. **Refactor** — clean duplication with test as safety net
8. **Mark complete** — update tasks file

Stop conditions: task fails verification 3× → pause; Critical security finding → stop; out-of-scope test starts failing → stop.

Parallel execution: tasks marked `parallel-safe: yes` with no unmet deps can run as background agents.

### `agents/code-reviewer.md`

Frontmatter: `name: code-reviewer`, `description: Reviews code changes against active stack rules`, `model: inherit`, `readonly: true`

Steps: read active stack from context → load rules → `git diff HEAD~1` → for each changed file check style/architecture/testing/security → output Critical/Important/Suggestion report.

### `agents/security-auditor.md`

Frontmatter: `name: security-auditor`, `description: Scans for secret leaks, injection risks, unsafe patterns`, `model: inherit`, `readonly: true`

Scans for: hardcoded secrets, SQL injection, command injection, path traversal, insecure deserialization, missing auth on new endpoints, weak crypto.
Output: grouped by Critical/High/Medium/Informational with file+line, pattern, remediation, OWASP/CWE reference.

### `agents/test-runner.md`

Frontmatter: `name: test-runner`, `description: Runs test suite and reports failures with root cause`, `model: inherit`, `readonly: false`

Steps: detect test command from stack (pytest/npm test/go test) → execute → if pass report count+coverage → if fail report test name, failed assertion, root cause (parsed from traceback), suggested fix.
Does NOT fix tests — reports only.

### `agents/verifier.md`

Frontmatter: `name: verifier`, `description: Validates done claims against acceptance criteria`, `model: inherit`, `readonly: true`

Steps: read spec/task AC → for each criterion find evidence (passing test + code path) → run relevant tests → try at least one edge case (empty, max-size, concurrent, network failure, auth expired).
Output: Verified (with evidence) / Unverified (claimed but unconfirmed) / Edge cases failed.

### `scripts/lint.sh`

Reads `file_path` from stdin JSON. Exits 0 if not a code file.
- `.py` → `ruff check --fix` (if available)
- `.ts/.tsx/.js/.jsx` → `npx biome check --write` (if available)
- `.go` → `gofmt -w`
- `.java` → no-op (IDE formatter)
All linter calls use `|| true` — non-blocking.

### `scripts/type-check.sh`

Reads `file_path` from stdin JSON.
- `.py` → `mypy $file_path` if `mypy.ini` or `pyproject.toml` present
- `.ts/.tsx` → `npx tsc --noEmit` if `tsconfig.json` present
- `.go` → `go vet ./...`
All calls use `|| true` — non-blocking.

### `scripts/test-runner.sh`

Triggered by `stop` event (no `file_path` needed).
- `pyproject.toml` or `setup.py` present → `pytest -x --tb=short`
- `package.json` with `"test"` script → `npm test --silent`
- `go.mod` present → `go test ./...`
On failure: prints advisory message, does not block exit.

### `scripts/block-destructive.sh`

Triggered by `beforeShellExecution`. Reads `command` from stdin JSON.
Returns JSON: `{"continue": true, "permission": "deny", "userMessage": "...", "agentMessage": "..."}` for matches.
Returns `{"continue": true, "permission": "allow"}` otherwise.

Deny-list patterns:
- `rm -rf /`, `rm -rf ~`, `rm -rf \.`
- `git push --force`, `git push -f `
- `git reset --hard origin`
- `DROP DATABASE`, `DROP TABLE`, `TRUNCATE TABLE`
- `sudo rm`, `mkfs`, `dd if=`

This is the ONLY blocking hook. All others are advisory.

### `hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      { "command": ".cursor/scripts/lint.sh" },
      { "command": ".cursor/scripts/type-check.sh" }
    ],
    "beforeShellExecution": [
      { "command": ".cursor/scripts/block-destructive.sh" }
    ],
    "stop": [
      { "command": ".cursor/scripts/test-runner.sh" }
    ]
  }
}
```

Note: `set-persona` rewrites `.cursor/scripts/` → `.claude/scripts/` when installing to Claude side.

### `mcp.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}" },
      "_note": "Override in client-config/personas/engineer/mcp.json for GitHub Enterprise"
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"],
      "env": {},
      "_note": "Optional. Override for internal database endpoints."
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sentry"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}",
        "SENTRY_ORG_SLUG": "${SENTRY_ORG_SLUG}"
      },
      "_note": "Optional. Override for internal Sentry instance."
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"],
      "env": {}
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {}
    }
  }
}
```

### `rules/000-engineer-workflow.mdc`

Frontmatter: `description: Engineer persona workflow rules`, `alwaysApply: true`

Sections:
- **TDD is mandatory** — write failing test first, run it, write minimum implementation, refactor
- **Subagent delegation table** — when to invoke each of the 4 agents
- **Hooks are guardrails** — if a hook blocks a command, fix the issue, do not work around it
- **Phase discipline** — do not advance phase until current phase AC are met

---

## Acceptance Criteria

- [ ] `ls personas/engineer/commands/` → `engineer-tasks.md`, `engineer-implement.md`
- [ ] `ls personas/engineer/agents/` → 4 files
- [ ] `ls personas/engineer/scripts/` → 4 files, all executable after `chmod +x`
- [ ] `cat personas/engineer/hooks.json | python3 -m json.tool` → parses cleanly
- [ ] `cat personas/engineer/mcp.json | python3 -m json.tool` → parses cleanly
- [ ] `mcp.json` has `_note` on every client-overridable server
- [ ] `block-destructive.sh` returns deny JSON for `git push --force` input
- [ ] `block-destructive.sh` returns allow JSON for `echo hello` input
- [ ] `hooks.json` references `.cursor/scripts/` (not `.claude/scripts/`) — rewriting is `set-persona`'s job
