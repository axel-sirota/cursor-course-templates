---
description: Begin a development session with active context
---

# Start Session Command

Initializes the AI context for the current work session. This command ensures the AI "knows" the project rules, stack, and current phase before writing any code.

## Execution Flow

## Persona Detection (run first)

Read the active persona from context:
- Cursor: `.cursor/context.md` — look for `## Active Persona`
- Claude Code: `CLAUDE.md` — look for `## Active Persona`

If section missing or value is empty → **STOP**. Tell the user: "⚠️ No persona configured. Run **/set-persona** first, then come back to `/start-session`." Do not proceed.

Branch to the appropriate preamble below, then continue with the standard execution flow.

### Persona Preambles

Each preamble lists the persona's "in-session" commands — those are the ones the user should call DURING this session to make progress. They are not standalone commands; they are spokes of the session loop. The session loop spine is always:

```
/start-session → [persona's in-session commands] → /next-session
```

**engineer:**
- Load active stack from context + active rules.
- Show: current stack, active phase, last session summary if present.
- Ask for session goal.
- **In-session commands available:** `/engineer-tasks` (decompose the session goal into TDD-ordered tasks), `/engineer-implement` (drive the red→green→refactor loop for one task at a time). Also: `/code-review` and `/research` as needed.

**designer:**
- Load active Figma context file if present (`docs/figma-context-*.md`).
- Show: active design tokens summary, last session's prototype state.
- Ask which frame or component to work on today.
- **In-session commands available:** `/designer-extract` (pull design tokens from Figma), `/designer-compose` (assemble new components from tokens), `/designer-iterate` (apply review feedback), `/designer-handoff` (produce dev-ready spec).

**pm:**
- Load active PRD if present (`prds/` or `docs/`).
- Show: PRD title, story count, validation status.
- Ask which epic or story to focus on today.
- **In-session commands available:** `/pm-decompose` (split a PRD epic into INVEST stories), `/pm-validate` (check stories meet INVEST + have ACs), `/pm-report` (produce a sprint status summary).

**data-scientist:**
- Load active EDA doc + experiment log.
- Show: dataset in use, last experiment's metrics, next hypothesis to test.
- Ask for today's experiment goal.
- **In-session commands available:** `/ds-explore` (EDA pass on a dataset), `/ds-experiment` (run a single trained-model experiment with tracked metrics), `/ds-validate` (sanity-check results — seeds, leakage, baselines), `/ds-handoff` (model card + serving spec).

**devops:**
- Load active infrastructure context.
- Show: current stack (terraform / ansible / k8s-helm), active phase, last plan/apply state.
- Ask for today's change scope.
- **In-session commands available:** (no persona-specific commands yet — use universal `/code-review`, `/research`. Direct shell commands like `terraform plan`, `ansible-lint` are the primary tools for this persona.)

---

**1. Context Check**
- Read `CLAUDE.md`.
- **Condition**: If the file is missing or contains no `## Active Persona`:
  - Stop.
  - Tell the user: "⚠️ Project is not configured. Please run **/set-persona** first."

**2. Context Loading**
- Display a brief summary of the active context:
  > "Context Loaded: **{Language} / {Framework}**"
  > "Current Phase: **{Active Phase}**"
  > "Strictness: **{Strictness Level}**"

**3. Session Goal**
- Ask: "What is the goal for this session?"
- If the user provides a goal — e.g., "Implement POST /users" (web API), "Write Silver transform for sales pipeline" (Spark), "Add dim_customers dbt model" (dbt), "Write nginx Ansible role" (Ansible) — cross-reference it with the Active Phase in `CLAUDE.md`.

**4. Rule Enforcement**
- Remind the user (internally) to adhere to the active rules in `.claude/rules/`.
- **Constraint**: Do not suggest code that violates the active style guide (e.g., don't use `camelCase` in Python if `snake_case` is mandated).

**5. Ready State**
- Confirm readiness: "I am ready. Guides are active. Let's build."
- Remind the user how the session loop works:

  > "**To make progress in this session, use the in-session commands listed in the preamble above** (e.g. `/engineer-tasks` then `/engineer-implement` for engineer). When you're done for today, run `/next-session` to log state and generate a handoff for next time."
