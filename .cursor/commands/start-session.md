---
description: Begin a work session for one persona, with its stack, rules and plan loaded
---

# Start Session Command

```
/start-session [<role>]
```

Loads one persona's context before any work happens. The session loop is always:

```
/start-session <role> → [that persona's in-session commands] → /next-session
```

## Execution Flow

### 1. Pick the persona

- Read `## Active Personas` from `.cursor/context.md`. Empty → **STOP**: "⚠️ No persona configured. Run `/set-persona add <role>` first, then `/setup-stack <role>` and `/architect <role>`." (use the role the student typed, or `<role>` if none)
- Role from the argument, else the only active persona, else ask "Which persona is this session for? {list}". Role given but not active → **STOP**: "`<role>` is not active. Run `/set-persona add <role>` first."

### 2. Check the pipeline order

Run these checks in order and stop at the first failure. Write nothing until all pass.

From the `## Persona: <role>` block:
- Stack unset → **STOP**: "`<role>` has no stack yet. Run `/setup-stack <role>` first, then `/architect <role> @exercises/<role>/<exercise>/README.md`."
- `workspaces/<role>/plans/sessions/session-overview.md` or `workspaces/<role>/plans/.architect-manifest.json` missing → **STOP**: "No plan for `<role>` yet. Run `/architect <role> @exercises/<role>/<exercise>/README.md` first. A session needs a plan."
- `.architect-manifest.json` has no `approved_at` → **STOP**: "The `<role>` plan is not approved yet. Review `workspaces/<role>/plans/` and reply \"approved\" to the `/architect` review gate. If that chat is gone, run `/architect <role>` and pick `review` to see the gate again."

Then write the role to `.cursor/.active-session` (one line, nothing else). Hooks use it to decide whose `stop` checks run.

### 3. Load context

Read, in order:
1. `personas/<role>/persona.yaml`
2. Every rule in `.cursor/rules/<role>/` (persona rules + `stack-*` rules). These govern every file written in this session.
3. Each path in `persona.yaml` → `session_context`, replacing `{workspace}` with the persona's workspace. Skip missing paths silently.
4. The lowest-numbered session file in `{workspace}/plans/sessions/` that still has unchecked tasks. That is the current session.

### 4. Show the summary

```
Session: <title> (<role>)
Stack: <stack> (<Architecture Shape>)
Phase: <Active Phase>
Current session file: <path>  (<done>/<total> tasks)
Last stopped at: <from plans/transitions/latest.md, or "first session">

In-session commands:
  <name>  <use>      (from persona.yaml → in_session_commands)
```

### 5. Agree the goal

Ask: "What is the goal for this session?" Propose the next unchecked tasks from the current session file as the default. If the goal is outside the current session or outside `workspaces/<role>/`, say so and ask whether to continue.

### 6. Ready

"Ready. Rules for <role> are active for files in workspaces/<role>/. Use the in-session commands above to make progress, and run `/next-session <role>` when you stop."

Next: work the session with the in-session commands, then `/next-session <role>`.

## Rules for the whole session

- Write only inside `workspaces/<role>/`. Reading other workspaces is fine (cross-persona exercises hand off through them); editing them is not.
- Do not suggest anything that breaks the active rules. If a rule blocks the goal, say which rule and ask.
- To switch persona mid-session, run `/next-session` first, then `/start-session <other-role>`.
