---
description: Execute Phase 0 (Architecture & Skeleton) using active stack context
---

# Architect Phase Command

Initiates **Phase 0** of the development lifecycle in **three gated phases**:
1. **Design** — produce all planning docs (session files, interface contract, phase breakdown)
2. **⛔ Human Review** — student reads and approves before anything is built
3. **Scaffold** — build the walking skeleton from the approved plan

---

## Step 0: Acceptance Criteria — Read This First

This command is NOT complete until ALL of the following exist:

| Artifact | Required | Notes |
|----------|----------|-------|
| `plans/sessions/session-overview.md` | MANDATORY | Phase breakdown + session list |
| `plans/sessions/session-1-phase-0.md` | MANDATORY | Skeleton session plan |
| `plans/sessions/session-N-phase-X.md` | MANDATORY | One file per feature phase (N≥2) |
| `plans/interface-contract.md` | MANDATORY | API/pipeline/IaC interface spec |
| Walking skeleton code | MANDATORY | Only after human approves plans/ |

You may NOT print the final ✅ summary until you have verified all of these exist via `ls`.

---

## Step 1: Persona + Context Detection

Read the active persona and stack:
- Claude Code: `CLAUDE.md` — look for `## Active Persona` and `## Active Stack`
- Cursor: `.cursor/context.md` — same fields

If persona is missing → treat as `engineer` (default).

Read `.claude/rules/*.md` (or `.cursor/rules/*.mdc`) for stack standards.

### Persona preambles (what the interface contract looks like per persona)

**engineer — by Architecture Shape:**
- **REST API** (python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs): OpenAPI routes + data model
- **Data Pipeline** (python-spark, python-mlops): job stages + schema definitions + medallion layers
- **Analytics Model** (python-dbt-snowflake): staging/mart model tree + source definitions
- **Statistical Computing** (r-tidyverse): notebook sequence + `src/` function signatures
- **IaC Playbook** (devops-ansible): role list + playbook structure + variable contract
- **GitOps Platform** (devops-k8s-helm): chart structure + values.yaml contract
- **Cloud Infrastructure** (devops-terraform): module inputs/outputs + resource map

**designer:** Component tree (what exists vs. needs creating), token requirements, layout structure. No API design.

**pm:** PRD structure — goals, non-goals, user personas, INVEST user stories, NFR categories. No implementation detail.

**data-scientist:** Experiment plan — data sources, EDA hypotheses, candidate models, success metrics, validation approach.

---

## Step 2: Plan Source Detection

Check if user provided a plan document:
- User explicitly referenced a file path (`/architect plan.md`, `/architect requirements.md`)
- User pasted plan content in the message
- Common plan files exist: `plan.md`, `requirements.md`, `PRD.md`, `design.md`, `plans/requirements.md`

**If plan found → Plan Extraction Mode (steps 3A–5A)**
**If no plan → Design Mode (steps 3B–5B)**

---

## ══════════════════════════════════════
## PHASE 1: DESIGN DOCS
## ══════════════════════════════════════

> **Goal:** Produce all planning artifacts. No code files yet.

---

### Plan Extraction Mode (3A–5A)

**3A. Extract Requirements**
- Trust the plan — do not redesign or suggest alternatives
- Extract: features, interface contract, data model, architectural decisions, tech stack specifics
- If anything is unclear: ask before proceeding ("The plan mentions auth but doesn't specify OAuth vs JWT — which?")

**4A. Verify Stack Compatibility**
- Check: does the plan's tech stack match `CLAUDE.md` / `context.md`?
- If mismatch: warn user, offer options, wait for decision before continuing

**5A. Generate Output Manifest**

Before creating any files, print this manifest (fill in actual values):

```
ARCHITECT OUTPUT MANIFEST
=========================
I will create the following files:

plans/
├── interface-contract.md       ← [describe: e.g., "7 REST endpoints for blog API"]
└── sessions/
    ├── session-overview.md     ← phase breakdown + session list
    ├── session-1-phase-0.md    ← skeleton session
    ├── session-2-phase-1.md    ← [feature name]
    └── session-N-phase-X.md   ← [feature name]

I will create ALL of the above before this command is complete.
```

Then create each file. Session file format:

```markdown
# Session N: Phase X — [Feature Name]

## Goal
[What this session accomplishes]

## Requirements (from plan)
- [Exact requirement from plan]

## Tasks
- [ ] [Concrete task]
- [ ] [Concrete task]

## Acceptance Criteria
- [ ] [Verifiable outcome — "you are done when..."]

## Verification
[How to test this session is complete]
```

📋 **Phase 1 checkpoint:** Print this when all doc files are created:
```
📋 PHASE 1 COMPLETE — Design docs written
   ✅ plans/interface-contract.md
   ✅ plans/sessions/session-overview.md
   ✅ plans/sessions/session-1-phase-0.md
   ✅ plans/sessions/session-N... ([N] total)
```

---

### Design Mode (3B–5B)

**3B. Design the Interface Contract**

Based on Architecture Shape, design the appropriate interface:
- **REST API**: design routes (method, path, request body, response)
- **Data Pipeline**: design job stages, input/output schemas, Bronze/Silver/Gold layers
- **Analytics Model**: design source definitions, staging models, mart models, grain
- **Statistical Computing**: design notebook sequence, `src/` function signatures
- **IaC Playbook**: design role list, playbook structure, variable contract
- **GitOps Platform**: design chart structure, values.yaml contract, ArgoCD app
- **Cloud Infrastructure**: design module inputs/outputs, resource map

**4B. Generate Output Manifest**

Before creating any files, print this manifest (fill in actual values):

```
ARCHITECT OUTPUT MANIFEST
=========================
I will create the following files:

plans/
├── interface-contract.md       ← [describe what's in it]
└── sessions/
    ├── session-overview.md     ← phase breakdown + session list
    ├── session-1-phase-0.md    ← skeleton session
    ├── session-2-phase-1.md    ← [feature name]
    └── session-N-phase-X.md   ← [feature name]

I will create ALL of the above before this command is complete.
```

Then create each file using the session format from 5A above.

📋 **Phase 1 checkpoint:** Print when all doc files are created:
```
📋 PHASE 1 COMPLETE — Design docs written
   ✅ plans/interface-contract.md
   ✅ plans/sessions/session-overview.md
   ✅ plans/sessions/session-1-phase-0.md
   ✅ plans/sessions/session-N... ([N] total)
```

---

## ══════════════════════════════════════
## ⛔ PHASE 2: HUMAN REVIEW GATE
## ══════════════════════════════════════

After Phase 1 is complete, print EXACTLY this and STOP. Do not write any code. Do not scaffold. Do not proceed:

```
⛔ REVIEW REQUIRED — No code has been written yet. This is intentional.

Please review the planning docs before we build anything:

  📂 plans/interface-contract.md   — the full interface design
  📂 plans/sessions/               — [N] session files

Questions to ask yourself:
  • Does the interface match what you want to build?
  • Are there features missing or features you don't need?
  • Do the session files break the work into reasonable chunks?

To modify: edit any file in plans/ directly, then tell me what changed.

When you are satisfied with the plan, say: "approved" or "looks good" or "proceed".
Do NOT proceed until the student explicitly approves.
```

**Wait for explicit human approval before continuing to Phase 3.**

Acceptable approval signals: "approved", "looks good", "proceed", "ok go ahead", "yes", "lgtm", "build it", or equivalent affirmative.

If the student asks for changes: make them in the plans/ files, re-print the Phase 2 gate message, and wait again.

---

## ══════════════════════════════════════
## PHASE 3: SCAFFOLD (after approval only)
## ══════════════════════════════════════

> **Goal:** Build the walking skeleton from the approved plan. Stub implementations only — no business logic.

Read `plans/sessions/session-1-phase-0.md` to understand what to scaffold.

**Scaffold rules by Architecture Shape:**

- **REST API**: scaffold directory structure per stack pattern, create entrypoint, create stub route handlers returning hardcoded 200 OK
- **Data Pipeline**: scaffold job entry script, create stub Bronze/Silver/Gold stage functions returning empty DataFrames
- **Analytics Model (dbt)**: scaffold staging + mart model stubs with `select 1 as placeholder`
- **Statistical Computing (R)**: scaffold analysis/ notebook structure, stub `src/` functions
- **IaC Playbook**: scaffold role directory structure, stub tasks with `# TODO` comments
- **GitOps Platform**: scaffold Chart.yaml, values.yaml, stub deployment/service templates
- **Cloud Infrastructure**: scaffold module structure, stub `main.tf`, `variables.tf`, `outputs.tf`

After scaffolding, verify the skeleton runs:
- **REST API**: start the server, confirm all stub endpoints respond
- **Pipeline/IaC/R**: validate syntax (e.g., `terraform validate`, `dbt parse`, `Rscript --parse`)

📋 **Phase 3 checkpoint:** Print when scaffold is complete:
```
📋 PHASE 3 COMPLETE — Skeleton built
   ✅ Directory structure scaffolded
   ✅ Entrypoint created
   ✅ Stub implementations created for all interfaces
   ✅ Skeleton verified (runs/parses without errors)
```

---

## Mandatory Completion Gate

Before printing the final ✅ summary, run these checks:

```bash
ls plans/sessions/
```

Confirm:
- `session-overview.md` exists
- At least 2 session files exist (`session-1-phase-0.md` + at least one feature session)
- `plans/interface-contract.md` exists

If ANY file is missing: create it NOW. Do not print the final summary until all files exist.

Then print:

```
✅ /architect complete

Phase 1 — Design docs:
  • plans/interface-contract.md
  • plans/sessions/session-overview.md
  • plans/sessions/session-1-phase-0.md
  [list all session files from ls output]

Phase 3 — Skeleton:
  [list key files created]

Next: Run /start-session to begin implementing session-2-phase-1.
```

---

## Usage Examples

```
/architect "Build a blog API"
```
→ Design Mode — AI designs interface → writes docs → ⛔ waits for approval → scaffolds

```
/architect plan.md
```
→ Plan Extraction Mode — reads plan.md → extracts requirements → writes docs → ⛔ waits for approval → scaffolds

```
/architect requirements.md
```
→ Plan Extraction Mode — data pipeline or IaC plan

---

## Key Rules

- **Never skip Phase 2.** The student must explicitly approve the plan before code is written.
- **Never create code files during Phase 1.** Docs only until Phase 2 is cleared.
- **Never print ✅ summary without running `ls` to verify files exist.**
- **`plans/` not `plan/`** — always use `plans/` (with s) as the directory name.
- **Session files are MANDATORY** — at minimum: session-overview.md + session-1-phase-0.md + one feature session.
