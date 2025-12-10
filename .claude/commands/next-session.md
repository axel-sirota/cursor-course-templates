---
description: Generate a transition prompt for the next coding session
---

# Next Session Command

Wraps up the current work and generates a "Context Beacon" for the next time you work.

## Execution Flow

**1. Analyze Session**
- What files were changed?
- What tests are passing?
- What is pending?

**2. Update Context**
- If `CLAUDE.md` tracks "Active Phase", suggest updating it if the phase is complete.

**3. Generate Transition Prompt**
Output a code block the user can copy-paste (or save to a file):

```markdown
# Session Transition
**Last Status**: [Success/Fail]
**Stopped At**: [Function/File being worked on]
**Next Step**: [Immediate action for next session]

**Context to Load**:
- CLAUDE.md
- [Relevant Source File]
```

## Usage
`/next-session`
-> *Generates summary and next steps.*
