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

## Usage
`@read` -> Loads the brain of the project.

## Quick Summary Output
After reading, provide:
- **Stack**: {Language} / {Framework}
- **Current Phase**: {Phase}
- **Next Step**: What should be done next based on context?
