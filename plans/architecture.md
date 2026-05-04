# Platform Architecture — Multi-Client Multi-Persona AI Course

**Status:** Research complete. Ready to build.
**Date:** 2026-05-04
**Context:** Cursor/Claude Code course platform for enterprise clients (Intuit, Salesforce, others). Private repo.

---

## 1. Core Principle

**The base repo is the product. Client configs are overlays. Clients never see each other.**

```
cursor-course-templates/     ← this repo (private)
  personas/                  ← 4 generic persona packs
  stacks/                    ← 6 generic stack packs (adding python-datascience)
  .cursor/commands/          ← universal + setup commands
  .claude/commands/          ← identical mirror
  client-config/             ← GITIGNORED — populated by instructor before class

separate private repos (instructor-managed, one per client):
  axel-sirota/intuit-course-config
  axel-sirota/salesforce-course-config
```

---

## 2. Personas

Four first-class personas. Each is a self-contained pack in `personas/{name}/`.

| Persona | Deliverable | Stack needed? |
|---|---|---|
| `engineer` | Working code behind tests | Yes — run `setup-stack` after |
| `designer` | Visual prototype matching Figma source | No |
| `pm` | PRD with INVEST stories + AC | No |
| `data-scientist` | Reproducible experiment + model card | Yes — `setup-stack python-datascience` |

---

## 3. Persona Pack Structure

Every persona has identical directory layout:

```
personas/{name}/
├── persona.md          ← mental model, vocabulary, workflow phases, key rules
├── README.md           ← what this pack adds (commands, agents, hooks, MCPs)
├── SETUP.md            ← pre-class student checklist
├── .env.example        ← env var slots with _note comments for client overrides
├── commands/           ← persona-specific slash commands (markdown)
├── agents/             ← subagent definitions (YAML frontmatter + prompt)
├── scripts/            ← hook scripts (bash)
├── hooks.json          ← hook wiring (.cursor/scripts/ paths — rewritten for .claude/ at install)
├── mcp.json            ← generic open-source MCP defaults + _note override hints
└── rules/
    └── 000-{name}-workflow.mdc
```

---

## 4. Commands Per Persona

### Universal commands (exist today, get persona-aware branches)

These 6 commands read `## Active Persona` from context and branch behavior:

| Command | Engineer | Designer | PM | Data Scientist |
|---|---|---|---|---|
| `/architect` | Design API surface | Design component hierarchy | Draft PRD structure | Design experiment plan |
| `/start-session` | Load stack + rules | Load design tokens context | Load active PRD | Load dataset + experiment log |
| `/start-project` | Propose entities + API | Propose component library | Propose user stories | Propose data pipeline |
| `/code-review` | Security + style + tests | Token discipline + logic untouched | INVEST + AC format | Reproducibility + model risks |
| `/next-session` | Phase advance + test status | Screenshot + PR status | Gap check + ticket status | Experiment log update |
| `/read` | Stack + phase + test status | Active Figma + token state | Active PRD + story count | Active experiment + dataset |

These 4 stay naturally universal (no persona branch needed):

- `/setup-stack` — engineer + data-scientist only; others skip
- `/detect-stack` — brownfield tool, always engineer-flavored
- `/dockerize` — engineer tool
- `/research` — tool-agnostic

### Persona-specific commands (installed by `set-persona`)

**Engineer** — ships code:
- `/engineer-tasks` — decompose architect plan into parallel-safe tasks (Given/When/Then per task)
- `/engineer-implement` — TDD execution loop: red→green→refactor, subagent delegation, stop conditions

**Designer** — ships prototypes:
- `/designer-extract` — pull tokens/components/layout from Figma via MCP → `docs/figma-context-{frame}.md`
- `/designer-compose` — assemble prototype from existing components using extracted context
- `/designer-iterate` — visual refinement loop (click element → state change → hot reload)
- `/designer-handoff` — generate PR description: what changed, what preserved, breakpoint screenshots

**PM** — ships specs:
- `/pm-validate` — Three Amigos critique: `dev-perspective` + `qa-perspective` + `gap-detector` subagents
- `/pm-decompose` — break epic into dependency-ordered tickets for issue tracker
- `/pm-report` — pull status from Jira/GitHub Issues, generate stakeholder update

**Data Scientist** — ships experiments:
- `/ds-explore` — EDA loop: profile data, visualize distributions, document hypotheses → `docs/eda-{dataset}.md`
- `/ds-experiment` — run experiment with tracked params/metrics/seed → `docs/experiments/{date}-{name}.md`
- `/ds-validate` — validate model on held-out data, check for bias/drift → `docs/validation-{model}.md`
- `/ds-handoff` — generate model card: what it does, limitations, deployment requirements → `docs/model-card-{name}.md`

---

## 5. Subagents Per Persona

Every agent: YAML frontmatter (`name`, `description`, `model: inherit`, `readonly: true/false`) + prompt.
Agents are installed to `.cursor/agents/` AND `.claude/agents/` by `set-persona`.

**Engineer agents:**
- `code-reviewer` — reviews diff vs active stack rules (readonly)
- `security-auditor` — scans for secret leaks, injection, unsafe patterns (readonly)
- `test-runner` — executes test suite, summarizes failures with root cause (NOT readonly — executes)
- `verifier` — validates "done" claims against acceptance criteria, tries edge cases (readonly)

**Designer agents:**
- `figma-extractor` — fetches tokens/components/layout from Figma MCP → context file (readonly)
- `token-validator` — scans CSS/SCSS/JSX for hardcoded hex/px values, suggests token replacements (readonly)
- `responsive-checker` — Playwright screenshots at 375/768/1440px, reports layout issues (NOT readonly — takes screenshots)

**PM agents:**
- `dev-perspective` — technical feasibility critique: hidden complexity, dependency risks, cost estimate (readonly)
- `qa-perspective` — edge case finder: empty input, concurrency, auth expiry, i18n, a11y (readonly)
- `gap-detector` — structural PRD completeness check: NFRs, success metrics, rollout plan, open questions (readonly)

**Data Scientist agents:**
- `data-profiler` — statistical profile of dataset: dtypes, nulls, distributions, correlations, outliers (readonly)
- `experiment-tracker` — logs params/metrics/artifacts to `docs/experiments/log.md` (NOT readonly — writes)
- `reproducibility-checker` — verifies seed set, requirements pinned, notebook runs top-to-bottom, no absolute paths (readonly)

---

## 6. Hooks Per Persona

Hook scripts live in `personas/{name}/scripts/`. Installed to `.cursor/scripts/` AND `.claude/scripts/`.
`hooks.json` references `.cursor/scripts/` — `set-persona` rewrites to `.claude/scripts/` for Claude side.

All scripts read `file_path` from stdin JSON and exit 0 if not their file type. Hooks are non-blocking (warnings to stderr, not hard failures) except `block-destructive.sh`.

| Persona | Event | Script | Checks |
|---|---|---|---|
| engineer | `afterFileEdit` | `lint.sh` | ruff (py), biome (ts/js), gofmt (go) |
| engineer | `afterFileEdit` | `type-check.sh` | mypy (py), tsc --noEmit (ts), go vet |
| engineer | `beforeShellExecution` | `block-destructive.sh` | rm -rf, git push --force, DROP TABLE, etc. |
| engineer | `stop` | `test-runner.sh` | pytest / npm test / go test |
| designer | `afterFileEdit` | `token-validator.sh` | hardcoded hex colors, pixel spacing |
| designer | `afterFileEdit` | `no-inline-styles.sh` | style={{}} in JSX/TSX |
| designer | `stop` | `screenshot-compare.sh` | prompt to invoke responsive-checker |
| pm | `afterFileEdit` | `invest-validator.sh` | As-a/I-want/So-that in prds/*.md |
| pm | `afterFileEdit` | `ac-format-check.sh` | Given/When/Then per story |
| pm | `stop` | `gap-detector.sh` | invoke gap-detector agent |
| data-scientist | `afterFileEdit` | `seed-check.sh` | random.seed / np.random.seed / torch.manual_seed |
| data-scientist | `afterFileEdit` | `notebook-lint.sh` | notebook execution count = total cells (jq parse) |
| data-scientist | `stop` | `log-experiment.sh` | invoke experiment-tracker agent |

---

## 7. MCP Servers Per Persona

Generic defaults only. Client overlays replace with internal endpoints via `client-config/personas/{role}/mcp.json`.
Each entry has a `_note` field documenting the override point for instructors.

**Engineer:**
- `github` — `@modelcontextprotocol/server-github` — needs `GITHUB_PAT`
- `postgres` — `@modelcontextprotocol/server-postgres` — needs `DATABASE_URL` (optional)
- `sentry` — `@modelcontextprotocol/server-sentry` — needs `SENTRY_AUTH_TOKEN` (optional)
- `playwright` — `@playwright/mcp@latest` — no auth
- `context7` — `@upstash/context7-mcp@latest` — no auth

**Designer:**
- `figma` — `figma-developer-mcp` — needs `FIGMA_ACCESS_TOKEN` + Figma desktop running
- `playwright` — `@playwright/mcp@latest` — no auth
- `context7` — `@upstash/context7-mcp@latest` — no auth

**PM:**
- `atlassian` — `@modelcontextprotocol/server-atlassian` — needs `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
- `github-issues` — `@modelcontextprotocol/server-github` — needs `GITHUB_PAT`
- `slack` — `@modelcontextprotocol/server-slack` — needs `SLACK_BOT_TOKEN` (optional)
- `notion` — `@modelcontextprotocol/server-notion` — needs `NOTION_API_KEY` (optional)

**Data Scientist:**
- `filesystem` — ships with Claude Code/Cursor — no auth, scoped to `data/` directory
- `context7` — `@upstash/context7-mcp@latest` — no auth
- _(client overlay adds: Snowflake, MLflow, BigQuery, internal data catalog)_

---

## 8. Stack Packs

Existing stacks unchanged. Adding one:

```
stacks/python-datascience/
├── context.md          ← Language: Python 3.11+, Jupyter, sklearn/pandas/pytorch
├── rules/
│   ├── 000-ds-workflow.mdc       ← seed discipline, no raw data, model card required
│   └── 100-notebook-standards.mdc ← cell org, markdown headers, no global state
├── templates/
│   └── ds-starter.md             ← notebook starter template
└── vibe/
    └── vibe_ds_workflow.md       ← EDA → Experiment → Validate → Handoff guide
```

---

## 9. The `set-persona` Command

Replaces spec's `setup-persona`. Client-overlay-aware. Single student command.

**Algorithm:**

```
1. Read personas/ directory → build available persona list dynamically
2. Check .cursor/.persona-manifest.json → if exists, list previous persona files, ask confirm removal
3. Show persona menu with one-para summary from each personas/{role}/README.md
4. Remove previous persona files per manifest
5. Copy personas/{role}/ to .cursor/ and .claude/ (all subdirs)
   - hooks.json → .cursor/hooks.json verbatim
   - hooks.json → .claude/hooks.json with .cursor/scripts/ → .claude/scripts/ rewrite
   - scripts/*.sh → chmod +x on both sides
6. IF client-config/personas/{role}/ exists:
   - REPLACE mcp.json entirely with client version
   - APPEND client rules/*.mdc to .cursor/rules/ and .claude/rules/ (don't replace base rules)
   - REPLACE .env.example with client version
   - Record client-sourced files separately in manifest under "client_files" key
7. IF client-config/client.md exists:
   - Write ## Active Client to context files
8. Update .cursor/context.md and CLAUDE.md:
   - ## Active Persona: {role}
   - ## Active Client: {client} (if present)
9. Write manifest to .cursor/.persona-manifest.json and .claude/.persona-manifest.json
10. Print confirmation summary:
    ✅ Persona active: {role}
    Commands: {list}
    Agents: {list}
    Hooks: {summary by event}
    MCPs: {list, flagging which need credentials}
    Client overlay: {applied/not present}
    Next step: {persona-specific instruction}
```

**Manifest format:**
```json
{
  "persona": "engineer",
  "client": "intuit",
  "installed_at": "2026-05-04T12:00:00Z",
  "base_files": ["...paths from personas/engineer/..."],
  "client_files": ["...paths from client-config/personas/engineer/..."]
}
```

---

## 10. Client Config Structure

Never in this repo. Instructor distributes as zip or private git clone before class.

```
client-config/                        ← dropped in repo root, gitignored
├── client.md                         ← ## Client: Intuit \n ## Policies: ...
├── mcp-overrides.json                ← top-level overrides (rarely needed)
├── env.example                       ← Intuit-specific env var names/instructions
├── SETUP.md                          ← Intuit student pre-class checklist
└── personas/
    ├── engineer/
    │   └── mcp.json                  ← Intuit GitHub Enterprise + internal Postgres
    ├── designer/
    │   └── mcp.json                  ← Intuit Figma org token instructions
    ├── pm/
    │   └── mcp.json                  ← Intuit Jira URL + Confluence URL
    └── data-scientist/
        └── mcp.json                  ← Intuit Snowflake + internal MLflow
```

The instructor fills in `mcp.json` files. Axel never sees internal MCP configs.
Each `mcp.json` fully replaces the generic persona's `mcp.json` — no deep merge.
Client rules (if any) in `personas/{role}/rules/` are APPENDED to base rules, not replacing them.

---

## 11. Dual-Tool Symmetry

Every file installed by `set-persona` goes to BOTH `.cursor/` and `.claude/`.
Content is identical EXCEPT `hooks.json` which gets path-rewritten.

```
personas/{role}/hooks.json
  → .cursor/hooks.json          (verbatim copy)
  → .claude/hooks.json          (.cursor/scripts/ replaced with .claude/scripts/)
```

Command files: identical content in both `.cursor/commands/` and `.claude/commands/`.
Agent files: identical content in both `.cursor/agents/` and `.claude/agents/`.
Script files: identical content + chmod +x in both `.cursor/scripts/` and `.claude/scripts/`.
Rule files: identical content in both `.cursor/rules/` and `.claude/rules/`.

---

## 12. Build Phases

| Phase | What to build | Key files |
|---|---|---|
| **A** | `personas/engineer/` complete | commands(2) + agents(4) + scripts(4) + hooks.json + mcp.json + rules(1) |
| **B** | `personas/designer/` complete | commands(4) + agents(3) + scripts(3) + hooks.json + mcp.json + rules(1) |
| **C** | `personas/pm/` complete | commands(3) + agents(3) + scripts(3) + hooks.json + mcp.json + rules(1) |
| **D** | `personas/data-scientist/` complete | commands(4) + agents(3) + scripts(3) + hooks.json + mcp.json + rules(1) |
| **E** | `stacks/python-datascience/` | context.md + rules(2) + templates(1) + vibe(1) |
| **F** | `/set-persona` command | .cursor/commands/set-persona.md + .claude/commands/set-persona.md |
| **G** | 6 universal commands — persona-aware branches | architect, start-session, start-project, code-review, next-session, read |
| **H** | `.gitignore` entry for `client-config/` | one line |
| **I** | Sample `client-config/` structure | README explaining how instructor populates it |
| **J** | Docs update | README.md, QUICKSTART.md, METHODOLOGY.md, student_runbook.md |

---

## 13. Student Flow (Day of Class)

```
# Before class (instructor provides):
# - Repo access (clone URL)
# - client-config.zip (drop in repo root and unzip)

git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
unzip ~/client-config.zip    # or: git clone <client-config-repo> client-config

# In Claude Code or Cursor:
/set-persona                 # picks role, detects client-config automatically, installs everything
/setup-stack python-fastapi  # engineer + data-scientist only
/start-session               # begin working
```

One command to install the full role environment. Client config is invisible to the student.

---

## 14. What Axel Never Needs to Know

- Client's internal GitHub Enterprise URL
- Client's internal Jira/Confluence URLs
- Client's internal data catalog or MLflow endpoint
- Client's internal Snowflake connection details
- Any client-specific MCP config

The instructor fills these into `client-config/personas/{role}/mcp.json` before distributing to students. The `set-persona` command installs whatever is in that file. Axel ships the slot structure and documentation of what each slot expects.
