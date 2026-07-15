---
description: Begin a development session with active context
---

# Start Session Command

Initializes the AI context for the current work session. This command ensures the AI "knows" the project rules, stack, and current phase before writing any code.

## Execution Flow

**1. Context Check**
- Read `.cursor/context.md`.
- **Condition**: If the file contains "No Stack Configured" or is missing:
  - Stop.
  - Tell the user: "⚠️ Project is not configured. Please run **`@setup-stack`** first."

**1.5. Phase State Check**
- Read `plan/PHASES.md`.
- **Condition**: If the file is missing, or has no `CURRENT_PHASE:` footer, or no matching `## Phase {CURRENT_PHASE}` block:
  - Stop.
  - Tell the user: "⚠️ No phase/session state found. Please run **`@architect`** first."
  - Do not guess or invent a phase.

**2. Context Loading**
- Parse the `## Phase {CURRENT_PHASE}` block from `plan/PHASES.md` (per the footer's `CURRENT_PHASE` pointer).
- Display a brief summary of the active context:
  > "Context Loaded: **{Language} / {Framework}**" (from `context.md`)
  > "Current Phase: **Phase {CURRENT_PHASE}: {Name}** ({Status})" (from `plan/PHASES.md`)
  > "Pending: {Pending items}" (from `plan/PHASES.md`)
  > "Strictness: **{Strictness Level}**" (from `context.md`)

**3. Session Goal**
- Ask: "What is the goal for this session?" (e.g., "Implement the next Pending item for the current phase")
- If the user provides a goal, cross-reference it against the `Pending` list of the current phase in `plan/PHASES.md`, not just `context.md`.

**4. Rule Enforcement**
- Remind the user (internally) to adhere to the active rules in `.cursor/rules/`.
- **Constraint**: Do not suggest code that violates the active style guide (e.g., don't use `camelCase` in Python if `snake_case` is mandated).

**5. Ready State**
- Confirm readiness: "I am ready. Guides are active. Let's build."
