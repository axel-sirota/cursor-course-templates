# Session 13 — Phase J: Docs Part 1 (README + QUICKSTART + METHODOLOGY)

**Phase:** J
**Goal:** Update the three primary repo docs to reflect the persona system.
**Depends on:** Sessions 1–12 complete (all personas + set-persona + universal commands)
**Next session:** Session 14 (student_runbook + CLAUDE.md)

---

## Files to Update

```
README.md            ← ADD persona section, update Getting Started, update Commands table
QUICKSTART.md        ← ADD persona-first workflow at top
METHODOLOGY.md       ← ADD persona section after Core Principles
```

---

## Change Specifications

### `README.md`

**Getting Started section** — add step before `setup-stack`:

Before current step 3 (`@setup-stack`), add:

```
2.5. Run `@set-persona` (Cursor) or `/set-persona` (Claude Code) and pick your role:
     - `engineer` — if you write code
     - `designer` — if you build prototypes
     - `pm` — if you write product specs
     - `data-scientist` — if you run experiments
```

Note: engineer + data-scientist then continue to `setup-stack`. Designer + PM skip it.

**Commands table** — add new row at top:

| Cursor IDE | Claude Code | Description |
|---|---|---|
| `@set-persona` | `/set-persona` | **START HERE.** Choose your role. Installs all role-specific tools. |
| (existing rows unchanged) | | |

**New section: Personas** — add after Features:

```markdown
## 🎭 Personas

This repo supports four roles. Run `@set-persona` or `/set-persona` to activate yours.

| Persona | Who it's for | What it installs |
|---|---|---|
| **engineer** | Software developers | TDD commands, code-reviewer + security-auditor agents, lint/type-check hooks, GitHub/Postgres/Playwright MCPs |
| **designer** | UI/UX designers | Figma extract/compose/iterate/handoff commands, token-validator agent, design-token hooks, Figma/Playwright MCPs |
| **pm** | Product managers | PRD validate/decompose/report commands, Three Amigos agents, INVEST/AC-format hooks, Atlassian/Jira MCPs |
| **data-scientist** | Data scientists & ML engineers | EDA/experiment/validate/handoff commands, data-profiler agent, seed/reproducibility hooks, filesystem/context7 MCPs |

Client-specific tool configurations (internal GitHub Enterprise, Jira URLs, data platforms) are injected automatically from `client-config/` if your instructor provided one.
```

### `QUICKSTART.md`

**Add at the very top** (before existing content):

```markdown
## Step 0: Choose Your Role

Before anything else, run:

- Cursor: `@set-persona`
- Claude Code: `/set-persona`

Pick your role: **engineer**, **designer**, **pm**, or **data-scientist**.

- Engineers and data scientists: then run `@setup-stack` / `/setup-stack`
- Designers and PMs: skip `setup-stack` — your persona is ready immediately

Everything below assumes you've done this first.
```

### `METHODOLOGY.md`

**Add new section** between `Core Principles` and `Command Reference`:

```markdown
## Personas

The Adaptive SDLC runs underneath all four roles. What changes per persona is the *vocabulary*, *deliverable*, and *tooling* — not the phase-based discipline.

### Shared foundation

All personas follow the same session structure:
1. `/start-session` — load context, state goal
2. Work (using persona-specific commands)
3. `/next-session` — document state, log handoffs

All personas use the same quality loop:
- Universal commands (`/architect`, `/code-review`, etc.) adapt their output per role
- Subagents handle isolated tasks without polluting the main context
- Hooks enforce quality guardrails automatically

### What's different per persona

| | Engineer | Designer | PM | Data Scientist |
|---|---|---|---|---|
| **Deliverable** | Tested code | Visual prototype | PRD + tickets | Experiment + model card |
| **Quality gate** | Tests pass + security clean | Tokens used + logic intact | INVEST + AC format | Seed set + reproducible |
| **Primary MCPs** | GitHub, Postgres | Figma, Playwright | Jira, Confluence | filesystem, context7 |
| **Handoff artifact** | PR | PR_DESCRIPTION.md | Jira tickets | model card |

### Cross-persona handoff

The capstone exercise passes one feature through all four personas:
1. PM writes the PRD with acceptance criteria
2. Designer produces the prototype consuming the PRD
3. Engineer builds the code satisfying the PRD's acceptance criteria
4. Data Scientist validates any model or data component

The shared workflow vocabulary (specs, plans, sessions, acceptance criteria) is what makes this handoff clean.
```

---

## Acceptance Criteria

- [ ] `README.md` Commands table has `set-persona` as first row
- [ ] `README.md` has `## 🎭 Personas` section with all 4 personas described
- [ ] `QUICKSTART.md` starts with "Step 0: Choose Your Role"
- [ ] `METHODOLOGY.md` has a `## Personas` section with the cross-persona handoff explanation
- [ ] No existing content in any of the three files is removed — only additions
