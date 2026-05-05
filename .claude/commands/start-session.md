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

If section missing or value is empty → treat as `engineer` (backwards compatible default).

Branch to the appropriate preamble below, then continue with the standard execution flow.

### Persona Preambles

**engineer:** Load active stack from context + active rules. Show: current stack, active phase, last session summary if present. Ask for session goal.

**designer:** Load active Figma context file if present (`docs/figma-context-*.md`). Show: active design tokens summary, last session's prototype state. Ask which frame or component to work on today.

**pm:** Load active PRD if present (`prds/` or `docs/`). Show: PRD title, story count, validation status. Ask which epic or story to focus on today.

**data-scientist:** Load active EDA doc + experiment log. Show: dataset in use, last experiment's metrics, next hypothesis to test. Ask for today's experiment goal.

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
