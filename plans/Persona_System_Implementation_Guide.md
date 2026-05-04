# Persona System Implementation Guide

**Repository:** `axel-sirota/cursor-course-templates`
**Target:** Add a customizable persona-based experience (engineer, designer, PM) on top of the existing Adaptive SDLC stack-pack system.
**Driver tool:** Claude Code, working from this document as a roadmap.
**Backwards compatibility:** Mandatory — every existing flow continues to work unchanged for engineers who skip `setup-persona`.

---

## Table of Contents

1. [How to Use This Document](#how-to-use-this-document)
2. [Mental Model](#mental-model)
3. [Final Target Topology](#final-target-topology)
4. [Phase A — Engineer Persona Scaffolding](#phase-a--engineer-persona-scaffolding)
5. [Phase B — `setup-persona` Command and Manifest](#phase-b--setup-persona-command-and-manifest)
6. [Phase C — Designer Persona](#phase-c--designer-persona)
7. [Phase D — PM Persona](#phase-d--pm-persona)
8. [Phase E — Make Universal Commands Persona-Aware](#phase-e--make-universal-commands-persona-aware)
9. [Phase F — Documentation and Student-Facing Assets](#phase-f--documentation-and-student-facing-assets)
10. [Acceptance Tests](#acceptance-tests)
11. [Rollback Plan](#rollback-plan)
12. [Reference: All MCPs, Hooks, Subagents, Commands](#reference-all-mcps-hooks-subagents-commands)

---

## How to Use This Document

This guide is written to be handed to Claude Code in the root of a fresh clone of `cursor-course-templates`. Each phase contains:

- A goal statement
- A Claude Code prompt block you can paste verbatim
- A list of files to create or modify
- Concrete file content (or its specification)
- Acceptance criteria

Run phases in order. After each phase, run the acceptance test for that phase before proceeding. The phases are designed so that the repo is in a working state at every checkpoint — partial migration is safe.

When this guide says "**[Claude Code prompt]**", that is the literal text to paste into Claude Code. When it says "**File:**", that is the file Claude Code should create or modify. When it says "**Verify:**", that is the acceptance check.

### Required environment

- Node.js 20+ (for any future tooling)
- Python 3.10+ (for hook scripts)
- A working clone of `cursor-course-templates`
- Claude Code installed and running in the repo root

### A note on dual-tool symmetry

Every change in this guide affects both `.cursor/` and `.claude/` paths. Where a file goes in both, the content is identical. To avoid repeating "create the same file in `.cursor/X` and `.claude/X`" everywhere, this guide says "create at both `.cursor/X` and `.claude/X`" once and then refers to "the dual file" thereafter.

---

## Mental Model

Read this section before issuing any prompts. The whole implementation depends on getting these concepts right.

### What a persona is

A persona is a bundle of role-specific configuration that activates on top of the existing Adaptive SDLC. When a student runs `/setup-persona`, the tool copies a curated set of:

- **Commands** — slash commands the student can invoke (`engineer-implement`, `designer-extract`, `pm-validate`)
- **Subagents** — specialized AI workers with isolated context the main agent delegates to
- **Hooks** — lifecycle automations (run lint after edit, validate INVEST format on PRD save)
- **MCP servers** — external integrations (GitHub for engineers, Figma for designers, Atlassian for PMs)
- **Rules** — always-applied constraints in the system prompt

### What the engineer persona inherits

The engineer persona is the closest to the existing repo. After `setup-persona engineer`, the student then runs `setup-stack python-fastapi` (or another stack) and gets the existing flow plus the engineer's added subagents, hooks, and MCPs. **Nothing in the existing engineer flow changes.**

### What designer and PM personas need

Designer and PM are net-new. They do **not** use the `stacks/` library — there is no Python-vs-Node decision for a designer building a Figma prototype or a PM writing a PRD. Their persona definition includes everything `stacks/python-fastapi/context.md` would provide for an engineer.

### The two-tier command model

After this implementation, commands fall into two tiers:

**Tier 1 — Universal (persona-aware):** The 10 existing commands stay at `.cursor/commands/` and `.claude/commands/`. Six of them (`architect`, `start-session`, `start-project`, `code-review`, `next-session`, `read`) get a small "persona-aware" branch added near the top — they read `## Active Persona` from the context file and adjust prompts accordingly. The other four (`setup-stack`, `detect-stack`, `dockerize`, `research`, `research-export`) stay engineer-flavored or remain naturally universal.

**Tier 2 — Persona-specific:** Each persona ships a small set of commands that only make sense for that role. These are copied into `.cursor/commands/` and `.claude/commands/` by `setup-persona` and removed when switching personas.

### The manifest mechanism

The single most important piece of new infrastructure is `.cursor/.persona-manifest.json`. When `setup-persona` copies files, it records every file it touched in this manifest. When it runs again to switch personas, it reads the manifest, deletes the previous persona's files, and installs the new persona. This is what makes persona switching clean and idempotent.

### Backwards compatibility contract

A student who runs `setup-stack` directly without `setup-persona` first must still get the existing engineer flow. The repo's existing tests, examples, and documentation continue to work. `setup-persona` is purely additive.

---

## Final Target Topology

After all six phases, the repo looks like this. **Items marked NEW are added by this implementation. Items marked UPDATED are modified. Everything else is unchanged.**

```
cursor-course-templates/
├── README.md                                  # UPDATED: persona section added
├── QUICKSTART.md                              # UPDATED: persona-first workflow added
├── METHODOLOGY.md                             # UPDATED: persona section added
├── ADAPTATION_GUIDE.md                        # unchanged
├── CLAUDE.md                                  # UPDATED: placeholder text
├── student_runbook.md                         # UPDATED: per-persona flows
│
├── personas/                                  # NEW
│   ├── engineer/                              # NEW
│   │   ├── persona.md
│   │   ├── README.md
│   │   ├── SETUP.md
│   │   ├── .env.example
│   │   ├── commands/
│   │   │   ├── engineer-tasks.md
│   │   │   └── engineer-implement.md
│   │   ├── agents/
│   │   │   ├── code-reviewer.md
│   │   │   ├── security-auditor.md
│   │   │   ├── test-runner.md
│   │   │   └── verifier.md
│   │   ├── hooks.json
│   │   ├── mcp.json
│   │   ├── rules/
│   │   │   └── 000-engineer-workflow.mdc
│   │   └── scripts/
│   │       ├── lint.sh
│   │       ├── type-check.sh
│   │       ├── test-runner.sh
│   │       └── block-destructive.sh
│   │
│   ├── designer/                              # NEW
│   │   ├── persona.md
│   │   ├── README.md
│   │   ├── SETUP.md
│   │   ├── .env.example
│   │   ├── commands/
│   │   │   ├── designer-extract.md
│   │   │   ├── designer-compose.md
│   │   │   ├── designer-iterate.md
│   │   │   └── designer-handoff.md
│   │   ├── agents/
│   │   │   ├── figma-extractor.md
│   │   │   ├── token-validator.md
│   │   │   └── responsive-checker.md
│   │   ├── hooks.json
│   │   ├── mcp.json
│   │   ├── rules/
│   │   │   └── 000-designer-workflow.mdc
│   │   └── scripts/
│   │       ├── token-validator.sh
│   │       ├── no-inline-styles.sh
│   │       └── screenshot-compare.sh
│   │
│   └── pm/                                    # NEW
│       ├── persona.md
│       ├── README.md
│       ├── SETUP.md
│       ├── .env.example
│       ├── commands/
│       │   ├── pm-validate.md
│       │   ├── pm-decompose.md
│       │   └── pm-report.md
│       ├── agents/
│       │   ├── dev-perspective.md
│       │   ├── qa-perspective.md
│       │   └── gap-detector.md
│       ├── hooks.json
│       ├── mcp.json
│       ├── rules/
│       │   └── 000-pm-workflow.mdc
│       └── scripts/
│           ├── invest-validator.sh
│           ├── ac-format-check.sh
│           └── gap-detector.sh
│
├── stacks/                                    # unchanged
│   └── (existing stack packs)
│
├── .cursor/                                   # UPDATED
│   ├── commands/
│   │   ├── setup-persona.md                   # NEW
│   │   ├── setup-stack.md                     # unchanged
│   │   ├── detect-stack.md                    # unchanged
│   │   ├── architect.md                       # UPDATED: persona-aware
│   │   ├── start-session.md                   # UPDATED: persona-aware
│   │   ├── start-project.md                   # UPDATED: persona-aware
│   │   ├── research.md                        # unchanged
│   │   ├── research-export.md                 # unchanged
│   │   ├── code-review.md                     # UPDATED: persona-aware
│   │   ├── next-session.md                    # UPDATED: persona-aware
│   │   ├── read.md                            # UPDATED: persona-aware
│   │   └── dockerize.md                       # unchanged
│   ├── rules/                                 # populated at setup time
│   ├── agents/                                # populated at setup time, NEW directory
│   ├── scripts/                               # populated at setup time, NEW directory
│   ├── hooks.json                             # populated at setup time, NEW file
│   ├── mcp.json                               # populated at setup time, NEW file
│   ├── context.md                             # UPDATED: ## Active Persona field
│   └── .persona-manifest.json                 # NEW, runtime-only
│
└── .claude/                                   # symmetric mirror of .cursor/
    └── (same structure with .claude/ paths)
```

---

## Phase A — Engineer Persona Scaffolding

**Goal:** Build the engineer persona end-to-end as the reference implementation. By the end of this phase, the engineer persona pack exists in `personas/engineer/`. It is not yet wired into a `setup-persona` command — that is Phase B.

**Why engineer first:** The engineer persona is the closest to the existing repo. Building it first lets us validate the file layout and naming conventions before cloning the pattern for designer and PM.

### A.1 Create the directory scaffolding

**[Claude Code prompt]**

```
Create the following directory structure under personas/engineer/:

personas/engineer/
├── persona.md
├── README.md
├── SETUP.md
├── .env.example
├── commands/
├── agents/
├── rules/
├── scripts/
├── hooks.json
└── mcp.json

Leave the files empty for now — I will populate them in subsequent prompts. Just confirm the directories exist.
```

### A.2 Write `persona.md`

**File:** `personas/engineer/persona.md`

This file is the engineer's equivalent of `stacks/python-fastapi/context.md`. It defines the mental model, vocabulary, and key rules for the persona. It is what `architect`, `start-session`, etc. read when they want to know "what does this user actually do all day."

**Content:**

```markdown
# Engineer Persona

## Mental Model

You ship code. Your unit of delivery is a working feature behind a feature flag, with passing tests, documented in the repo, reviewed by a peer or an AI subagent, and traceable back to a spec.

## Vocabulary

- **Spec** — A technology-agnostic description of what to build (markdown).
- **Plan** — A technology-specific mapping of the spec to your stack (markdown).
- **Tasks** — A parallel-safe decomposition of the plan into independent units of work.
- **Implementation** — The TDD red→green→refactor loop that produces working code.

## Workflow Phases

1. **Discover** — Use `architect` or `start-project` to scope the problem.
2. **Specify** — Write a spec.md that names entities, contracts, and acceptance criteria.
3. **Plan** — Map the spec to your stack (Python FastAPI, Node Express, etc.) using `architect`.
4. **Tasks** — Break the plan into parallel-safe units with `engineer-tasks`.
5. **Implement** — Run `engineer-implement` to delegate tasks to subagents under a TDD loop.
6. **Review** — `code-review` for security, style, and test coverage.

## Key Rules

- TDD is mandatory. No implementation code without a failing test first.
- Every endpoint or function has a typed signature.
- Secrets never enter the repo. Hooks block this at edit time.
- Destructive shell commands (`rm -rf`, force push) require explicit allow.
- Every session begins with `start-session` and ends with `next-session`.

## Active Stack

Set by `setup-stack` after `setup-persona engineer` completes. Until then, this persona is incomplete. Run `setup-stack` to pick a stack pack from `stacks/`.
```

### A.3 Write `README.md`

**File:** `personas/engineer/README.md`

**Content:**

```markdown
# Engineer Persona Pack

This pack adds engineer-specific subagents, hooks, MCP integrations, and commands to the Adaptive SDLC.

## What this pack adds

**Commands:**
- `engineer-tasks` — Decompose a plan into parallel-safe tasks
- `engineer-implement` — Run the TDD execution loop with subagent delegation

**Subagents:**
- `code-reviewer` — Reviews diffs against active stack rules
- `security-auditor` — Scans for secret leaks, injection risks
- `test-runner` — Runs the test suite and reports failures
- `verifier` — Validates "done" claims against acceptance criteria

**Hooks:**
- `afterFileEdit` — Lint and type-check changed files
- `beforeShellExecution` — Block destructive commands
- `stop` — Run the test suite at session end

**MCP servers:**
- GitHub — Issue and PR operations
- PostgreSQL — Read-only database introspection
- Sentry — Error retrieval and analysis
- Playwright — Browser automation for E2E tests
- Context7 — Up-to-date library documentation

## How this pack pairs with `setup-stack`

After running `setup-persona engineer`, run `setup-stack` to select a stack pack (Python FastAPI, Node Express, Java Spring, Go Gin, Terraform, or blank). The persona pack and the stack pack compose: persona rules sit alongside stack rules, persona subagents work with stack-specific tooling.

## Prerequisites

See `SETUP.md` for the full pre-class checklist.
```

### A.4 Write `SETUP.md`

**File:** `personas/engineer/SETUP.md`

This is the pre-class tech setup list — it can be sent to students directly.

**Content:**

```markdown
# Engineer Persona — Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. AI code assistant

Install one of:
- Cursor IDE: https://cursor.sh
- Claude Code: https://docs.claude.com/en/docs/claude-code/overview

## 2. Programming language

Install one of (whichever you plan to use during class):
- Python 3.11+ with `pip` and `venv`
- Node.js 20+ with `npm`
- Go 1.22+
- Java 21 with Maven or Gradle

Verify with `python --version`, `node --version`, etc.

## 3. Git

Install Git and configure your name and email:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## 4. Docker (optional but recommended)

Required only if you plan to use the Python FastAPI or Node Express stacks, which run a containerized PostgreSQL.

Install Docker Desktop and confirm `docker --version` works.

## 5. MCP server credentials

Copy `personas/engineer/.env.example` to `.env` in the project root and fill in:

- `GITHUB_PAT` — A GitHub personal access token with `repo` scope (https://github.com/settings/tokens)
- `SENTRY_AUTH_TOKEN` — Optional. Only needed if your project uses Sentry.
- `DATABASE_URL` — Optional. Only needed if your project connects to a Postgres instance.

## 6. Repository access

Clone `cursor-course-templates`:

```
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

## 7. Smoke test

In the repo root, open your AI tool and run:

- Cursor: `@setup-persona`
- Claude Code: `/setup-persona`

You should see a prompt asking which persona to install. Pick `engineer`. After it completes, run `setup-stack` and pick `blank`. You should see a confirmation that the engineer persona is active and the blank stack is configured.

If any step fails, contact the instructor before class.
```

### A.5 Write `.env.example`

**File:** `personas/engineer/.env.example`

```
# Engineer Persona — Environment Variables
# Copy this file to .env in the project root and fill in your values.

# Required for GitHub MCP
GITHUB_PAT=ghp_your_token_here

# Optional: Sentry MCP
SENTRY_AUTH_TOKEN=
SENTRY_ORG_SLUG=

# Optional: PostgreSQL MCP
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Optional: Context7 MCP (no auth needed for free tier)
```

### A.6 Write the four engineer subagents

Each subagent is a markdown file with YAML frontmatter. Cursor reads `.cursor/agents/*.md`; Claude Code reads `.claude/agents/*.md`. Both formats are identical, so we ship one file and copy it to both at setup time.

**File:** `personas/engineer/agents/code-reviewer.md`

```markdown
---
name: code-reviewer
description: Reviews code changes against the active stack's rules. Use after every implementation block to catch style violations, missing tests, and architectural drift before it accumulates.
model: inherit
readonly: true
---

You are a senior code reviewer specialized in the active project's stack. Your job is to read recent changes (last commit or staged diff) and report violations against the rules in `.cursor/rules/` or `.claude/rules/`.

When invoked:

1. Read the active stack from the context file (`.cursor/context.md` or `CLAUDE.md`).
2. Load all rules from the active rules directory.
3. Run `git diff HEAD~1` (or the staged diff if instructed) to identify changed files.
4. For each changed file, check against the loaded rules:
   - Style: naming conventions, formatting, type annotations
   - Architecture: layering, dependency direction, file placement
   - Testing: every new function has a test; tests assert behavior, not implementation
   - Security: no hardcoded secrets, no `os.system` or `eval`, no SQL string concatenation
5. Output a structured report:
   - **Critical** (security risk or rule violation that blocks merge)
   - **Important** (style or architectural drift)
   - **Suggestion** (improvement, not a blocker)

Do not modify code. Only report.

Be thorough but not pedantic. If a rule is ambiguous, flag the ambiguity instead of guessing.
```

**File:** `personas/engineer/agents/security-auditor.md`

```markdown
---
name: security-auditor
description: Scans recent code changes for secret leaks, injection vulnerabilities, and unsafe patterns. Use after any change that touches authentication, database access, file I/O, or external API calls.
model: inherit
readonly: true
---

You are a security auditor. You read recent code changes and identify high-risk patterns.

When invoked:

1. Identify the diff to review (last commit, staged changes, or a specific file).
2. Scan for:
   - Hardcoded secrets (API keys, tokens, passwords, connection strings)
   - SQL injection risk (string concatenation in queries, missing parameterization)
   - Command injection (`os.system`, `subprocess` with shell=True and user input)
   - Path traversal (user-controlled paths without validation)
   - Insecure deserialization (`pickle.loads`, `yaml.load` without SafeLoader)
   - Missing authentication or authorization on new endpoints
   - Use of weak cryptography (MD5, SHA1, hardcoded IVs)
3. Output a report grouped by severity (Critical, High, Medium, Informational).

For each finding, include:
- File and line number
- The vulnerable pattern
- A concrete remediation
- A reference (OWASP, CWE) when applicable

Do not modify code. Only report.

If the diff is clean, say so plainly. Do not invent issues.
```

**File:** `personas/engineer/agents/test-runner.md`

```markdown
---
name: test-runner
description: Runs the project's test suite and reports failures with actionable summaries. Use when the main agent declares an implementation complete and needs verification, or when CI signals a failure that needs investigation.
model: inherit
readonly: false
---

You execute tests and analyze results.

When invoked:

1. Read the active stack from the context file.
2. Determine the test command from the stack (e.g., `pytest`, `npm test`, `go test ./...`).
3. Execute the test command.
4. If tests pass, report:
   - Total tests run
   - Total passed
   - Coverage percentage if available
5. If tests fail, for each failure report:
   - Test name and file
   - The assertion that failed
   - The root cause (parsed from the traceback, not just the raw output)
   - A suggested fix

Do not attempt to fix failing tests yourself. Report only. The main agent decides whether to delegate the fix back to an implementer subagent.
```

**File:** `personas/engineer/agents/verifier.md`

```markdown
---
name: verifier
description: Validates that work declared as "done" actually meets the acceptance criteria from the spec. Use after `engineer-implement` reports a task complete, before the main agent moves to the next task.
model: inherit
readonly: true
---

You are a skeptical verifier. Your job is to confirm that completed work actually works.

When invoked:

1. Read the spec or task description that was supposedly completed.
2. Identify the acceptance criteria (Given/When/Then or equivalent).
3. For each criterion, find evidence in the code that the criterion is satisfied:
   - A passing test that exercises that criterion
   - The code path that handles the case
4. Run the relevant tests to confirm they pass.
5. Try at least one edge case the implementer may not have considered:
   - Empty input
   - Maximum-size input
   - Concurrent access
   - Network failure
   - Authentication missing or expired
6. Report:
   - **Verified:** Criteria with evidence and passing tests
   - **Unverified:** Criteria the implementer claimed but you cannot confirm
   - **Edge cases failed:** Cases the implementer missed

Do not accept "the implementer said it's done" as evidence. Test it yourself.
```

### A.7 Write the engineer hook scripts

**File:** `personas/engineer/scripts/lint.sh`

```bash
#!/usr/bin/env bash
# Engineer hook: lint changed file
# Reads JSON payload from stdin (Cursor afterFileEdit format) and runs the appropriate linter.

set -euo pipefail

# Read the file_path from the JSON payload on stdin
file_path=$(jq -r '.file_path // empty')

if [[ -z "$file_path" ]]; then
  exit 0
fi

# Glob filter: only lint relevant files
case "$file_path" in
  *.py)
    if command -v ruff &>/dev/null; then
      ruff check --fix "$file_path" || true
    fi
    ;;
  *.ts|*.tsx|*.js|*.jsx)
    if command -v npx &>/dev/null; then
      npx biome check --write "$file_path" 2>/dev/null || true
    fi
    ;;
  *.go)
    if command -v gofmt &>/dev/null; then
      gofmt -w "$file_path"
    fi
    ;;
  *.java)
    # No-op for Java; relies on IDE formatter
    ;;
  *)
    # Not a code file we lint
    ;;
esac

exit 0
```

**File:** `personas/engineer/scripts/type-check.sh`

```bash
#!/usr/bin/env bash
# Engineer hook: type-check the project
# Runs after a file edit. Scoped by file extension so Python projects don't trigger tsc and vice versa.

set -euo pipefail

file_path=$(jq -r '.file_path // empty')
[[ -z "$file_path" ]] && exit 0

case "$file_path" in
  *.py)
    if command -v mypy &>/dev/null && [[ -f "mypy.ini" || -f "pyproject.toml" ]]; then
      mypy "$file_path" 2>/dev/null || true
    fi
    ;;
  *.ts|*.tsx)
    if command -v npx &>/dev/null && [[ -f "tsconfig.json" ]]; then
      npx tsc --noEmit 2>/dev/null || true
    fi
    ;;
  *.go)
    go vet ./... 2>/dev/null || true
    ;;
esac

exit 0
```

**File:** `personas/engineer/scripts/test-runner.sh`

```bash
#!/usr/bin/env bash
# Engineer hook: run the test suite at session end
# Triggered by the `stop` lifecycle event.

set -euo pipefail

if [[ -f "pyproject.toml" || -f "setup.py" ]]; then
  if command -v pytest &>/dev/null; then
    pytest -x --tb=short 2>/dev/null || echo "Tests failed. Review output before next session."
  fi
elif [[ -f "package.json" ]]; then
  if grep -q '"test"' package.json; then
    npm test --silent 2>/dev/null || echo "Tests failed. Review output before next session."
  fi
elif [[ -f "go.mod" ]]; then
  go test ./... 2>/dev/null || echo "Tests failed. Review output before next session."
fi

exit 0
```

**File:** `personas/engineer/scripts/block-destructive.sh`

```bash
#!/usr/bin/env bash
# Engineer hook: block destructive shell commands
# Triggered by `beforeShellExecution`. Reads command from stdin JSON, returns JSON to allow/deny.

set -euo pipefail

command=$(jq -r '.command // empty')

# Deny-list of destructive patterns
deny_patterns=(
  'rm -rf /'
  'rm -rf ~'
  'rm -rf \.\$'
  'git push --force'
  'git push -f '
  'git reset --hard origin'
  'DROP DATABASE'
  'DROP TABLE'
  'TRUNCATE TABLE'
  'sudo rm'
  'mkfs'
  'dd if='
)

for pattern in "${deny_patterns[@]}"; do
  if echo "$command" | grep -qE "$pattern"; then
    cat <<EOF
{
  "continue": true,
  "permission": "deny",
  "userMessage": "Blocked destructive command: $pattern. If this is intentional, run it in a terminal outside the agent.",
  "agentMessage": "The user's policy blocks this command pattern. Suggest a safer alternative."
}
EOF
    exit 0
  fi
done

# Allow by default
echo '{"continue": true, "permission": "allow"}'
exit 0
```

### A.8 Write the engineer `hooks.json`

**File:** `personas/engineer/hooks.json`

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

A note on paths: this JSON ships in `personas/engineer/` referencing `.cursor/scripts/` because `setup-persona` copies the scripts to `.cursor/scripts/` (and `.claude/scripts/`) at activation time. The `setup-persona` command is responsible for rewriting paths to `.claude/scripts/` when copying to the Claude Code side.

### A.9 Write the engineer `mcp.json`

**File:** `personas/engineer/mcp.json`

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"],
      "env": {}
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sentry"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}",
        "SENTRY_ORG_SLUG": "${SENTRY_ORG_SLUG}"
      }
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

### A.10 Write the engineer rule

**File:** `personas/engineer/rules/000-engineer-workflow.mdc`

```markdown
---
description: Engineer persona workflow rules. Always applied when the engineer persona is active.
alwaysApply: true
---

# Engineer Workflow Rules

## TDD is mandatory

Never write implementation code without a failing test first. The order is:

1. Write a test that asserts the behavior you want.
2. Run the test and confirm it fails.
3. Write the minimum code to make it pass.
4. Refactor with the test as a safety net.

If asked to implement something without a test, propose the test first and ask for approval before writing implementation code.

## Subagent delegation

When a task involves more than one of {writing implementation, reviewing security, running tests, validating completeness}, delegate to the appropriate subagent:

- New endpoint with auth or DB access → `security-auditor` after writing
- Implementation declared complete → `verifier` to confirm
- Test failures unclear → `test-runner` for structured analysis
- PR-sized diff → `code-reviewer` before commit

Subagents have isolated context. Pass them what they need; do not assume they remember earlier conversation.

## Hooks are guardrails, not suggestions

If a hook blocks a command, do not work around it. Either fix the underlying issue or flag it to the user.

## Phase discipline

Do not advance phase until the current phase's acceptance criteria are met. The phases are defined in `stacks/{active-stack}/vibe/phase_workflow.md` if present, otherwise the methodology default: Phase 0 (Skeleton) → Phase 1+ (Implementation per endpoint).
```

### A.11 Write the two engineer-specific commands

**File:** `personas/engineer/commands/engineer-tasks.md`

```markdown
# /engineer-tasks

**Purpose:** Decompose a plan from `architect` into a list of parallel-safe tasks ready for `engineer-implement`.

**Prerequisites:**
- A plan exists at `docs/plan-{feature}.md` produced by `architect`
- The active persona is `engineer` (verify in `.cursor/context.md` or `CLAUDE.md`)

**What this command does:**

1. Read the plan from `docs/plan-{feature}.md` (ask the user which plan if multiple).
2. Identify natural task boundaries:
   - Each endpoint or function = one task
   - Each test file = one task (if doing TDD strictly per file)
   - Each migration = one task
3. For each task, declare:
   - `id` — short slug
   - `title` — one-line description
   - `acceptance` — Given/When/Then format
   - `touched_files` — files this task will create or modify
   - `depends_on` — list of task IDs that must complete first
4. Detect file conflicts: if two tasks modify the same file, mark them as sequential, not parallel.
5. Output `docs/tasks-{feature}.md` as a markdown table plus per-task detail sections.

**Example invocation:**

```
/engineer-tasks
```

Then reads `docs/plan-task-management-api.md` and writes `docs/tasks-task-management-api.md`.

**Output schema:**

The tasks file has two sections:

1. **Summary table:** id, title, depends_on, parallel-safe? (yes/no)
2. **Per-task detail:** acceptance criteria, touched files, suggested subagent for review

`engineer-implement` consumes this file directly.
```

**File:** `personas/engineer/commands/engineer-implement.md`

```markdown
# /engineer-implement

**Purpose:** Execute the TDD loop on a tasks file produced by `engineer-tasks`. Delegates work to subagents and verifies each task before moving on.

**Prerequisites:**
- A tasks file exists at `docs/tasks-{feature}.md`
- Subagents `code-reviewer`, `security-auditor`, `test-runner`, `verifier` are available in `.cursor/agents/` or `.claude/agents/`
- The active persona is `engineer`

**What this command does:**

For each task in the tasks file, in dependency order:

1. **Red:** Write a failing test that exercises the acceptance criteria.
2. **Run:** Invoke the `test-runner` subagent. Confirm the test fails for the expected reason.
3. **Green:** Write the minimum implementation to make the test pass.
4. **Run:** Invoke `test-runner` again. Confirm the test now passes and no other tests broke.
5. **Audit:** If the task touched authentication, database access, or external I/O, invoke `security-auditor`. Address any Critical findings before continuing.
6. **Verify:** Invoke `verifier` against the original acceptance criteria. Confirm criteria are met.
7. **Refactor:** Clean up duplication or unclear naming, with the test as safety net.
8. **Mark complete:** Update the tasks file to mark the task done.

**Parallel execution:**

Tasks marked `parallel-safe? yes` and with no unmet dependencies can be delegated to background subagents using Cursor's `is_background: true` or Claude Code's agent teams. Default to sequential unless the user explicitly requests parallelism.

**Stop conditions:**

- A task fails verification three times → pause and ask the user
- A security-auditor finding is Critical → stop and ask the user
- Any test outside the task's scope starts failing → stop and ask the user

**Output:**

A summary at the end of the run:
- Tasks completed
- Tasks blocked (with reasons)
- Tests added (count and coverage delta if available)
- Subagent invocations and any non-trivial findings

**Example invocation:**

```
/engineer-implement
```

Reads `docs/tasks-task-management-api.md`, executes each task, and writes a session summary to `docs/sessions/{date}-{feature}.md` for `next-session` to pick up.
```

### A.12 Phase A acceptance test

**[Verify]**

Run these checks. All must pass before moving to Phase B.

1. `ls personas/engineer/` shows: `persona.md`, `README.md`, `SETUP.md`, `.env.example`, `commands/`, `agents/`, `rules/`, `scripts/`, `hooks.json`, `mcp.json`
2. `ls personas/engineer/commands/` shows two files: `engineer-tasks.md`, `engineer-implement.md`
3. `ls personas/engineer/agents/` shows four files: `code-reviewer.md`, `security-auditor.md`, `test-runner.md`, `verifier.md`
4. `ls personas/engineer/scripts/` shows four files: `lint.sh`, `type-check.sh`, `test-runner.sh`, `block-destructive.sh`
5. `chmod +x personas/engineer/scripts/*.sh` succeeds
6. `cat personas/engineer/hooks.json | jq .` parses without error
7. `cat personas/engineer/mcp.json | jq .` parses without error
8. The existing `setup-stack` flow still works: in a separate clone, run `setup-stack python-fastapi` and confirm the existing engineer flow is unchanged

---

## Phase B — `setup-persona` Command and Manifest

**Goal:** Build the entry-point command that activates a persona pack. After this phase, students can run `setup-persona` and get the engineer persona installed.

### B.1 Write `setup-persona.md`

This file goes in **both** `.cursor/commands/` and `.claude/commands/` (identical content). The dual-tool symmetry is preserved by having the same content in both places.

**File:** `.cursor/commands/setup-persona.md` and `.claude/commands/setup-persona.md`

```markdown
# /setup-persona

**Purpose:** Activate a persona pack on the current project. Personas bundle role-specific commands, subagents, hooks, MCP servers, and rules.

**When to use:** First step in any new project, before `setup-stack`. If you switch personas mid-project, run this command again — it will cleanly remove the previous persona's files before installing the new one.

## What this command does

### Step 1: Detect existing persona

Read `.cursor/.persona-manifest.json` (or `.claude/.persona-manifest.json` if running in Claude Code). If a persona is already active, list every file the previous persona installed and ask the user to confirm removal before proceeding.

### Step 2: Prompt for persona selection

Present three options:

1. **engineer** — Software developers using AI for spec-driven development
2. **designer** — Designers using AI for design-system-aware prototyping
3. **pm** — Product managers using AI for PRDs, validation, and ticket decomposition

Show a one-paragraph summary of each from `personas/{role}/README.md`.

### Step 3: Remove previous persona (if any)

For every entry in `.persona-manifest.json`, delete the file. Then delete the manifest itself. Confirm removal completed cleanly.

### Step 4: Copy persona files

For the selected persona, copy:

- `personas/{role}/commands/*.md` → `.cursor/commands/` and `.claude/commands/`
- `personas/{role}/agents/*.md` → `.cursor/agents/` and `.claude/agents/`
- `personas/{role}/scripts/*.sh` → `.cursor/scripts/` and `.claude/scripts/` (chmod +x)
- `personas/{role}/rules/*.mdc` → `.cursor/rules/` and `.claude/rules/`
- `personas/{role}/hooks.json` → `.cursor/hooks.json` (rewrite paths if needed) and `.claude/hooks.json`
- `personas/{role}/mcp.json` → `.cursor/mcp.json` and `.claude/mcp.json`

For each copied file, append its destination path to a new `.persona-manifest.json` at both `.cursor/.persona-manifest.json` and `.claude/.persona-manifest.json`.

### Step 5: Update context file

Update `.cursor/context.md` and `CLAUDE.md`:

- If the file does not exist or is the placeholder, create it with:
  ```
  # Project Context
  
  ## Active Persona
  {selected_role}
  
  ## Active Stack
  (set by /setup-stack — engineer persona only)
  ```
- If the file exists, find or insert an `## Active Persona` section and set it to the selected role.

### Step 6: Persona-specific follow-up

- **engineer:** Print a message instructing the user to run `setup-stack` next.
- **designer:** Skip stack selection. Print a message instructing the user to copy `personas/designer/.env.example` to `.env` and fill in `FIGMA_ACCESS_TOKEN`.
- **pm:** Skip stack selection. Print a message instructing the user to copy `personas/pm/.env.example` to `.env` and fill in Atlassian credentials.

### Step 7: Confirmation summary

Output:

```
✅ Persona active: {role}

Commands available: {list of persona-specific commands plus universal commands}
Subagents loaded: {list}
Hooks active: {summary by lifecycle event}
MCP servers configured: {list, marking which need credentials in .env}

Next step: {persona-specific instruction}
```

## Manifest format

`.persona-manifest.json`:

```json
{
  "persona": "engineer",
  "installed_at": "2026-05-04T12:00:00Z",
  "files": [
    ".cursor/commands/engineer-tasks.md",
    ".cursor/commands/engineer-implement.md",
    ".cursor/agents/code-reviewer.md",
    ".cursor/agents/security-auditor.md",
    ".cursor/agents/test-runner.md",
    ".cursor/agents/verifier.md",
    ".cursor/scripts/lint.sh",
    ".cursor/scripts/type-check.sh",
    ".cursor/scripts/test-runner.sh",
    ".cursor/scripts/block-destructive.sh",
    ".cursor/rules/000-engineer-workflow.mdc",
    ".cursor/hooks.json",
    ".cursor/mcp.json"
  ]
}
```

## Errors

- **Source file missing:** Abort and report which file. Do not proceed with a partial install.
- **Destination file exists and is not in the manifest:** Ask the user — overwrite or abort.
- **Manifest exists but lists files that no longer exist on disk:** Warn but continue (treat as already-removed).
```

### B.2 Path-rewriting logic for `hooks.json`

The hooks.json in `personas/engineer/` references `.cursor/scripts/...`. When copying to the Claude Code side, paths must become `.claude/scripts/...`.

**[Claude Code prompt]**

```
Update the setup-persona command's Step 4 logic to handle hooks.json path rewriting:

When copying personas/{role}/hooks.json to .cursor/hooks.json, copy verbatim.
When copying personas/{role}/hooks.json to .claude/hooks.json, replace every occurrence of ".cursor/scripts/" with ".claude/scripts/" before writing.

Document this in the setup-persona.md file under Step 4.
```

### B.3 Update `CLAUDE.md` placeholder

**File:** `CLAUDE.md` (root, not `.claude/CLAUDE.md`)

**Old content:**
```markdown
# Project Context

> ⚠️ No Stack Configured
>
> This project has not been configured yet.
> Please run /setup-stack to initialize the development environment.
```

**New content:**
```markdown
# Project Context

> ⚠️ No Persona Configured
>
> This project has not been configured yet.
> Please run /setup-persona to choose your role (engineer, designer, or pm).
> After picking a persona, engineers will be prompted to run /setup-stack next.
```

### B.4 Phase B acceptance test

**[Verify]**

1. From a clean clone, in Claude Code, run `/setup-persona`. Pick `engineer`. Confirm:
   - `.persona-manifest.json` exists at `.cursor/` and `.claude/`
   - Engineer files are present in `.cursor/agents/`, `.cursor/scripts/`, `.cursor/commands/`, `.cursor/rules/`
   - Engineer files are present in `.claude/agents/`, `.claude/scripts/`, `.claude/commands/`, `.claude/rules/`
   - `.cursor/hooks.json` references `.cursor/scripts/...`
   - `.claude/hooks.json` references `.claude/scripts/...`
   - `CLAUDE.md` has `## Active Persona: engineer`
2. Run `/setup-stack` and pick `python-fastapi`. Confirm the existing engineer flow runs and stack rules are merged with engineer rules.
3. Run `/setup-persona` again, pick `engineer` again. Confirm it idempotently re-installs without duplicating files.
4. Manually create a fake file at `.cursor/agents/code-reviewer.md` with garbage content. Run `/setup-persona engineer`. Confirm it asks before overwriting.

---

## Phase C — Designer Persona

**Goal:** Build the designer persona pack with the same structure as engineer. By the end of this phase, `setup-persona designer` works end-to-end.

### C.1 Directory scaffolding

**[Claude Code prompt]**

```
Create personas/designer/ with the same structure as personas/engineer/:

personas/designer/
├── persona.md
├── README.md
├── SETUP.md
├── .env.example
├── commands/
├── agents/
├── rules/
├── scripts/
├── hooks.json
└── mcp.json
```

### C.2 `personas/designer/persona.md`

```markdown
# Designer Persona

## Mental Model

You ship visual experiences. Your unit of delivery is a working prototype that consumes existing design tokens and components, faithful to the Figma source of truth, with logic preserved and a clear handoff to engineering.

## Vocabulary

- **Source of truth** — The Figma file, accessed via the Figma MCP.
- **Design tokens** — Named values for color, spacing, typography, radius. Never hardcoded in components.
- **Components** — Reusable building blocks already in the codebase. Reused, not reinvented.
- **Prototype** — A running implementation of the design intent, not a redesign.
- **Handoff** — A PR description with what changed, what was preserved, and what reviewers should check.

## Workflow Phases

1. **Discover** — Use `start-project` to scope the design problem.
2. **Extract** — Use `designer-extract` to pull tokens, components, and layout from Figma via MCP.
3. **Compose** — Use `designer-compose` to assemble the prototype from existing components.
4. **Iterate** — Use `designer-iterate` (Visual Editor / Design Mode) to refine spacing, hierarchy, and interactions.
5. **Handoff** — Use `designer-handoff` to generate a PR description with before/after, scope notes, and a designer QA checklist.

## Key Rules

- **Keep logic intact.** Never rewrite handlers, routes, or state management. Visual changes only.
- **Minimal diff.** The smallest change that achieves the design intent.
- **Reuse existing tokens and components.** Do not invent new conventions.
- **Figma is the source of truth.** Layout, spacing, and color values come from the Figma file via MCP.
- **No hardcoded values.** Every color, spacing, font size, and radius must reference a token.
```

### C.3 `personas/designer/README.md`

```markdown
# Designer Persona Pack

This pack adds designer-specific subagents, hooks, MCP integrations, and commands to the Adaptive SDLC.

## What this pack adds

**Commands:**
- `designer-extract` — Pull tokens, components, and layout from Figma via MCP
- `designer-compose` — Assemble a prototype from existing components
- `designer-iterate` — Refine via Visual Editor / Design Mode
- `designer-handoff` — Generate PR description with before/after and scope notes

**Subagents:**
- `figma-extractor` — Read-only Figma context fetcher
- `token-validator` — Verifies no hardcoded color/spacing/font values
- `responsive-checker` — Verifies mobile/tablet/desktop breakpoints

**Hooks:**
- `afterFileEdit` (CSS/SCSS/TSX/JSX) — Run token validator and no-inline-styles check
- `stop` — Run screenshot comparison vs Figma reference

**MCP servers:**
- Figma — Direct read of design tokens, components, layouts
- Playwright — Visual regression and responsive screenshots
- Context7 — Up-to-date framework documentation (React, Vue, Svelte)

## Why no `setup-stack` step

Designer work is framework-agnostic at the persona level. The codebase already has its framework chosen; the designer's job is to ship visual changes inside it without disturbing logic. There is no Python-vs-Node decision to make.

## Prerequisites

See `SETUP.md` for the full pre-class checklist, including Figma access token setup.
```

### C.4 `personas/designer/SETUP.md`

```markdown
# Designer Persona — Pre-Class Setup

Complete every item below before class.

## 1. AI code assistant

Install one of:
- Cursor IDE: https://cursor.sh
- Claude Code: https://docs.claude.com/en/docs/claude-code/overview

## 2. Figma desktop app

Required for the Figma MCP server (the MCP runs locally and talks to the desktop app, not the web version).

Install Figma desktop: https://www.figma.com/downloads/

In Figma desktop, enable the MCP server:
1. Click the Figma icon (top-left) → Preferences
2. Check "Enable Dev Mode MCP Server"
3. Restart Figma

## 3. Figma access token

Generate a personal access token: https://www.figma.com/developers/api#access-tokens

Copy `personas/designer/.env.example` to `.env` and set `FIGMA_ACCESS_TOKEN`.

## 4. Node.js

Install Node.js 20+ for running the prototype. The class repo will use a JavaScript framework (React, Svelte, or Vue) chosen by the instructor.

## 5. Repository access

Clone `cursor-course-templates` and complete the smoke test in section 7 below.

## 6. Browser

Chrome or Chromium-based for Playwright MCP visual regression. Other browsers work but Playwright defaults assume Chromium.

## 7. Smoke test

In the repo root, open your AI tool and run `/setup-persona`. Pick `designer`. You should see a confirmation listing the designer commands and the Figma MCP. If Figma MCP shows an error, verify the desktop app is running with Dev Mode MCP enabled.
```

### C.5 `personas/designer/.env.example`

```
# Designer Persona — Environment Variables

# Required for Figma MCP
FIGMA_ACCESS_TOKEN=figd_your_token_here

# Optional: Context7 (no auth needed for free tier)
```

### C.6 Designer subagents

**File:** `personas/designer/agents/figma-extractor.md`

```markdown
---
name: figma-extractor
description: Read-only fetcher for Figma file context. Use when starting a new design implementation or when the main agent needs design tokens, component specs, or layout data from a Figma file.
model: inherit
readonly: true
---

You extract Figma context via the Figma MCP. You never modify the Figma file or the codebase.

When invoked with a Figma URL or node ID:

1. Use the Figma MCP to fetch:
   - Design tokens (colors, spacing, typography, radius, shadows)
   - Component definitions and variants
   - Layout structure (auto-layout, grids, breakpoints)
   - Asset references (icons, images)
2. Save extracted context to a structured markdown file at `docs/figma-context-{frame-name}.md` containing:
   - Token table (name → value)
   - Component table (name → variants → props mapping)
   - Layout description in plain language
   - Asset URLs and download paths
3. Report back to the main agent with:
   - Path to the context file
   - Count of tokens, components, assets extracted
   - Any inconsistencies found (e.g., hardcoded values in the Figma file itself)

Do not write component implementation. Only extract and document.
```

**File:** `personas/designer/agents/token-validator.md`

```markdown
---
name: token-validator
description: Scans CSS, SCSS, and JSX/TSX files for hardcoded color, spacing, or typography values. Use after any file edit to a styling file or as a stop-time check before commit.
model: inherit
readonly: true
---

You enforce design token discipline.

When invoked:

1. Read the file or diff to validate.
2. Scan for hardcoded values:
   - Colors: hex codes (`#FFF`, `#1a2b3c`), `rgb()`, `rgba()`, `hsl()`, named colors
   - Spacing: pixel values in margin, padding, gap, width, height (acceptable: 0, 1px borders)
   - Typography: hardcoded `font-size`, `font-weight`, `line-height` in px, em, or numeric
   - Radius: hardcoded `border-radius` values
3. For each violation, look up whether a matching token exists in the design system (check `tokens.json`, `theme.ts`, or the relevant tokens file).
4. Report:
   - **Violation:** file, line, hardcoded value, suggested token replacement (if found)
   - **Unmatched:** hardcoded value with no obvious token match — flag for human decision

Do not modify code. Only report.

Use Context7 MCP if you need to look up framework-specific token conventions (Tailwind, MUI, Chakra, etc.).
```

**File:** `personas/designer/agents/responsive-checker.md`

```markdown
---
name: responsive-checker
description: Verifies that visual changes work across mobile, tablet, and desktop breakpoints. Use at the end of a designer-iterate session before generating the handoff.
model: inherit
readonly: false
---

You verify responsive behavior.

When invoked:

1. Identify the URL of the running prototype (default: http://localhost:3000 or as specified by the user).
2. Use the Playwright MCP to take screenshots at three breakpoints:
   - Mobile: 375 × 667
   - Tablet: 768 × 1024
   - Desktop: 1440 × 900
3. For each screenshot:
   - Save to `docs/responsive/{breakpoint}-{page}.png`
   - Note any visible issues: overflow, broken layout, hidden content, text truncation
4. Report:
   - Breakpoint pass/fail with screenshot paths
   - Specific issues per breakpoint
   - Suggested fixes referencing the existing responsive utilities in the codebase

Do not modify code. Only report.
```

### C.7 Designer hook scripts

**File:** `personas/designer/scripts/token-validator.sh`

```bash
#!/usr/bin/env bash
# Designer hook: validate design tokens on changed file
set -euo pipefail

file_path=$(jq -r '.file_path // empty')
[[ -z "$file_path" ]] && exit 0

case "$file_path" in
  *.css|*.scss|*.tsx|*.jsx|*.vue|*.svelte)
    # Look for hardcoded hex colors outside of comments
    if grep -nE '#[0-9a-fA-F]{3,6}' "$file_path" | grep -v '//\|/\*\|<!--'; then
      echo "WARNING: Hardcoded hex color in $file_path. Use a design token instead." >&2
    fi
    # Look for hardcoded pixel values in margin/padding/gap (rough heuristic)
    if grep -nE '(margin|padding|gap):\s*[0-9]+px' "$file_path" | grep -v '0px\|1px'; then
      echo "WARNING: Hardcoded spacing in $file_path. Use a spacing token instead." >&2
    fi
    ;;
esac

exit 0
```

**File:** `personas/designer/scripts/no-inline-styles.sh`

```bash
#!/usr/bin/env bash
# Designer hook: warn about inline styles in JSX/TSX
set -euo pipefail

file_path=$(jq -r '.file_path // empty')
[[ -z "$file_path" ]] && exit 0

case "$file_path" in
  *.tsx|*.jsx)
    if grep -nE 'style=\{\{' "$file_path"; then
      echo "WARNING: Inline style in $file_path. Use a className with design tokens." >&2
    fi
    ;;
esac

exit 0
```

**File:** `personas/designer/scripts/screenshot-compare.sh`

```bash
#!/usr/bin/env bash
# Designer hook: take a screenshot at session end for visual regression baseline
# Triggered by `stop`. The actual comparison happens in the responsive-checker subagent.
set -euo pipefail

mkdir -p docs/screenshots
echo "Session ended. Run @responsive-checker to generate breakpoint screenshots." >&2
exit 0
```

### C.8 Designer `hooks.json`

**File:** `personas/designer/hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      { "command": ".cursor/scripts/token-validator.sh" },
      { "command": ".cursor/scripts/no-inline-styles.sh" }
    ],
    "stop": [
      { "command": ".cursor/scripts/screenshot-compare.sh" }
    ]
  }
}
```

### C.9 Designer `mcp.json`

**File:** `personas/designer/mcp.json`

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--figma-api-key=${FIGMA_ACCESS_TOKEN}", "--stdio"],
      "env": {}
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

### C.10 Designer rule

**File:** `personas/designer/rules/000-designer-workflow.mdc`

```markdown
---
description: Designer persona workflow rules. Always applied when the designer persona is active.
alwaysApply: true
---

# Designer Workflow Rules

## Three guardrails for every visual change

1. **Keep logic intact.** Do not modify route handlers, event handlers, form submissions, state management, or data fetching. Visual changes only.
2. **Minimal diff.** The smallest change that achieves the design intent. Avoid refactoring "while you're in there."
3. **Reuse existing tokens and components.** Do not introduce new color values, spacing values, or component patterns when existing ones cover the case.

## Figma is the source of truth

When in doubt about a value, check Figma via the Figma MCP. Do not invent measurements.

## Workflow

1. Start with `designer-extract` to pull current Figma context.
2. Use `designer-compose` to assemble from existing components.
3. Iterate visually with `designer-iterate` — annotate elements directly in the running prototype rather than describing them in text.
4. Use `designer-handoff` to generate the PR description.

## Subagent delegation

- Style file edited → `token-validator` to check for hardcoded values
- Layout change complete → `responsive-checker` to verify breakpoints
- Figma URL provided → `figma-extractor` to fetch context
```

### C.11 Designer commands

**File:** `personas/designer/commands/designer-extract.md`

```markdown
# /designer-extract

**Purpose:** Pull design tokens, components, and layout from a Figma file via the Figma MCP.

**Prerequisites:**
- The Figma desktop app is running with Dev Mode MCP enabled
- `FIGMA_ACCESS_TOKEN` is set in `.env`
- The active persona is `designer`

**What this command does:**

1. Ask for a Figma URL or frame node ID.
2. Delegate to the `figma-extractor` subagent with the URL.
3. The subagent saves extracted context to `docs/figma-context-{frame-name}.md`.
4. Report the path and a one-line summary of what was extracted (token count, component count, asset count).

**Example invocation:**

```
/designer-extract https://www.figma.com/file/abc123/Design?node-id=4-200
```

**Output:**

A markdown file at `docs/figma-context-{frame-name}.md` containing:
- Token table
- Component variant matrix
- Layout description
- Asset URLs

This file is consumed by `designer-compose`.
```

**File:** `personas/designer/commands/designer-compose.md`

```markdown
# /designer-compose

**Purpose:** Assemble a working prototype from a Figma context file plus existing components in the codebase.

**Prerequisites:**
- A Figma context file exists at `docs/figma-context-{frame-name}.md`
- The codebase has an existing component library
- The active persona is `designer`

**What this command does:**

1. Read the Figma context file.
2. For each component referenced in the layout:
   - Search the codebase for an existing matching component
   - If found: import and use it
   - If not found: ask whether to create or reuse a similar one
3. Apply the layout using existing layout primitives (flex/grid utilities, spacing tokens).
4. Wire up empty handlers — do not invent business logic.
5. Output: a working component or page in the codebase, plus a summary of:
   - Components reused
   - Tokens applied
   - Stubs left for engineering to fill in

**Constraints (enforced by the designer rule):**

- No hardcoded color or spacing values
- No inline styles
- No modification of existing handlers or state

**Example invocation:**

```
/designer-compose docs/figma-context-checkout-page.md
```

**Output:**

New or updated component files matching the Figma source. After this command, run `designer-iterate` to refine.
```

**File:** `personas/designer/commands/designer-iterate.md`

```markdown
# /designer-iterate

**Purpose:** Refine a composed prototype using Visual Editor / Design Mode (clicking on elements directly rather than describing them in text).

**Prerequisites:**
- A composed prototype exists and is running locally (`npm run dev` or equivalent)
- The active persona is `designer`

**What this command does:**

1. Confirm the running URL (default: http://localhost:3000).
2. Open the Visual Editor / Design Mode in the AI tool.
3. Walk the user through the iterate loop:
   - Click an element on the running page
   - State the change in plain language ("more vertical breathing room here")
   - The agent translates the click + statement into a code change
   - The change applies and the page hot-reloads
4. After three to five iterations, suggest invoking `responsive-checker` to confirm breakpoints still work.

**Example invocation:**

```
/designer-iterate
```

Then click and describe changes interactively. There is no "command argument" — this is an interactive loop.

**Output:**

Updated component files with iterative refinements. The hot reload provides immediate visual feedback. When done, run `designer-handoff`.
```

**File:** `personas/designer/commands/designer-handoff.md`

```markdown
# /designer-handoff

**Purpose:** Generate a PR description and reviewer checklist for the visual changes made in this session.

**Prerequisites:**
- A working branch with visual changes
- The active persona is `designer`

**What this command does:**

1. Run `git diff main...HEAD --stat` to identify changed files.
2. Categorize changes:
   - **Visual changes** (CSS, JSX classNames, layout)
   - **Tokens used** (which design tokens appeared in the diff)
   - **Components reused** (which existing components were imported)
   - **Logic preserved** (confirm no handlers, routes, or state files were modified)
3. Run `responsive-checker` to capture breakpoint screenshots.
4. Generate `PR_DESCRIPTION.md` with sections:
   - **What changed** (2–4 bullet points)
   - **What was preserved** (logic, routes, handlers — explicit)
   - **Screens to review** (screenshots from responsive-checker)
   - **Designer QA checklist** (matched Figma source: yes/no, breakpoints work: yes/no, tokens used: yes/no)
5. Output the PR description path and a one-line summary.

**Example invocation:**

```
/designer-handoff
```

**Output:**

A `PR_DESCRIPTION.md` file ready to paste into a GitHub or GitLab PR, plus screenshots in `docs/responsive/`.
```

### C.12 Phase C acceptance test

**[Verify]**

1. From a clean clone, run `/setup-persona`. Pick `designer`. Confirm:
   - Designer files copied to `.cursor/` and `.claude/`
   - Manifest lists 13 files (4 commands, 3 agents, 3 scripts, 1 rule, hooks.json, mcp.json, plus the persona.md reference)
   - `CLAUDE.md` shows `## Active Persona: designer`
   - Output message instructs to copy `.env.example` and set `FIGMA_ACCESS_TOKEN`
2. Switch personas: run `/setup-persona engineer`. Confirm:
   - Designer files removed cleanly per manifest
   - Engineer files installed
   - `CLAUDE.md` updated to `## Active Persona: engineer`
3. Verify `personas/designer/hooks.json` and `personas/designer/mcp.json` parse as valid JSON.

---

## Phase D — PM Persona

**Goal:** Build the PM persona pack. Same structure as engineer and designer.

### D.1 Directory scaffolding

**[Claude Code prompt]**

```
Create personas/pm/ with the same structure as personas/engineer/ and personas/designer/.
```

### D.2 `personas/pm/persona.md`

```markdown
# PM Persona

## Mental Model

You ship clarity. Your unit of delivery is a PRD that engineering can build, with INVEST user stories, Given/When/Then acceptance criteria, edge cases identified, and tickets decomposed and dependency-ordered.

## Vocabulary

- **PRD** — Product Requirements Document. Markdown file in `prds/` or `docs/`.
- **User story** — INVEST-compliant: Independent, Negotiable, Valuable, Estimable, Small, Testable.
- **Acceptance criteria** — Given/When/Then format.
- **Three Amigos** — PM, Dev, QA review. Simulated via subagents.
- **Epic** — A collection of related user stories.
- **Decomposition** — Breaking an epic into tickets with dependencies.

## Workflow Phases

1. **Discover** — Use `start-project` to scope an opportunity from research, interview notes, or stakeholder input.
2. **Specify** — Use `architect` to draft the PRD with INVEST stories and acceptance criteria.
3. **Validate** — Use `pm-validate` to run the Three Amigos critique via subagents.
4. **Decompose** — Use `pm-decompose` to break the epic into Jira tickets with dependencies.
5. **Track** — Use `pm-report` to generate status updates from Jira and Confluence.

## Key Rules

- Every user story is INVEST-compliant. Run `pm-validate` to enforce.
- Every story has at least one Given/When/Then acceptance criterion.
- Every PRD has a section for non-functional requirements (performance, security, accessibility).
- Edge cases are explicitly listed, not left implicit.
- Tickets are written from the user's perspective ("As a..."), not the engineer's perspective ("Implement...").
```

### D.3 `personas/pm/README.md`

```markdown
# PM Persona Pack

This pack adds product manager–specific subagents, hooks, MCP integrations, and commands to the Adaptive SDLC.

## What this pack adds

**Commands:**
- `pm-validate` — Three Amigos critique on a PRD
- `pm-decompose` — Break an epic into Jira tickets with dependencies
- `pm-report` — Generate status updates from Jira and Confluence

**Subagents:**
- `dev-perspective` — Technical feasibility critique
- `qa-perspective` — Edge case and testability finder
- `gap-detector` — Finds missing NFRs, edge cases, and ambiguous criteria

**Hooks:**
- `afterFileEdit` (markdown in `prds/`, `docs/`) — Run INVEST validator and AC format check
- `stop` — Run gap-detector against the active PRD

**MCP servers:**
- Atlassian — Jira and Confluence integration
- GitHub Issues — For repos using GitHub Issues instead of Jira
- Slack — Stakeholder communication and status posting
- Notion — Alternative documentation surface

## Why no `setup-stack` step

PM work is not tied to a tech stack. The PRD describes what to build; the engineer's stack determines how. The PM persona produces markdown artifacts (PRDs, user stories, status reports) and external service operations (Jira tickets, Confluence pages).

## Prerequisites

See `SETUP.md`.
```

### D.4 `personas/pm/SETUP.md`

```markdown
# PM Persona — Pre-Class Setup

## 1. AI code assistant

Cursor or Claude Code installed and verified.

## 2. Atlassian credentials

You will need read access to a Jira project and write access if you plan to test ticket creation.

Generate an Atlassian API token: https://id.atlassian.com/manage-profile/security/api-tokens

Copy `personas/pm/.env.example` to `.env` and set:

- `JIRA_URL` (e.g., https://yourcompany.atlassian.net)
- `JIRA_USERNAME` (your email)
- `JIRA_API_TOKEN` (generated above)
- `CONFLUENCE_URL` (often the same as JIRA_URL with /wiki appended)
- `CONFLUENCE_USERNAME`
- `CONFLUENCE_API_TOKEN` (same token works for both)

## 3. Optional: Slack and Notion

If your team uses Slack for status updates, also set `SLACK_BOT_TOKEN` (instructions: https://api.slack.com/authentication/token-types).

If your team uses Notion, set `NOTION_API_KEY` (instructions: https://developers.notion.com/docs/create-a-notion-integration).

## 4. Repository access

Clone `cursor-course-templates`.

## 5. Smoke test

Run `/setup-persona`, pick `pm`. Confirm the manifest lists PM files. Test the Atlassian MCP by asking the agent to list your Jira projects — if credentials work, you should see a list.

## 6. PRD template

The instructor will provide a PRD template at the start of class. You can also use `personas/pm/templates/prd-template.md` if present (created during the course as students iterate).
```

### D.5 `personas/pm/.env.example`

```
# PM Persona — Environment Variables

# Required for Atlassian MCP (Jira + Confluence)
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=you@example.com
JIRA_API_TOKEN=
CONFLUENCE_URL=https://yourcompany.atlassian.net/wiki
CONFLUENCE_USERNAME=you@example.com
CONFLUENCE_API_TOKEN=

# Required for GitHub Issues MCP (engineers' work tracking)
GITHUB_PAT=

# Optional: Slack
SLACK_BOT_TOKEN=

# Optional: Notion
NOTION_API_KEY=
```

### D.6 PM subagents

**File:** `personas/pm/agents/dev-perspective.md`

```markdown
---
name: dev-perspective
description: Technical feasibility critique on a PRD or user story. Use during pm-validate to surface implementation risks, hidden complexity, and dependency issues before tickets are created.
model: inherit
readonly: true
---

You are a senior engineer reviewing a PRD from a feasibility perspective.

When invoked with a PRD or user story:

1. Read the document carefully.
2. For each user story or feature, ask:
   - Is the technical approach implied here actually feasible?
   - What systems does this touch that aren't named in the story?
   - Are there race conditions, scaling issues, or data consistency concerns?
   - What's the rough engineering cost (small/medium/large/unknown)?
   - What pre-existing dependencies block this?
3. For each acceptance criterion:
   - Can it be tested by automation?
   - Is "given/when/then" specific enough to write a test against?
4. Report:
   - **Feasible as written** — list IDs of stories that pass
   - **Feasible with changes** — story ID, the issue, the suggested rewrite
   - **Hidden complexity** — story ID, the implicit dependencies the PM didn't name
   - **Cost estimate** — rough sizing per story

Do not modify the PRD. Only critique.

Your job is not to say "no." Your job is to surface what the PM may not have considered.
```

**File:** `personas/pm/agents/qa-perspective.md`

```markdown
---
name: qa-perspective
description: Edge case and testability critique on a PRD or user story. Use during pm-validate alongside dev-perspective.
model: inherit
readonly: true
---

You are a senior QA engineer reviewing a PRD for testability and edge case coverage.

When invoked:

1. Read the PRD or user story.
2. For each story, list the edge cases the PM has not yet named:
   - Empty input
   - Maximum-length input
   - Concurrent access (two users at once)
   - Network failure mid-operation
   - Authentication missing or expired
   - Permissions insufficient
   - State transitions in unexpected order
   - Internationalization (non-ASCII characters, RTL languages)
   - Accessibility (screen reader compatibility, keyboard navigation)
3. For each acceptance criterion:
   - Could you write a test for this? If not, what makes it untestable?
   - Are the success conditions observable?
4. Report:
   - **Edge cases to add** — per story, list of cases the PRD should cover
   - **Untestable criteria** — which ACs are too vague or subjective
   - **Suggested rewrites** — concrete Given/When/Then replacements

Do not modify the PRD. Only critique.
```

**File:** `personas/pm/agents/gap-detector.md`

```markdown
---
name: gap-detector
description: Finds missing NFRs, ambiguous language, and structural gaps in a PRD. Use as a final pass before sending the PRD to engineering.
model: inherit
readonly: true
---

You scan PRDs for what's missing, not what's wrong.

When invoked:

1. Read the PRD end to end.
2. Check for the presence of:
   - **Goals and non-goals** — explicit "won't do" list
   - **User personas** — who is this for, with named roles
   - **User stories** — INVEST-compliant
   - **Acceptance criteria** — Given/When/Then per story
   - **Non-functional requirements** — performance, security, privacy, accessibility, internationalization, observability
   - **Edge cases** — explicitly listed, not implied
   - **Dependencies** — internal teams, external services, data sources
   - **Rollout plan** — feature flag? gradual? all-at-once?
   - **Success metrics** — how do we know it worked?
   - **Open questions** — what we don't yet know
3. Report:
   - **Present** — sections that exist and are non-empty
   - **Missing** — sections absent entirely
   - **Weak** — sections present but underspecified, with a one-line suggestion of what to add

Do not modify the PRD. Only report gaps.
```

### D.7 PM hook scripts

**File:** `personas/pm/scripts/invest-validator.sh`

```bash
#!/usr/bin/env bash
# PM hook: validate user stories follow the INVEST + As-a/I-want/So-that format
set -euo pipefail

file_path=$(jq -r '.file_path // empty')
[[ -z "$file_path" ]] && exit 0

# Only validate markdown files in PRD or spec directories
case "$file_path" in
  *prds/*.md|*specs/*.md|*docs/prds/*.md|*docs/specs/*.md)
    # Look for "As a" lines and check they have "I want" and "so that"
    while IFS= read -r line; do
      if echo "$line" | grep -qiE '^(\*|-|\d+\.) +As an? '; then
        if ! echo "$line" | grep -qiE 'I want.*so that'; then
          echo "WARNING: Story in $file_path may not follow As-a/I-want/So-that format: $line" >&2
        fi
      fi
    done < "$file_path"
    ;;
esac

exit 0
```

**File:** `personas/pm/scripts/ac-format-check.sh`

```bash
#!/usr/bin/env bash
# PM hook: check acceptance criteria use Given/When/Then format
set -euo pipefail

file_path=$(jq -r '.file_path // empty')
[[ -z "$file_path" ]] && exit 0

case "$file_path" in
  *prds/*.md|*specs/*.md|*docs/prds/*.md|*docs/specs/*.md)
    # Look for "Acceptance Criteria" sections
    if grep -qi 'acceptance criteria' "$file_path"; then
      # Check that the file has at least one Given/When/Then triple
      if ! grep -qiE '^\s*\*?\s*Given' "$file_path" || \
         ! grep -qiE '^\s*\*?\s*When' "$file_path" || \
         ! grep -qiE '^\s*\*?\s*Then' "$file_path"; then
        echo "WARNING: $file_path has Acceptance Criteria section but no Given/When/Then triples found." >&2
      fi
    fi
    ;;
esac

exit 0
```

**File:** `personas/pm/scripts/gap-detector.sh`

```bash
#!/usr/bin/env bash
# PM hook: at session end, suggest running gap-detector on PRDs
set -euo pipefail

# Find PRDs modified this session (rough heuristic: modified in last hour)
prd_count=$(find . -path '*/prds/*.md' -o -path '*/specs/*.md' 2>/dev/null | xargs -I{} find {} -mmin -60 2>/dev/null | wc -l)

if [[ "$prd_count" -gt 0 ]]; then
  echo "Session ended with PRD changes. Consider running @gap-detector to find missing sections." >&2
fi

exit 0
```

### D.8 PM `hooks.json`

**File:** `personas/pm/hooks.json`

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      { "command": ".cursor/scripts/invest-validator.sh" },
      { "command": ".cursor/scripts/ac-format-check.sh" }
    ],
    "stop": [
      { "command": ".cursor/scripts/gap-detector.sh" }
    ]
  }
}
```

### D.9 PM `mcp.json`

**File:** `personas/pm/mcp.json`

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_USERNAME": "${JIRA_USERNAME}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
        "CONFLUENCE_URL": "${CONFLUENCE_URL}",
        "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    }
  }
}
```

### D.10 PM rule

**File:** `personas/pm/rules/000-pm-workflow.mdc`

```markdown
---
description: PM persona workflow rules. Always applied when the PM persona is active.
alwaysApply: true
---

# PM Workflow Rules

## Every user story is INVEST-compliant

- **I**ndependent — no chained dependencies in a single story
- **N**egotiable — implementation details left open
- **V**aluable — clear user benefit
- **E**stimable — engineering can size it
- **S**mall — fits in one sprint
- **T**estable — has Given/When/Then acceptance criteria

If a story violates INVEST, propose a rewrite or split before continuing.

## Every PRD has a non-goals section

What we are explicitly not doing. Equally important as what we are doing.

## Every PRD has a non-functional requirements section

Performance budgets, security constraints, accessibility level, internationalization, observability hooks.

## Three Amigos before tickets

Run `pm-validate` (which delegates to `dev-perspective` and `qa-perspective` subagents) before running `pm-decompose`. The PRD must survive both critiques first.

## Tickets are written from the user's perspective

"As a [role], I want [outcome], so that [reason]." Not "Implement endpoint X." The implementer translates the story into technical work; the PM names the user value.

## Subagent delegation

- PRD draft complete → `pm-validate` (delegates to `dev-perspective`, `qa-perspective`)
- About to send PRD to engineering → `gap-detector`
- Tickets ready → `pm-decompose`
```

### D.11 PM commands

**File:** `personas/pm/commands/pm-validate.md`

```markdown
# /pm-validate

**Purpose:** Run the Three Amigos critique on a PRD by delegating to `dev-perspective` and `qa-perspective` subagents in parallel, then surfacing both reports.

**Prerequisites:**
- A PRD exists at `prds/{name}.md` or `docs/prds/{name}.md`
- The active persona is `pm`

**What this command does:**

1. Identify the PRD file to validate (ask if multiple exist).
2. Invoke `dev-perspective` subagent on the PRD.
3. Invoke `qa-perspective` subagent on the PRD in parallel.
4. Wait for both reports.
5. Synthesize a combined report:
   - **Feasibility blockers** (from dev-perspective Critical findings)
   - **Edge cases to add** (from qa-perspective)
   - **Untestable criteria** (from qa-perspective)
   - **Cost estimates** (from dev-perspective)
   - **Suggested rewrites** (from both)
6. Save the combined report to `prds/{name}-validation.md`.
7. Display the summary inline.

**Example invocation:**

```
/pm-validate
```

**Output:**

A validation report at `prds/{name}-validation.md`. The PM reviews the report and updates the PRD before running `pm-decompose`.

**Stop conditions:**

- If dev-perspective reports any feasibility blockers, do not run `pm-decompose` until they are resolved.
- If qa-perspective reports more than three untestable criteria, recommend rewriting before decomposing.
```

**File:** `personas/pm/commands/pm-decompose.md`

```markdown
# /pm-decompose

**Purpose:** Break a validated PRD into Jira tickets (or GitHub issues) with dependencies and acceptance criteria, then create them via the Atlassian MCP.

**Prerequisites:**
- A validated PRD at `prds/{name}.md` (validation passed in `pm-validate`)
- Atlassian MCP configured with valid credentials
- The active persona is `pm`

**What this command does:**

1. Read the PRD.
2. For each user story:
   - Extract title, description, acceptance criteria
   - Identify the parent epic (or create one if not yet existing)
   - Identify dependencies on other stories
3. Show the user a preview of all tickets that will be created (do not create yet).
4. After user approval, use the Atlassian MCP to:
   - Create the parent epic if needed
   - Create each story as a child of the epic
   - Set dependency links (`blocks`/`is blocked by`)
   - Set acceptance criteria in the description field
5. Output a markdown summary at `prds/{name}-tickets.md` listing every created ticket with its Jira key.

**Example invocation:**

```
/pm-decompose
```

**Constraints:**

- Default to creating tickets in the project named in `JIRA_DEFAULT_PROJECT_KEY` env var, or ask the user.
- Never create tickets without explicit user confirmation of the preview.
- If a story has no acceptance criteria, refuse to create the ticket and prompt the user to add criteria first.

**Output:**

- New tickets in Jira
- A markdown summary at `prds/{name}-tickets.md`
```

**File:** `personas/pm/commands/pm-report.md`

```markdown
# /pm-report

**Purpose:** Generate a status update from Jira and Confluence using the Atlassian MCP. Optionally post to Slack.

**Prerequisites:**
- Atlassian MCP configured
- An epic key or filter to query
- The active persona is `pm`

**What this command does:**

1. Ask for the scope: an epic key, a Jira filter, a sprint, or a date range.
2. Use the Atlassian MCP to fetch:
   - All tickets matching the scope
   - Their status, assignee, last update
   - Recent comments on each
3. Summarize:
   - **In progress:** tickets with status "In Progress" or "In Review"
   - **Blocked:** tickets with the blocked label or recent blocking comments
   - **Done since last report:** tickets moved to Done since a date the user provides (default: 7 days)
   - **At risk:** tickets that haven't moved status in N days
4. Write the report to `reports/{date}-status.md`.
5. Ask if the user wants to:
   - Copy the report to Confluence (uses Atlassian MCP write)
   - Post a summary to Slack (uses Slack MCP)

**Example invocation:**

```
/pm-report
```

**Output:**

- A markdown report at `reports/{date}-status.md`
- Optionally: a Confluence page or Slack message
```

### D.12 Phase D acceptance test

**[Verify]**

1. Run `/setup-persona` and pick `pm`. Confirm files installed and previous persona files removed cleanly.
2. Verify `personas/pm/mcp.json` parses and references all four MCPs (Atlassian, GitHub, Slack, Notion).
3. Verify all PM hook scripts are executable and parse without errors.
4. Switch back and forth: engineer → designer → pm → engineer. Confirm clean transitions each time.

---

## Phase E — Make Universal Commands Persona-Aware

**Goal:** Update six existing universal commands to read `## Active Persona` from the context file and adapt their behavior accordingly. The other four (`setup-stack`, `detect-stack`, `dockerize`, `research`, `research-export`) stay as-is — they are either engineer-only or naturally universal.

The pattern is: at the top of each command, add a short section that reads the active persona and branches the prompt accordingly. The bulk of each command stays unchanged.

### E.1 Update `architect`

**File:** `.cursor/commands/architect.md` and `.claude/commands/architect.md`

Add this block at the top, just under the existing "Purpose" line:

```markdown
## Persona-aware behavior

Read `## Active Persona` from `.cursor/context.md` or `CLAUDE.md`.

- **engineer:** (existing behavior) Design API surface, create walking skeleton, generate implementation plan.
- **designer:** Design a component structure. Identify which existing components to reuse, which design tokens apply, which Figma frames are the source. Output: a design spec at `docs/design-spec-{feature}.md`.
- **pm:** Draft a PRD. Identify users, user stories (INVEST), acceptance criteria (Given/When/Then), non-goals, NFRs. Output: a PRD at `prds/{name}.md`.
- **No persona set:** Run the engineer behavior with a warning: "No persona is active. Defaulting to engineer behavior. Run /setup-persona to customize."
```

The rest of the command stays unchanged.

### E.2 Update `start-session`

**File:** `.cursor/commands/start-session.md` and `.claude/commands/start-session.md`

Add at the top of the command body:

```markdown
## Persona-aware loading

Read `## Active Persona`. Display:

- **engineer:** "Persona: engineer. Stack: {active-stack}. Phase: {active-phase}."
- **designer:** "Persona: designer. Active Figma context: {path or 'none'}."
- **pm:** "Persona: pm. Active PRDs: {list of PRDs in prds/ directory}."
- **No persona:** Warn and default to engineer.

Then proceed with the existing session-start flow.
```

### E.3 Update `start-project`

**File:** `.cursor/commands/start-project.md` and `.claude/commands/start-project.md`

Add at the top:

```markdown
## Persona-aware behavior

- **engineer:** (existing behavior) Domain modeling — propose entities, tables, REST endpoints.
- **designer:** Design system audit — propose component categories, token systems, layout primitives needed for the domain.
- **pm:** Opportunity discovery — propose user personas, jobs to be done, success metrics, MVP scope.
- **No persona:** Default to engineer with a warning.
```

### E.4 Update `code-review`

**File:** `.cursor/commands/code-review.md` and `.claude/commands/code-review.md`

Add at the top:

```markdown
## Persona-aware audit

- **engineer:** (existing behavior) Full audit — security, style, testing, architecture.
- **designer:** Visual audit — token compliance, no inline styles, responsive breakpoints, accessibility (alt text, ARIA labels, contrast). Delegates to `token-validator` and `responsive-checker` subagents if available.
- **pm:** PRD audit — INVEST compliance, AC format, NFR coverage, edge cases. Delegates to `gap-detector` subagent if available.
- **No persona:** Default to engineer.
```

### E.5 Update `next-session`

**File:** `.cursor/commands/next-session.md` and `.claude/commands/next-session.md`

Add at the top:

```markdown
## Persona-aware wrap-up

- **engineer:** (existing behavior) Analyze changed files, check test status, update Active Phase, generate transition document.
- **designer:** Analyze visual changes, check responsive breakpoints (run `responsive-checker` if available), generate handoff summary.
- **pm:** Analyze PRD changes, check INVEST compliance, run `gap-detector`, generate stakeholder update.
```

### E.6 Update `read`

**File:** `.cursor/commands/read.md` and `.claude/commands/read.md`

Add at the top:

```markdown
## Persona-aware context load

Display the active persona at the top of the output, then load:

- **engineer:** Stack, phase, next step (existing behavior).
- **designer:** Active Figma context, last component composed, breakpoints status.
- **pm:** Active PRDs, validation status, ticket creation status.
```

### E.7 Phase E acceptance test

**[Verify]**

1. With engineer persona active, run `architect "Build a notification preferences feature"`. Confirm output is API-design-flavored (existing behavior).
2. Switch to designer. Run `architect "Build a notification preferences feature"`. Confirm output is component-structure-flavored, references existing components and tokens.
3. Switch to pm. Run `architect "Build a notification preferences feature"`. Confirm output is PRD-flavored with INVEST stories and NFRs.
4. Run `read` for each persona and confirm the displayed status differs.

---

## Phase F — Documentation and Student-Facing Assets

**Goal:** Update the documentation so students and instructors discover the persona system. Without this phase, the implementation is invisible.

### F.1 Update `README.md`

Add a new section at the top of the README, just under the title and before "Getting Started":

```markdown
## Three Personas, One Workflow

This template gives developers, product managers, and designers a single, customizable workflow for working with an AI code assistant of their choice (Cursor or Claude Code).

Each participant picks their persona at the start, and the assistant loads a role-specific set of commands, subagents, hooks, and MCP servers tailored to how they actually work — engineers ship code, product managers ship specs, designers ship prototypes. The same phase-based workflow runs underneath, so artifacts hand off cleanly across roles.

To activate a persona, run:

- Cursor: `@setup-persona`
- Claude Code: `/setup-persona`

After picking a persona, engineers will be prompted to run `setup-stack` next. Designers and PMs are ready to go.

See the per-persona docs:

- [Engineer](personas/engineer/README.md)
- [Designer](personas/designer/README.md)
- [PM](personas/pm/README.md)
```

### F.2 Update `QUICKSTART.md`

Add a new "Workflow 0" at the top, before the existing three workflows:

```markdown
### Workflow 0: Pick a Persona

**Best for:** Every project. This is the entry point.

**Steps:**

1. **Get the Template**

   ```
   git clone https://github.com/axel-sirota/cursor-course-templates my-project
   cd my-project
   ```

2. **Open in Your AI Tool**

   - Cursor: `cursor .`
   - Claude Code: `claude`

3. **Pick Your Persona**

   - Cursor: `@setup-persona`
   - Claude Code: `/setup-persona`

   Choose:
   - **engineer** — software development
   - **designer** — design-system-aware prototyping
   - **pm** — product management

4. **Persona-specific next step:**

   - Engineers: continue to Workflow 1, 2, or 3 (stack selection)
   - Designers and PMs: copy the persona's `.env.example` to `.env` and fill in credentials. Skip to "Command Reference" below.
```

Push the existing three workflows down and rename them: "Workflow 1: Engineer with Known Stack," "Workflow 2: Engineer with Custom Stack," "Workflow 3: Adapt Existing Codebase (Engineer)."

### F.3 Update `METHODOLOGY.md`

Add a new section after "Core Principles," before "Command Reference":

```markdown
## Personas

A persona is a bundle of role-specific configuration. Picking a persona at session start activates a curated set of:

- Commands (the persona-specific slash commands)
- Subagents (specialized AI workers with isolated context)
- Hooks (lifecycle automations)
- MCP servers (external tool integrations)
- Rules (always-applied constraints)

The repository ships three personas:

- **engineer** — Closest to the existing Adaptive SDLC. After `setup-persona engineer`, run `setup-stack` to pick a tech stack pack.
- **designer** — Visual changes against an existing codebase, sourced from Figma via MCP. No tech stack selection needed.
- **pm** — PRDs, validation, and ticket decomposition. Output is markdown plus Jira/Confluence operations via Atlassian MCP.

Personas are managed by `setup-persona` and tracked via `.cursor/.persona-manifest.json`. Switching personas is clean and idempotent — the previous persona's files are removed before the new persona's files are installed.

Universal commands (`architect`, `start-session`, `code-review`, etc.) are persona-aware: they read the active persona from the context file and adapt their behavior. Persona-specific commands (`engineer-implement`, `designer-extract`, `pm-validate`, etc.) are added when a persona activates and removed when it deactivates.
```

### F.4 Update `student_runbook.md`

The existing runbook (likely engineer-focused) gets three sections added — one per persona. The runbook's day-of structure stays intact; the new sections describe the persona-specific flow at each timepoint.

**[Claude Code prompt]**

```
Read student_runbook.md. For each major timepoint in the runbook (e.g., morning kickoff, mid-morning lab, afternoon hooks/MCP block, capstone), add a per-persona breakdown explaining what each persona does at that timepoint.

Pattern:

### Morning Kickoff (existing section)

(existing content)

#### Engineer flow
- Run /setup-persona, pick engineer
- Run /setup-stack, pick blank or python-fastapi
- ...

#### Designer flow
- Run /setup-persona, pick designer
- Verify Figma desktop is running with Dev Mode MCP
- ...

#### PM flow
- Run /setup-persona, pick pm
- Verify Atlassian credentials work by listing your projects
- ...
```

### F.5 Phase F acceptance test

**[Verify]**

1. Read README.md as a new student would. Confirm the persona section is visible above the fold and explains the choice.
2. Read QUICKSTART.md. Confirm Workflow 0 is the first thing a student sees.
3. Read METHODOLOGY.md. Confirm the Personas section exists and is consistent with the implementation.
4. Read student_runbook.md. Confirm every major timepoint has per-persona instructions.

---

## Acceptance Tests

These are the end-to-end tests that confirm the entire implementation works. Run them after Phase F.

### Test 1: Engineer end-to-end

```
1. Fresh clone of the repo.
2. /setup-persona → pick engineer
3. /setup-stack → pick python-fastapi
4. /architect "Build a task management API with create, list, mark-complete endpoints"
5. /engineer-tasks (consumes the plan)
6. /engineer-implement (executes tasks via subagents)
7. /code-review
8. /next-session
```

Expected: Working FastAPI app with passing tests, code review report, session transition document.

### Test 2: Designer end-to-end

```
1. Fresh clone of the repo.
2. Set FIGMA_ACCESS_TOKEN in .env.
3. /setup-persona → pick designer
4. /designer-extract <figma-url>
5. /designer-compose docs/figma-context-{frame}.md
6. /designer-iterate (interactive)
7. /designer-handoff
```

Expected: Working prototype matching Figma source, PR_DESCRIPTION.md with breakpoint screenshots, no logic modifications detected by code-review.

### Test 3: PM end-to-end

```
1. Fresh clone of the repo.
2. Set Atlassian credentials in .env.
3. /setup-persona → pick pm
4. /architect "Notification preferences feature"
5. /pm-validate (delegates to dev-perspective and qa-perspective)
6. (PM reviews and updates PRD)
7. /pm-decompose (creates tickets in Jira)
8. /pm-report (generates status update)
```

Expected: Validated PRD, tickets in Jira matching the PRD's stories, status report.

### Test 4: Cross-persona capstone

This is the integration test for the May/June course delivery.

```
1. Three students (or one student playing all three roles in sequence) clone the repo.
2. PM: /setup-persona pm → /architect "User notification preferences" → /pm-validate → /pm-decompose
3. Designer: /setup-persona designer → /designer-extract <figma-url> → /designer-compose → /designer-iterate → /designer-handoff
4. Engineer: /setup-persona engineer → /setup-stack python-fastapi → /architect (reads PRD from prds/) → /engineer-tasks → /engineer-implement → /code-review
```

Expected: PRD in prds/, prototype in components/, working backend, all three artifacts coherent.

### Test 5: Persona switching

```
1. /setup-persona engineer → confirm engineer files installed
2. /setup-persona designer → confirm engineer files removed and designer files installed
3. /setup-persona pm → confirm designer files removed and pm files installed
4. /setup-persona engineer → confirm pm files removed and engineer files re-installed
```

Expected: Clean transitions, no orphaned files, manifest accurate at each step.

### Test 6: Backwards compatibility

```
1. Fresh clone.
2. Skip /setup-persona entirely.
3. /setup-stack python-fastapi
4. /architect "Simple API"
5. /start-session
```

Expected: The existing engineer flow works unchanged. No persona is required for the legacy workflow.

---

## Rollback Plan

If a phase fails or the implementation needs to be paused, here is how to roll back to a working state.

### Rollback within a phase

Each phase is structured so the repo is in a working state at every checkpoint. If a sub-step fails:

1. `git status` to see what's uncommitted.
2. `git checkout -- <file>` for files that should revert.
3. `rm -rf personas/{role}/` if a partially-built persona is broken.
4. Continue from the last passing acceptance test.

### Rollback an entire phase

Each phase should be a single git branch:

```
git checkout main
git branch persona-phase-A
# ... do Phase A work ...
git commit -am "Phase A: engineer persona"
git checkout main
git merge persona-phase-A
```

If Phase B is broken, revert the merge:

```
git revert -m 1 <merge-commit-sha>
```

### Full implementation rollback

The entire implementation can be rolled back without breaking the existing repo:

```
rm -rf personas/
rm -f .cursor/commands/setup-persona.md
rm -f .claude/commands/setup-persona.md
git checkout -- CLAUDE.md README.md QUICKSTART.md METHODOLOGY.md student_runbook.md
git checkout -- .cursor/commands/architect.md .claude/commands/architect.md
git checkout -- .cursor/commands/start-session.md .claude/commands/start-session.md
git checkout -- .cursor/commands/start-project.md .claude/commands/start-project.md
git checkout -- .cursor/commands/code-review.md .claude/commands/code-review.md
git checkout -- .cursor/commands/next-session.md .claude/commands/next-session.md
git checkout -- .cursor/commands/read.md .claude/commands/read.md
```

The repo is now back to pre-implementation state.

---

## Reference: All MCPs, Hooks, Subagents, Commands

A flat reference of everything added by this implementation, for quick lookup.

### Subagents (10 total)

| Persona | Name | Read-only | Purpose |
|---------|------|-----------|---------|
| engineer | code-reviewer | yes | Reviews diffs against stack rules |
| engineer | security-auditor | yes | Scans for secrets, injection, unsafe patterns |
| engineer | test-runner | no | Runs test suite and reports failures |
| engineer | verifier | yes | Validates "done" claims against acceptance criteria |
| designer | figma-extractor | yes | Pulls tokens, components, layout from Figma MCP |
| designer | token-validator | yes | Scans for hardcoded color/spacing/font values |
| designer | responsive-checker | no | Takes screenshots at three breakpoints, reports issues |
| pm | dev-perspective | yes | Technical feasibility critique on PRD |
| pm | qa-perspective | yes | Edge case and testability critique on PRD |
| pm | gap-detector | yes | Finds missing NFRs, ambiguous language, structural gaps |

### Persona-specific commands (9 total)

| Persona | Command | Purpose |
|---------|---------|---------|
| engineer | engineer-tasks | Decompose plan into parallel-safe tasks |
| engineer | engineer-implement | TDD execution loop with subagent delegation |
| designer | designer-extract | Pull Figma context via MCP |
| designer | designer-compose | Assemble prototype from existing components |
| designer | designer-iterate | Visual Editor / Design Mode loop |
| designer | designer-handoff | Generate PR description with breakpoint screenshots |
| pm | pm-validate | Three Amigos critique via subagents |
| pm | pm-decompose | Create Jira tickets from validated PRD |
| pm | pm-report | Generate status update from Jira and Confluence |

### Universal commands made persona-aware (6)

`architect`, `start-session`, `start-project`, `code-review`, `next-session`, `read`

### Universal commands unchanged (5)

`setup-stack`, `detect-stack`, `dockerize`, `research`, `research-export`

### New universal command (1)

`setup-persona`

### Hook lifecycle events used

| Event | Engineer | Designer | PM |
|-------|----------|----------|-----|
| `afterFileEdit` | lint, type-check | token-validator, no-inline-styles | invest-validator, ac-format-check |
| `beforeShellExecution` | block-destructive | — | — |
| `stop` | test-runner | screenshot-compare | gap-detector |

### MCP servers per persona

| Persona | Server | Auth |
|---------|--------|------|
| engineer | github | GITHUB_PAT |
| engineer | postgres | DATABASE_URL |
| engineer | sentry | SENTRY_AUTH_TOKEN |
| engineer | playwright | none |
| engineer | context7 | none (free tier) |
| designer | figma | FIGMA_ACCESS_TOKEN |
| designer | playwright | none |
| designer | context7 | none |
| pm | atlassian | JIRA_*, CONFLUENCE_* |
| pm | github | GITHUB_PAT |
| pm | slack | SLACK_BOT_TOKEN |
| pm | notion | NOTION_API_KEY |

### File counts

- 3 personas × ~13 files each = 39 persona pack files
- 1 new universal command × 2 (Cursor + Claude Code) = 2 files
- 6 universal commands updated × 2 = 12 files updated
- 5 documentation files updated
- ~58 net new or modified files

---

## Closing notes

This implementation preserves every line of the existing methodology while layering a customizable persona experience on top. The engineer flow is unchanged for anyone who skips `setup-persona`. The new flow gives designers and PMs a first-class experience where their tools, vocabulary, and artifacts match how they actually work.

The cross-persona capstone is the proof point: same workflow vocabulary, three role-native paths to solving one problem, artifacts that hand off cleanly. That is the headline.

When in doubt, refer back to the mental model section. The whole implementation hangs on three ideas:

1. Persona is a layer, not a replacement.
2. The manifest makes switching safe.
3. Universal commands stay universal but become persona-aware.

Build it phase by phase, run the acceptance tests, and the May/June delivery has a working system.
