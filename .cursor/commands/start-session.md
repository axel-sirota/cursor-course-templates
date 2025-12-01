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

**2. Context Loading**
- Display a brief summary of the active context:
  > "Context Loaded: **{Language} / {Framework}**"
  > "Current Phase: **{Active Phase}**"
  > "Strictness: **{Strictness Level}**"

**3. Session Goal**
- Ask: "What is the goal for this session?"
- If the user provides a goal (e.g., "Implement POST /users"), cross-reference it with the Active Phase in `context.md`.

**4. Rule Enforcement**
- Remind the user (internally) to adhere to the active rules in `.cursor/rules/`.
- **Constraint**: Do not suggest code that violates the active style guide (e.g., don't use `camelCase` in Python if `snake_case` is mandated).

**5. Ready State**
- Confirm readiness: "I am ready. Guides are active. Let's build."
