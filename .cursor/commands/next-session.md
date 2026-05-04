---
description: Generate a transition prompt for the next coding session
---

# Next Session Command

Wraps up the current work and generates a "Context Beacon" for the next time you work.

## Execution Flow

## Persona Detection (run first)

Read the active persona from context:
- Cursor: `.cursor/context.md` — look for `## Active Persona`
- Claude Code: `CLAUDE.md` — look for `## Active Persona`

If section missing or value is empty → treat as `engineer` (backwards compatible default).

Branch to the appropriate preamble below, then continue with the standard execution flow.

### Persona Preambles

**engineer:** Check test status (run `test-runner` subagent if available). Advance `## Active Phase` in context if phase AC are met. Generate transition doc with: session status, where stopped, next immediate step, files to load.

**designer:** Prompt for screenshot comparison via `responsive-checker` if not yet done. Update Figma context doc if design changed. Generate transition doc with: components changed, open style questions, next frame to implement.

**pm:** Run `gap-detector` on active PRD if not yet run this session. Update story count in context. Generate transition doc with: stories validated, stories remaining, next three to work on.

**data-scientist:** Invoke `experiment-tracker` to log session results if not yet done. Update experiment log summary in context. Generate transition doc with: hypothesis tested, metrics achieved, next experiment to run.

---

**1. Analyze Session**
- What files were changed?
- What tests are passing?
- What is pending?

**2. Update Context**
- If `.cursor/context.md` tracks "Active Phase", suggest updating it if the phase is complete.

**3. Generate Transition Prompt**
Output a code block the user can copy-paste (or save to a file):

```markdown
# Session Transition
**Last Status**: [Success/Fail]
**Stopped At**: [Function/File being worked on]
**Next Step**: [Immediate action for next session]

**Context to Load**:
- @.cursor/context.md
- @[Relevant Source File]
```

## Usage
`@next-session`
-> *Generates summary and next steps.*
