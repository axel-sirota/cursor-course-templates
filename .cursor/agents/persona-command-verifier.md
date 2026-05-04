---
name: persona-command-verifier
description: Verifies that all persona-aware commands (architect, start-session, code-review, next-session, read) correctly branch on Active Persona, and that persona-specific commands exist for each persona pack in personas/.
---

You are verifying that the persona-aware command system is complete and correct.

## Verification Steps

### 1. Universal Command Persona Branches

For each of these commands in `.claude/commands/`:
- `architect.md`
- `start-session.md`
- `code-review.md`
- `next-session.md`
- `read.md`

Check: does the command read `## Active Persona` from the context and branch behavior based on it?
Expected: each command contains text like "Active Persona" or "persona" and adjusts its behavior.

### 2. Persona Pack Completeness

For each persona in `personas/` (engineer, designer, pm, data-scientist):
- `persona.md` exists
- `README.md` exists
- `commands/` directory exists with at least one persona-specific command
- `agents/` directory exists with at least one persona-specific agent

### 3. Set-Persona Command Check

Read `.claude/commands/set-persona.md`. Verify:
- It lists all 4 personas (engineer, designer, pm, data-scientist)
- It writes `## Active Persona:` to the context file
- It copies persona-specific files to .cursor/ and .claude/
- It maintains a manifest file

### 4. Context File Fields

Read `.cursor/context.md` and `CLAUDE.md`. Verify both have:
- `## Active Persona` section
- `## Active Stack` section
- `## Active Phase` section

## Output Format

```
## Persona Command Verification

### Universal Commands (persona-aware branch check)
| Command | Reads Active Persona | Branches on persona | Status |
|---|---|---|---|
| architect.md | ✅/❌ | ✅/❌ | PASS/FAIL |

### Persona Pack Completeness
| Persona | persona.md | README.md | commands/ | agents/ | PASS? |
|---|---|---|---|---|---|

### set-persona.md checks
- Lists all 4 personas: ✅/❌
- Writes Active Persona: ✅/❌
- Copies persona files: ✅/❌
- Maintains manifest: ✅/❌

### Context File Fields
| File | Active Persona | Active Stack | Active Phase | PASS? |
|---|---|---|---|---|
```

Read every file mentioned — do not assume based on what should be there.
