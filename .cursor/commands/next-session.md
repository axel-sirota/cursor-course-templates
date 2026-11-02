---
description: Close the current persona's session, run its quality gate, and write the handoff for next time
---

# Next Session Command

```
/next-session [<role>]
```

Wraps up the session started by `/start-session` and writes a transition doc.

## Execution Flow

### 1. Find the session persona

- Read `## Active Personas` from `.cursor/context.md`. Empty → **STOP**: "⚠️ No persona configured. Run **/set-persona** first."
- Role from the argument (must be active), else the role in `.cursor/.active-session`, else ask "Which persona's session are you closing? {active list}".
- Read `personas/<role>/persona.yaml`.

### 2. Run the quality gate

Run every item in `persona.yaml` → `quality_gate`, in order. Report each as ✅ / ❌ with one line of evidence (test output, agent verdict, file count). A ❌ does not block the handoff; it goes into the transition doc as the first next step.

Then check which `in_session_commands` were used this session. If none were, ask why and note the answer. It usually means the session had no structure.

### 3. Update progress

- Tick completed tasks and acceptance criteria in the current session file under `workspaces/<role>/plans/sessions/`.
- If every acceptance criterion of the current session is met, advance `Active Phase` in the `## Persona: <role>` block of `.cursor/context.md`. Otherwise leave it.

### 4. Write the transition doc

Write `workspaces/<role>/plans/transitions/<YYYY-MM-DD-HHMM>.md` and copy it to `workspaces/<role>/plans/transitions/latest.md`:

```markdown
# Session Transition (<role>)
**Date**: <ISO 8601>
**Status**: <Done / Partial / Blocked>
**Session file**: <path> (<done>/<total> tasks)
**Stopped at**: <file / task>
**Next step**: <one concrete action>

## Quality gate
<each item ✅ / ❌ with evidence>

## Files changed
<list, all under workspaces/<role>/>

## Next time
- Run `/start-session <role>`
- In-session commands: <from persona.yaml, the ones that fit the next step>
- Run `/architect <role>` instead only if the last phase just finished.
```

### 5. Clear the session marker

Delete `.cursor/.active-session` if it names this role (leave it alone if it names another persona). Print the path of the transition doc and the next step.

If other personas are active, list them with their Active Phase so the student can pick the next session.
