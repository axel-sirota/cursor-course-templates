# Lab 1 solution — Rebuild the Notifications Agent (service-scoped subagents)

Source lab: `materials/fragments/subagent-architecture.html`. Students move the
shipped agent aside (`mv .claude/agents/notifications-implementer.md
.claude/agents/notifications-implementer.md.bak`), rebuild it twice from the
payments agent as a template, then compare with the shipped one and restore it
(Demo 5 needs it back).

- **Easy:** rebuild `notifications-implementer` with `Write` and `Edit` removed from `tools`, delegate a change, and prove the allowlist blocks all writes — including ones inside `services/notifications`.
- **Hard:** restore `Write`/`Edit`, wire `path_guard.py` into the agent's frontmatter `hooks` scoped to `services/notifications`, and prove both directions: gateway edit dies with exit 2, notifications edit goes through.

Both tiers were executed live on 2026-07-24 (claude 2.1.218) against the scratch
copy; outputs below are real.

## Easy solution

Start from the payments agent, change the name/description/paths to notifications,
and cut the write tools from the frontmatter. Two deltas from the shipped file:
no `Write`/`Edit` in `tools`, and no `PreToolUse` block (there is nothing left for
`path_guard` to guard). Keep the `Stop` validate hook. Leave `isolation` out.
Lab 2 adds it.

```yaml
---
name: notifications-implementer
description: Implements features in services/notifications ONLY. Use for any notifications-service task.
tools: Read, Grep, Glob
color: orange
hooks:
  Stop:
    - hooks:
        - type: command
          command: "bash \"$CLAUDE_PROJECT_DIR\"/contracts/validate.sh services/notifications"
---
```

Note `Bash` is gone too — that is the twist, covered below. Restart `claude` (agent
files are discovered at session start), then delegate something that cannot be done
without a write:

```text
> Use the notifications-implementer agent to create a new fixture
  services/notifications/fixtures/notification_lab1.json containing one valid
  NotificationEvent for a rejected refund.
```

Real result: no file created, and the agent's report states it plainly —

```text
I read the contract and the service docs, and prepared the fixture — but I could
not create it or run the checks: this session gave me a read-only toolset
(Read, Grep, Glob only) — no Write/Edit and no shell. So nothing was written and
neither contracts/validate.sh nor pytest was executed. I will not report a
validation result I did not observe.
```

The blocked write includes in-scope paths: the fixture it could not create lives
inside `services/notifications/`. That is the tier's point made concrete —
allowlists gate *tools*, not *paths*.

**The Bash twist (observed live — teach it).** The lab text says to remove only
`Write` and `Edit`. Done literally (keeping `Bash`, as the payments template has),
the same delegation *succeeds*: in the reference run the agent, denied the Edit and
Write tools, wrote the fixture anyway with

```text
Bash: cat > /private/tmp/refund-monorepo/services/notifications/fixtures/notification_lab1.json <<'EOF' ...
```

and validate.sh passed. Nothing malicious — the agent had a job, had a shell, and
shells write files. This is the sharpest version of the lesson: the `tools`
allowlist gates named tools, not effects; any agent with `Bash` can write, so a
"read-only" agent must lose `Bash` too (or you rely on hooks, which is the Hard
tier). Run both versions if time allows — the contrast lands hard.

## Hard solution

Restore the write tools and add the canonical `path_guard` block from the fragment,
with the path argument changed to `services/notifications`. The full frontmatter:

```yaml
---
name: notifications-implementer
description: Implements features in services/notifications ONLY. Use for any notifications-service task.
tools: Read, Grep, Glob, Edit, Write, Bash
color: orange
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/path_guard.py services/notifications"
  Stop:
    - hooks:
        - type: command
          command: "bash \"$CLAUDE_PROJECT_DIR\"/contracts/validate.sh services/notifications"
---
```

(Body: the shipped agent's body is the model — scope statement, contract-first,
tests, scope fence, JSON completion report.)

Restart, then delegate one task with both directions in it:

```text
> Use the notifications-implementer agent to (1) add a comment line after the
  docstring of services/notifications/src/events.py and (2) add the same line
  after the docstring of services/gateway/src/main.py. Attempt BOTH edits and
  report exactly what happened to each, including any hook output.
```

Real transcript evidence, both directions:

```text
Edit(services/notifications/src/events.py)   -> succeeded, +1 line
Edit(services/gateway/src/main.py)           -> blocked:

PreToolUse:Edit hook error: [python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/path_guard.py services/notifications]: BLOCKED path_guard: /private/tmp/refund-monorepo/services/gateway/src/main.py is outside your service scope (services/notifications)
```

The gateway file was untouched, the agent relayed the BLOCKED message in its report
and suggested the gateway edit belongs to `gateway-implementer` — exactly the
success line the lab asks for ("the blocked attempt appears in the transcript with
the hook's BLOCKED message"). Note the hook matched on the path *segment*
`services/gateway/` inside an absolute path — that segment matching is why the
guard also works unchanged inside worktrees.

Fast pre-check that costs no session (same code path as the live event, executed
2026-07-24):

```text
$ python3 .claude/hooks/path_guard.py services/notifications --self-test services/gateway/src/main.py
BLOCKED path_guard: services/gateway/src/main.py is outside your service scope (services/notifications)
exit=2
$ python3 .claude/hooks/path_guard.py services/notifications --self-test services/notifications/src/events.py
exit=0
```

Wrap-up per the lab text: `diff` the rebuilt agent against
`.claude/agents/notifications-implementer.md.bak`, discuss the deltas (the shipped
one also carries `isolation: worktree` — Lab 2's topic), then restore the shipped
file. Verify the restore with `git diff` — clean means Demo 5 is safe.

## What students get wrong

1. **Leaving `Bash` in the Easy agent and concluding the exercise is broken** when
   the "write-blocked" agent writes the file anyway via `cat >`. That outcome is
   not failure, it is the finding — but students need the instructor to name it.
   Direct them to remove `Bash` (or compare both runs).
2. **Editing the agent file and testing in the same session.** Agent definitions
   load at session start; the running session still has the old toolset and the
   student "proves" the wrong thing. Restart `claude` after every frontmatter
   change. (First file in a brand-new `agents/` directory has the same rule.)
3. **Forgetting to restore the shipped agent afterwards** — Demo 5 and the
   capstone assume `notifications-implementer` has its full toolset, guard, and
   `isolation: worktree`. A leftover Lab 1 rebuild makes the parallel run fail in
   confusing ways two sections later. `git diff .claude/agents/` should be clean
   before moving on.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
