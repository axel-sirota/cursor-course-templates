---
description: Generate a transition prompt for the next coding session
---

# Next Session Command

Wraps up the current work session by **durably persisting** phase/session state to `plan/PHASES.md` (the shared state file also read/written by `@architect` and `@start-session`), then generates a human-readable "Context Beacon" summary for chat visibility.

This command is stack-agnostic: it never assumes a web service, a specific language, or a specific manifest file. It only reads and writes `plan/PHASES.md`, whose fields are stack-neutral text.

## Execution Flow

**1. Locate Shared State**
- Read `plan/PHASES.md`.
- **Condition**: If the file is missing:
  - Stop.
  - Tell the user: "⚠️ No phase plan found at `plan/PHASES.md`. Please run **@architect** first to generate it."
  - Do NOT invent, guess, or fabricate a phase from conversation history or file inspection.
- Identify the current phase block: the first `## Phase N: <name>` block with `Status: in-progress` (fall back to the first `Status: not-started` block if none is in-progress).

**2. Analyze Session**
- What files were changed this session?
- What tests/checks are passing (per the active stack's verification method — e.g., tests running, `terraform plan` clean, app responding, CLI exiting 0, library importing/compiling — whatever the current phase's `Goal` field defines as "working")?
- What is still pending relative to that phase's `Pending` list?

**3. Update Shared State (MANDATORY — this is a file write, not a suggestion)**
- Edit the current phase block in `plan/PHASES.md` directly:
  - **Status**: update `not-started` → `in-progress` if work started this session; update `in-progress` → `complete` if every item in `Pending` is now done.
  - **Done**: move any items completed this session from `Pending` to `Done`.
  - **Pending**: add any newly discovered work items.
  - **Last session stopped at**: set to the actual file/function/module/resource/endpoint/task that was being worked on when the session ended.
  - **Next step**: set to the concrete next action, phrased so `@start-session` can act on it directly.
  - If `Status` just became `complete` and the next `## Phase N+1` block exists with `Status: not-started`, set it to `in-progress` so the next session picks up cleanly.
- Perform this edit now, on disk. Do not merely describe it.
- **If** the active context file (`.cursor/context.md`) has an "Active Phase" line, sync it to mirror the current in-progress phase's name (one-line mirror for human skimming). `plan/PHASES.md` remains the source of truth — `.cursor/context.md`'s field is not parsed by any command and is cosmetic only.

**4. Generate Transition Summary**
After `plan/PHASES.md` has been updated, output a human-readable summary of the change (for chat visibility only — the durable record already lives in `plan/PHASES.md`):

```markdown
# Session Transition
**Phase**: [Phase N: name] — Status: [not-started/in-progress/complete]
**Last Status**: [Success/Fail]
**Stopped At**: [Function/File/Resource/Task being worked on]
**Done this session**: [items moved to Done]
**Next Step**: [Immediate action for next session, matches plan/PHASES.md]

**State persisted to**: `plan/PHASES.md`
**Context to Load next time**:
- @.cursor/context.md
- @plan/PHASES.md
- @[Relevant Source File]
```

## Usage
`@next-session`
-> *Writes updated phase state to `plan/PHASES.md`, then generates summary and next steps.*
