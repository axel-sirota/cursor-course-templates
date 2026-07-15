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
    - Reads `plan/PHASES.md` — the shared phase/session state file created by `@architect` and updated by `@next-session`. If this file does not exist, state clearly that no architecture/session state has been established yet and point the user to `@architect`.

## Usage
`@read` -> Loads the brain of the project.

## Quick Summary Output
After reading, provide:
- **Stack**: {active stack name, e.g. python-fastapi, go-gin, devops-terraform, blank}
- **Current Phase**: {Phase}
- **Next Step**: What should be done next based on context?
