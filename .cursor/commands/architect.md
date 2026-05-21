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

If persona is missing → **STOP**. Tell the user: "⚠️ No persona configured. Run **/set-persona** first, then come back to `/architect`." Do not proceed.

Read `.claude/rules/*.md` (or `.cursor/rules/*.mdc`) for stack standards.

### Persona preambles (what the interface contract looks like per persona)

**engineer / data-scientist / devops — derive from Active Stack, do NOT enumerate all shapes.**

Read `## Active Stack` from CLAUDE.md and look up the architecture shape via this table. Then load ONLY that shape's preamble below. Do not show the full table to the user — they only need to see the preamble for their own stack. (Listing every shape every time is what creates REST bias and noise.)

| Active Stack | Architecture Shape | Interface contract is... |
|---|---|---|
| python-fastapi, go-gin, java-spring, node-express, node-nestjs | REST API | OpenAPI routes + data model |
| go-grpc | gRPC Service | `.proto` service definitions + message types |
| python-spark, python-mlops | Data Pipeline | job stages + schema definitions + medallion layers |
| python-dbt-snowflake | Analytics Model | staging/mart model tree + source definitions |
| r-tidyverse | Statistical Computing | notebook sequence + `src/` function signatures |
| devops-ansible | IaC Playbook | role list + playbook structure + variable contract |
| devops-k8s-helm | GitOps Platform | chart structure + values.yaml contract |
| devops-terraform | Cloud Infrastructure | module inputs/outputs + resource map |
| python-datascience | Experiment Notebook | EDA sequence + model candidates + evaluation metrics |
| {custom from `new` stack} | Read shape from stacks/{stack}/context.md `Architecture Shape` field | Adapt — ask user if unclear |

If the active stack is missing or unknown, **STOP** and tell the user to run `/setup-stack` first. Do not assume REST.

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

**5A. Generate Output Manifest (chat + disk)**

Before creating any session files, do TWO things:

(1) Print the manifest to chat (fill in actual values):

```
ARCHITECT OUTPUT MANIFEST
=========================
I will create the following files:

plans/
├── interface-contract.md       ← [describe: e.g., "7 REST endpoints for task tracker"]
└── sessions/
    ├── session-overview.md     ← phase breakdown + session list
    ├── session-1-phase-0.md    ← skeleton session
    ├── session-2-phase-1.md    ← [feature name]
    └── session-N-phase-X.md   ← [feature name]

I will create ALL of the above before this command is complete.
```

(2) **Persist the manifest to disk** at `plans/.architect-manifest.json` so the Phase 1.5 self-audit can diff disk-vs-promise:

```json
{
  "generated_at": "{ISO 8601}",
  "mode": "extract | design",
  "active_stack": "{from CLAUDE.md}",
  "architecture_shape": "{from CLAUDE.md}",
  "planned_files": [
    {"path": "plans/interface-contract.md",          "purpose": "..."},
    {"path": "plans/sessions/session-overview.md",   "purpose": "..."},
    {"path": "plans/sessions/session-1-phase-0.md",  "purpose": "skeleton"},
    {"path": "plans/sessions/session-2-phase-1.md",  "purpose": "{feature}"}
  ],
  "interface_items": [
    "{e.g. 'GET /tasks', 'POST /tasks', 'GET /tasks/{id}'}"
  ]
}
```

`interface_items` is the exhaustive list of routes / job stages / dbt models / roles / etc. — whatever the contract specifies. The self-audit checks that every item appears in either the skeleton or a feature session.

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

Look up the Active Stack's Architecture Shape in the dispatch table from Step 1. Design ONLY that shape's interface — do not enumerate alternatives. Per-shape guidance:

- **REST API** → design routes (method, path, request body, response)
- **gRPC Service** → design `.proto` service + message types
- **Data Pipeline** → design job stages, input/output schemas, Bronze/Silver/Gold layers
- **Analytics Model** → design source definitions, staging models, mart models, grain
- **Statistical Computing** → design notebook sequence, `src/` function signatures
- **Experiment Notebook** → design EDA sequence, candidate models, evaluation metrics
- **IaC Playbook** → design role list, playbook structure, variable contract
- **GitOps Platform** → design chart structure, values.yaml contract, ArgoCD app
- **Cloud Infrastructure** → design module inputs/outputs, resource map

If the shape doesn't match any of the above (a custom stack), read `stacks/{active}/context.md` for guidance, and ask the user what the interface contract should look like before proceeding.

**4B. Generate Output Manifest (chat + disk)**

Same as 5A above: print the manifest to chat AND persist it to `plans/.architect-manifest.json` with the same JSON shape (`planned_files`, `interface_items`, etc.). The self-audit in Phase 1.5 depends on this file. Then create each file using the session format from 5A above.

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
## PHASE 1.5: SELF-AUDIT (adversarial loop)
## ══════════════════════════════════════

> **Goal:** Before showing the plan to the human, automatically check that what's on disk matches what we promised. This catches the common failure mode of "promised 5 sessions, wrote 2".

This phase runs SILENTLY (no chat output) unless something fails. If everything matches, just print one line at the end: `🔍 self-audit passed ({N} planned files, {M} interface items)` and proceed to Phase 2. If anything fails, FIX IT NOW or surface it to the user before Phase 2.

### 1.5a. Manifest diff (structural)

Read `plans/.architect-manifest.json` (just written in Phase 1) and `ls plans/sessions/ plans/interface-contract.md` (disk reality).

For each file in `planned_files`:
- **If disk path exists:** ✅ ok
- **If disk path is MISSING:** ❌ critical drift. Create the file NOW using the format from 5A. Do not move on until every planned file exists.

For each file on disk under `plans/sessions/` or `plans/interface-contract.md`:
- **If it's NOT in `planned_files`:** ⚠️ extra file. Print a warning to chat: `"Extra file on disk not in manifest: {path}. Did you mean to create it? (keep / remove / add-to-manifest)"`. Wait for user decision before continuing.

### 1.5b. Coverage diff (semantic)

Read every session file (`plans/sessions/session-*.md`) and extract the items they mention in their "Requirements" and "Tasks" sections.

For each item in `interface_items` (the contract — every endpoint / job stage / dbt model / role / etc.):
- **If it's mentioned in `session-1-phase-0.md` (skeleton) OR any feature session:** ✅ covered
- **If it's NOT mentioned anywhere:** ❌ orphaned contract item. Print: `"Interface item '{item}' is in the contract but no session implements it. Either (a) add a session for it, (b) move it into an existing session, or (c) remove it from the contract."` Wait for user decision.

For each session's mentioned items:
- **If a session mentions an item NOT in `interface_items`:** ⚠️ session promises something the contract didn't declare. Print: `"Session {N} mentions '{item}' but the interface contract doesn't list it. Add to contract, or remove from session?"` Wait.

### 1.5c. Structured self-critique (adversarial review)

After 1.5a and 1.5b are clean, ask yourself the following questions out loud (write the answers to chat, one paragraph each):

1. **Does Phase 0 (`session-1-phase-0.md`) actually build a walking skeleton of everything in the contract?** If the contract has 7 endpoints but Phase 0 stubs only 3, that's a gap — Phase 0's job is the full stub surface. Fix or call out.
2. **Are the feature sessions ordered by dependency, not by enumeration order?** If session-3 depends on something session-5 builds, the order is wrong. Re-order or note the dependency.
3. **Is any session doing too much?** A session should be 1-4 hours of focused work. If a session's task list looks like a whole sprint, split it.
4. **Are the acceptance criteria verifiable?** Each session's "you are done when..." must be testable, not vague ("looks good"). Reject vague ACs.
5. **Does the interface contract make sense for the chosen Architecture Shape?** REST contract for a Data Pipeline stack = wrong. Check stack ↔ contract coherence.

If any answer is "no" or "unclear", fix the relevant file BEFORE moving to Phase 2. Re-write the manifest entry to match if you change the structure.

### 1.5d. Audit summary

Print this only after all three sub-steps pass:

```
🔍 PHASE 1.5 SELF-AUDIT PASSED
   ✅ Manifest diff: {N} planned files, all present, no extras
   ✅ Coverage diff: {M} interface items, all covered by sessions
   ✅ Structured critique: skeleton complete, sessions well-scoped, ACs verifiable
```

Only then proceed to Phase 2.

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

**Scaffold rules — apply ONLY the active stack's shape, not all of them:**

- **REST API** → scaffold directory structure per stack pattern, create entrypoint, create stub route handlers returning hardcoded 200 OK
- **gRPC Service** → scaffold proto file, generate stubs, implement no-op service methods returning empty messages
- **Data Pipeline** → scaffold job entry script, create stub Bronze/Silver/Gold stage functions returning empty DataFrames
- **Analytics Model (dbt)** → scaffold staging + mart model stubs with `select 1 as placeholder`
- **Statistical Computing (R)** → scaffold analysis/ notebook structure, stub `src/` functions
- **Experiment Notebook** → scaffold `notebooks/` with EDA template, `data/` placeholder, `models/` stub
- **IaC Playbook** → scaffold role directory structure, stub tasks with `# TODO` comments
- **GitOps Platform** → scaffold Chart.yaml, values.yaml, stub deployment/service templates
- **Cloud Infrastructure** → scaffold module structure, stub `main.tf`, `variables.tf`, `outputs.tf`

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

Before printing the final ✅ summary, re-run Phase 1.5 one more time (manifest diff only — sub-step 1.5a). Scaffolding in Phase 3 may have created additional files; verify they are recorded in `plans/.architect-manifest.json` if they are planning artifacts (not implementation code — implementation code does NOT go in the manifest).

Then `ls plans/sessions/` and confirm:
- `session-overview.md` exists
- At least 2 session files exist (`session-1-phase-0.md` + at least one feature session)
- `plans/interface-contract.md` exists
- `plans/.architect-manifest.json` exists (was written in Phase 1)

If ANY of the above is missing: create or fix it NOW. Do not print the final summary until all checks pass.

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

Examples adapt to the active Architecture Shape — REST is just one of several. The shape is read from `## Architecture Shape` in CLAUDE.md (set by `/setup-stack`).

```
# REST API (python-fastapi, go-gin, java-spring, node-*):
/architect "Build a task tracker"

# Data Pipeline (python-spark, python-mlops):
/architect "Build a sales ETL with daily aggregations"

# Analytics Model (python-dbt-snowflake):
/architect "Model customer LTV from raw orders"

# Statistical Computing (r-tidyverse):
/architect "Time-series analysis of regional sales"

# Cloud Infrastructure (devops-terraform):
/architect "VPC + ALB + ECS service for staging"

# GitOps Platform (devops-k8s-helm):
/architect "Helm chart for our microservice with HPA"

# From an existing plan document:
/architect plan.md
/architect requirements.md
```

All forms write `plans/.architect-manifest.json`, run Phase 1.5 self-audit, and wait for human approval before scaffolding.

---

## Key Rules

- **Never skip Phase 1.5.** Self-audit catches the "promised 5, wrote 2" failure mode. Always run all three sub-steps (1.5a manifest diff, 1.5b coverage diff, 1.5c structured critique).
- **Never skip Phase 2.** The student must explicitly approve the plan before code is written.
- **Never create code files during Phase 1.** Docs only until Phase 2 is cleared.
- **Always write `plans/.architect-manifest.json`** when generating the output manifest in Phase 1 — Phase 1.5 depends on it.
- **`plans/` not `plan/`** — always use `plans/` (with s) as the directory name.
- **Session files are MANDATORY** — at minimum: session-overview.md + session-1-phase-0.md + one feature session.
- **Never enumerate all 9 architecture shapes** in chat. Derive the shape from `## Architecture Shape` in CLAUDE.md and show only that shape's guidance. Listing every shape is what creates REST bias and student confusion.
