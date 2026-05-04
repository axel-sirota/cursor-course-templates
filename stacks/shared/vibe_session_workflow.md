# AI Session Workflow

This document defines how to structure work sessions with an AI coding assistant.
It is fully language-agnostic and applies to any stack.

---

## What a Session Is

A session is a **bounded unit of work** with:
- A defined **goal** (what will be accomplished)
- A defined **start state** (where we are now)
- A defined **end state** (what "done" looks like)

Sessions prevent context drift — the tendency for long conversations to lose track
of the original objective and accumulate half-finished tangents.

A session should represent roughly 1–3 hours of focused work. If the goal is larger,
break it into multiple sessions with transition docs between them.

---

## Starting a Session (`/start-session`)

Before writing any code, establish context explicitly.

**Steps:**

1. **Load context** — read the persona file, stack rules, and active phase document.
   Confirm which phase is active and what its acceptance criteria are.

2. **Read the transition doc** — if a previous session ended with a transition doc,
   read it first. The "Next session" and "Files to load" sections are your starting point.

3. **State the session goal explicitly** — write it out in plain language before
   opening any files. Example:
   > "This session: implement the email verification endpoint, write integration tests,
   > and confirm all quality gates pass."

4. **Confirm scope** — does this goal fit within the current active phase?
   If the goal would advance the phase, confirm acceptance criteria are fully met first.
   Do not assume a phase is done because the primary work is done.

---

## During a Session

### One thing at a time

Finish the current task before starting a new one. If you discover a related issue
while working, note it and return after the current task is complete. Do not chase
tangents mid-task.

### Use subagents for isolated work

Delegate isolated, verifiable tasks to subagents:
- Running the test suite
- Checking code style
- Validating file formats or schemas
- Searching for patterns across the codebase

This keeps the main session context clean and makes it easier to see what succeeded
or failed.

### Commit working checkpoints

Do not accumulate hours of work without committing. After each complete, working unit
(a function that passes its tests, a schema that validates, a migration that runs):

```
git add {files}
git commit -m "feat: {what was just completed}"
```

Working checkpoints make it easy to roll back if the next step goes wrong.
They also produce a meaningful commit history rather than one giant commit at the end.

### Stop if the goal is wrong

If you discover mid-session that the stated goal is incorrect, incomplete, or based
on a misunderstanding — **stop**. Do not push forward on a wrong heading.

Instead:
1. Commit or stash whatever work is in progress.
2. State what you discovered and why the goal needs updating.
3. Revise the goal with the user.
4. Resume with the corrected goal.

Pushing forward when you know the direction is wrong wastes time and produces work
that will need to be undone.

---

## Ending a Session (`/next-session`)

Close every session deliberately. Do not let a session just trail off.

**Steps:**

1. **Run the quality gate** — the stack's full quality command must pass before
   the session is considered complete. Fix any issues before proceeding.

2. **Commit everything** — all work must be committed with meaningful messages.
   No uncommitted changes at the end of a session.

3. **Write the transition doc** — see format below. This is what the next session
   reads to resume without losing context.

4. **Update the active phase if criteria are met** — if all acceptance criteria for
   the current phase are satisfied, update `## Active Phase` in the context doc.
   Do not advance the phase unilaterally — confirm with the user first.

---

## Transition Doc Format

Save as a file in the project's transitions directory (e.g., `plans/transitions/`).
Name it by date and goal: `2026-05-04-add-email-verification.md`.

```markdown
## Session: {date} {goal}

### Accomplished
- {What was completed, one line per item}
- {Include file paths where relevant}

### Stopped at
{Exact file, function, or task where work stopped.
Be specific enough that the next session can resume without re-reading everything.}

### Next session
{The first action to take in the next session. One concrete step.}

### Files to load
- {path/to/file1} — {why it's relevant}
- {path/to/file2} — {why it's relevant}
```

The transition doc is the contract between sessions. Write it for yourself at the
start of the next session — assume you will remember nothing.

---

## Phase Gates

Phases advance when **all** acceptance criteria are met — not when the primary work
is done, not when it "mostly works," and not when the developer is tired of the phase.

Rules:
- The AI must not advance a phase unilaterally. Always confirm with the user.
- "Acceptance criteria" means the exact criteria written in the phase plan, not a
  subjective interpretation of them.
- If some criteria are met and others are not, state clearly which are incomplete.
  Do not declare the phase done.
- Partial progress is recorded in the transition doc and picked up in the next session.

---

## Anti-Patterns to Avoid

| Anti-pattern | Why it's harmful |
|---|---|
| Starting work before stating the goal | Context drifts; session produces the wrong thing |
| Skipping the transition doc | Next session starts cold; work is lost or repeated |
| Accumulating uncommitted work | One bad step can undo hours; history is unreadable |
| Chasing tangents mid-task | Current task is never truly finished |
| Advancing a phase without confirming criteria | Phase acceptance becomes meaningless |
| Pushing forward on a wrong goal | All work gets undone; trust is damaged |
