---
description: Read essential project context for every active persona
---

# Read Command

```
/read [<role>]
```

Loads the project brain. With no argument, summarises every active persona; with `<role>`, only that one.

## What it reads

1. `.cursor/context.md` → `## Active Personas` and each `## Persona: <role>` block. Empty → "⚠️ No persona configured. Run `/set-persona` first." Stop.
2. `METHODOLOGY.md` (phase + TDD principles).
3. For each persona:
   - `personas/<role>/persona.yaml`
   - rules in `.cursor/rules/<role>/` (count them)
   - the paths in `persona.yaml` → `session_context` (`{workspace}` replaced; missing paths skipped)
4. `.cursor/.active-session` if present.

## Output

One table, then one line per persona with the next step:

| Persona | Stack | Shape | Phase | Rules | Current session file | Last stopped at |
|---|---|---|---|---|---|---|

Next step per persona, by the first thing that is missing:

| Missing | Next step |
|---|---|
| Stack | `/setup-stack <role>` |
| `plans/sessions/session-overview.md` | `/architect <role>` |
| nothing | `/start-session <role>` (name the next unchecked task) |

If a session is open (`.cursor/.active-session`), say which persona owns it.
