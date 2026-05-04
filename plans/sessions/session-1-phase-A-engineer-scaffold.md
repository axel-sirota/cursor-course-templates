# Session 1 — Phase A: Engineer Persona Scaffold

**Phase:** A (Engineer persona pack)
**Goal:** Create the engineer persona directory skeleton and all non-functional files (persona.md, README.md, SETUP.md, .env.example).
**Depends on:** nothing
**Next session:** Session 2 (commands + agents + hooks)

---

## Files to Create

```
personas/engineer/
├── persona.md
├── README.md
├── SETUP.md
├── .env.example
├── commands/          (empty dir)
├── agents/            (empty dir)
├── scripts/           (empty dir)
└── rules/             (empty dir)
```

Note: `hooks.json` and `mcp.json` are created in Session 2.

---

## File Specifications

### `personas/engineer/persona.md`

Mental model, vocabulary, workflow phases, key rules for the engineer role.

- **Mental model:** Ship working code behind tests, traceable to a spec
- **Vocabulary:** Spec / Plan / Tasks / Implementation
- **Workflow phases:** Discover → Specify → Plan → Tasks → Implement → Review
- **Key rules:**
  - TDD mandatory — no implementation without a failing test
  - Every function has a typed signature
  - Secrets never enter the repo
  - Destructive shell commands require explicit allow
  - Every session begins with `start-session`, ends with `next-session`
- **Active Stack:** Set by `setup-stack` after `set-persona engineer` completes

### `personas/engineer/README.md`

What this pack adds. Student-facing. Sections:
- Commands: `engineer-tasks`, `engineer-implement`
- Subagents: `code-reviewer`, `security-auditor`, `test-runner`, `verifier`
- Hooks: `afterFileEdit` (lint + type-check), `beforeShellExecution` (block-destructive), `stop` (test suite)
- MCPs: GitHub, PostgreSQL, Sentry, Playwright, Context7
- How this pack pairs with `setup-stack`
- Prerequisites: see SETUP.md

### `personas/engineer/SETUP.md`

Pre-class student checklist. Sections:
1. AI code assistant (Cursor or Claude Code)
2. Programming language (Python 3.11+ / Node 20+ / Go 1.22+ / Java 21)
3. Git config (name + email)
4. Docker (optional, for containerized stacks)
5. MCP credentials: copy `.env.example` → `.env`, fill `GITHUB_PAT`
6. Repository access: clone `cursor-course-templates`
7. Smoke test: run `/set-persona`, pick `engineer`, then `/setup-stack blank`

### `personas/engineer/.env.example`

```
# Engineer Persona — Environment Variables
# Copy to .env in project root and fill in values.

# Required for GitHub MCP
GITHUB_PAT=ghp_your_token_here
# _note: For GitHub Enterprise, client-config/personas/engineer/mcp.json overrides the endpoint

# Optional: Sentry MCP
SENTRY_AUTH_TOKEN=
SENTRY_ORG_SLUG=
# _note: Provided by your instructor if your org uses Sentry

# Optional: PostgreSQL MCP
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
# _note: For internal databases, your instructor provides the connection string
```

---

## Acceptance Criteria

- [ ] `ls personas/engineer/` shows: `persona.md`, `README.md`, `SETUP.md`, `.env.example`, `commands/`, `agents/`, `scripts/`, `rules/`
- [ ] `cat personas/engineer/persona.md` contains `## Mental Model`, `## Vocabulary`, `## Workflow Phases`, `## Key Rules`, `## Active Stack`
- [ ] `cat personas/engineer/README.md` lists all 4 subagents, 2 commands, 3 hook events, 5 MCPs
- [ ] `cat personas/engineer/SETUP.md` has 7 numbered sections ending with smoke test
- [ ] `.env.example` has `_note` comments on every overridable field
- [ ] Existing `setup-stack` flow unaffected — test by reading `.cursor/commands/setup-stack.md` and confirming it still references `stacks/` not `personas/`
