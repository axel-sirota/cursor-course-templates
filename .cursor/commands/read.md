---
description: Read essential project context (Context-Aware)
---

# Read Command

Read essential project files to load context for the AI. This command is "Stack Aware" and looks for the active configuration.

## What this command reads:

1.  **Active Context**:
    - `@.cursor/context.md` (The Source of Truth)
    - `@.cursor/rules/*.mdc` (Active Rules)

2.  **Methodology**:
    - `@METHODOLOGY.md` (Core Phase/TDD principles)

3.  **Current Status**:
    - Checks for `plan/active-session.md` or similar session tracking files if they exist.

## Persona Detection (run first)

Read the active persona from context:
- Cursor: `.cursor/context.md` — look for `## Active Persona`
- Claude Code: `CLAUDE.md` — look for `## Active Persona`

If section missing or value is empty → treat as `engineer` (backwards compatible default).

Branch to the appropriate preamble below, then continue with the standard execution flow.

### Persona Preambles

**engineer:** Read context (stack + phase) + active rules + last session transition doc. Output: Stack, Current Phase, Active Rules count, Next Step.

**designer:** Read context (active persona) + active Figma context doc (if present). Output: Active Persona, Figma frame in progress, last iteration summary.

**pm:** Read context + active PRD (if present). Output: Active Persona, PRD title, story count, validation status.

**data-scientist:** Read context + active EDA doc + experiment log tail. Output: Active Persona, Dataset, Last experiment metrics, Next hypothesis.

---

## Usage
`@read` -> Loads the brain of the project.

## Quick Summary Output
After reading, provide:
- **Stack**: {Language} / {Framework}
- **Current Phase**: {Phase}
- **Next Step**: What should be done next based on context?
