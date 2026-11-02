---
description: Execute Phase 0 (Architecture & Skeleton) for one persona, using that persona's stack
---

# Architect Phase Command

```
/architect [<role>] ["what to build" | path/to/plan.md]
```

Runs **Phase 0** for ONE persona in **three gated phases**:
1. **Design**: produce all planning docs (session files, interface contract, phase breakdown)
2. **⛔ Human Review**: student reads and approves before anything is built
3. **Scaffold**: build the walking skeleton from the approved plan

Below, `{ws}` means that persona's workspace, `workspaces/<role>` (from `persona.yaml` → `workspace`).

---

## Step 0: Acceptance Criteria (read first)

This command is NOT complete until ALL of the following exist:

| Artifact | Required | Notes |
|----------|----------|-------|
| `{ws}/plans/sessions/session-overview.md` | MANDATORY | Phase breakdown + session list |
| `{ws}/plans/sessions/session-1-phase-0.md` | MANDATORY | Skeleton session plan |
| `{ws}/plans/sessions/session-N-phase-X.md` | MANDATORY | One file per feature phase (N≥2) |
| `{ws}/plans/interface-contract.md` | MANDATORY | The contract for this Architecture Shape |
| Walking skeleton in `{ws}/` | MANDATORY | Only after the human approves the plans |

You may NOT print the final ✅ summary until you have verified all of these exist via `ls`.

---

## Step 1: Persona + Context Detection

1. Read `## Active Personas` from `.cursor/context.md`. Empty → **STOP**: "⚠️ No persona configured. Run **/set-persona** first, then come back to `/architect`."
2. Pick the role: the argument if given (must be active); else the only active persona; else ask "Which persona is this plan for? {list}".
3. Read the `## Persona: <role>` block: `Stack`, `Architecture Shape`, `Active Phase`. Stack unset → **STOP**: "Run `/setup-stack <role>` first." Never assume a shape.
4. Read `personas/<role>/persona.yaml` (workspace, in-session commands) and every rule in `.cursor/rules/<role>/`. Those rules apply to everything you write in `{ws}/`.

### Architecture Shape dispatch

Look up the persona's shape in this table and load ONLY that row's guidance. Do not show the table to the user. Listing every shape creates REST bias and noise.

| Architecture Shape | Stacks | Interface contract is... | Skeleton is... | Skeleton check |
|---|---|---|---|---|
| REST API | python-fastapi, go-gin, java-spring, node-express, node-nestjs | OpenAPI routes + data model | Entrypoint + stub handlers returning hardcoded 200 | Start server, hit every stub |
| gRPC Service | go-grpc | `.proto` services + messages | Proto + generated stubs, no-op methods | `buf lint`, build |
| Data Pipeline | python-spark, python-mlops | Job stages + schemas + Bronze/Silver/Gold layers | Stage functions returning empty DataFrames | Import + run with empty input |
| Analytics Model | python-dbt-snowflake | Sources + staging/mart model tree + grain | Models with `select 1 as placeholder` | `dbt parse` |
| Statistical Computing | r-tidyverse | Notebook sequence + `src/` function signatures | Notebook files + stub functions | `Rscript --parse` |
| Experiment Notebook | python-datascience | Dataset, EDA sequence, candidate models, metrics | `notebooks/` EDA template, `data/`, `artifacts/`, `experiments/log.md` stubs | Notebook runs top to bottom |
| PRD Workspace | pm-prd-markdown | PRD outline: problem, goals, non-goals, users, epics, NFR categories, success metrics | `prds/<name>.md` with every section headed and TODO bodies, `stories/` folder, glossary | `markdownlint` + every required heading present |
| Design System | designer-react-tokens | Token set (semantic over primitive) + component inventory (exists / to build) + screen layout | `tokens/tokens.json`, component files rendering placeholders, one story per component | Token JSON validates, Storybook / test build passes |
| Close Workbook | python-accounting | Source files + schemas, reconciliation and analysis steps, output reports, tie-out points | `src/` step functions returning empty DataFrames, `output/` folder, pytest tie-out stubs | `pytest` collects and runs |
| {custom stack} | from `stacks/<stack>/context.md` | Read the stack's Architecture Shape; ask the user if unclear | | |

---

## Step 2: Plan Source Detection

Check if the user provided a plan:
- A file path in the arguments (`/architect pm prds/raw-notes.md`)
- Plan content pasted in the message
- Common files inside `{ws}/`: `plan.md`, `requirements.md`, `PRD.md`, `design.md`
- The persona's exercise brief, if the student says they are doing an exercise: `exercises/<role>/<exercise>/README.md`

**Plan found → Plan Extraction Mode (3A–5A). No plan → Design Mode (3B–4B).**

---

## ══════════════════════════════════════
## PHASE 1: DESIGN DOCS
## ══════════════════════════════════════

> **Goal:** Produce all planning artifacts. No code or content files yet.

### Plan Extraction Mode (3A–5A)

**3A. Extract requirements.** Trust the plan, do not redesign. Extract features, contract items, data model, decisions. Ask about anything unclear before continuing.

**4A. Verify stack compatibility.** Does the plan fit the persona's stack and shape? If not, warn, offer options, wait.

**5A. Output manifest (chat + disk).**

(1) Print to chat:

```
ARCHITECT OUTPUT MANIFEST (<role>)
=========================
{ws}/plans/
├── interface-contract.md       ← [e.g. "7 REST endpoints" / "PRD with 4 epics" / "3 reconciliations + flux report"]
└── sessions/
    ├── session-overview.md
    ├── session-1-phase-0.md    ← skeleton
    ├── session-2-phase-1.md    ← [feature]
    └── session-N-phase-X.md

I will create ALL of the above before this command is complete.
```

(2) Persist to `{ws}/plans/.architect-manifest.json`:

```json
{
  "generated_at": "<ISO 8601>",
  "persona": "<role>",
  "mode": "extract | design",
  "active_stack": "<stack>",
  "architecture_shape": "<shape>",
  "planned_files": [
    {"path": "{ws}/plans/interface-contract.md", "purpose": "..."},
    {"path": "{ws}/plans/sessions/session-overview.md", "purpose": "..."},
    {"path": "{ws}/plans/sessions/session-1-phase-0.md", "purpose": "skeleton"},
    {"path": "{ws}/plans/sessions/session-2-phase-1.md", "purpose": "<feature>"}
  ],
  "interface_items": ["<every route / stage / model / PRD epic / component / reconciliation the contract lists>"]
}
```

Then create each file. Session file format:

```markdown
# Session N: Phase X — [Feature Name]

## Goal
## Requirements (from plan)
## Tasks
- [ ] ...
## In-session commands to use
[from persona.yaml → in_session_commands, the ones that fit this session]
## Acceptance Criteria
- [ ] [Verifiable: "you are done when..."]
## Verification
[Exact command or check]
```

📋 **Phase 1 checkpoint:**
```
📋 PHASE 1 COMPLETE — Design docs written (<role>)
   ✅ {ws}/plans/interface-contract.md
   ✅ {ws}/plans/sessions/session-overview.md
   ✅ {ws}/plans/sessions/session-1-phase-0.md
   ✅ {ws}/plans/sessions/session-N... ([N] total)
```

### Design Mode (3B–4B)

**3B. Design the interface contract** for the persona's shape only, using the dispatch table row. Custom stack → read `stacks/<stack>/context.md` and ask the user what the contract should contain.

**4B. Output manifest** exactly as in 5A, then create the files and print the Phase 1 checkpoint.

---

## ══════════════════════════════════════
## PHASE 1.5: SELF-AUDIT (adversarial loop)
## ══════════════════════════════════════

Runs silently unless something fails. On success print one line: `🔍 self-audit passed ({N} planned files, {M} interface items)`.

**1.5a Manifest diff.** Every `planned_files` path exists on disk; create any missing one now. Any extra file under `{ws}/plans/sessions/` not in the manifest → ask: keep / remove / add-to-manifest.

**1.5b Coverage diff.** Every `interface_items` entry is mentioned in the skeleton or a feature session. Orphans → ask: add a session / move into an existing one / remove from contract. Session items not in the contract → ask: add to contract / remove from session.

**1.5c Structured critique.** Answer in chat, one paragraph each, and fix before Phase 2:
1. Does Phase 0 stub the WHOLE contract surface?
2. Are sessions ordered by dependency?
3. Is any session bigger than 1–4 hours of work? Split it.
4. Is every acceptance criterion verifiable (a command, a check, a count)?
5. Does the contract fit the Architecture Shape (no REST contract for a Close Workbook)?

**1.5d** Print:
```
🔍 PHASE 1.5 SELF-AUDIT PASSED
   ✅ Manifest diff: {N} planned files, all present, no extras
   ✅ Coverage diff: {M} interface items, all covered by sessions
   ✅ Structured critique: skeleton complete, sessions well-scoped, ACs verifiable
```

---

## ══════════════════════════════════════
## ⛔ PHASE 2: HUMAN REVIEW GATE
## ══════════════════════════════════════

Print EXACTLY this and STOP. Write nothing else:

```
⛔ REVIEW REQUIRED — Nothing has been built yet. This is intentional.

Please review the planning docs before we build anything:

  📂 {ws}/plans/interface-contract.md
  📂 {ws}/plans/sessions/   ([N] session files)

Questions to ask yourself:
  • Does the contract match what you want to build?
  • Is anything missing, or anything you don't need?
  • Is each session a reasonable chunk of work?

To modify: edit the files directly, then tell me what changed.
When you are satisfied, say "approved", "looks good" or "proceed".
```

Wait for explicit approval ("approved", "looks good", "proceed", "yes", "lgtm", "build it" or equivalent). If changes are requested, make them, re-print the gate, wait again.

---

## ══════════════════════════════════════
## PHASE 3: SCAFFOLD (after approval only)
## ══════════════════════════════════════

Read `{ws}/plans/sessions/session-1-phase-0.md`. Build the skeleton described in the persona's dispatch row, inside `{ws}/` only. Stubs and placeholders, no business logic or final content. Then run that row's skeleton check.

📋 **Phase 3 checkpoint:**
```
📋 PHASE 3 COMPLETE — Skeleton built (<role>)
   ✅ Structure scaffolded in {ws}/
   ✅ Stubs for every contract item
   ✅ Skeleton check passed: <the check you ran>
```

---

## Mandatory Completion Gate

Re-run 1.5a. Then `ls {ws}/plans/sessions/` and confirm `session-overview.md`, `session-1-phase-0.md`, at least one feature session, `{ws}/plans/interface-contract.md` and `{ws}/plans/.architect-manifest.json` exist. Fix anything missing before printing:

```
✅ /architect complete (<role>)

Design docs:
  • {ws}/plans/interface-contract.md
  • {ws}/plans/sessions/... [list from ls]

Skeleton:
  [key files created]

Next: /start-session <role> to begin session-2-phase-1.
```

In the `## Persona: <role>` block of `.cursor/context.md`, set `Active Phase: Phase 1`.

---

## Usage Examples

```
/architect engineer "Expense tracker API"
/architect pm exercises/pm/01-notes-to-prd/README.md
/architect designer "Budget overview screen"
/architect data-scientist "Categorise transactions"
/architect accountant "October bank reconciliation and flux"
```

## Key Rules

- One persona per run. Several active personas → run `/architect <role>` once for each.
- Everything goes in `{ws}/`. Never write into another persona's workspace.
- Never skip Phase 1.5 or Phase 2. Never create code or content files during Phase 1.
- Always write `{ws}/plans/.architect-manifest.json`.
- Never list all architecture shapes in chat.
