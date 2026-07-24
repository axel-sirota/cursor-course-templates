# Lab 3 solution — Author a Service Context (nested CLAUDE.md)

Source lab: `materials/fragments/nested-claude-md.html`.

- **Easy:** rewrite `services/notifications/CLAUDE.md` in your own style (under 150 lines, zero duplication with the root file), then prove lazy loading with a before/after `/context` comparison.
- **Hard:** prove sibling isolation across a whole session, then add `claudeMdExcludes` to suppress one service's file entirely and verify the exclusion held.

The loading-behavior runs below were executed live on 2026-07-24 (claude 2.1.218)
against the scratch copy.

## Easy solution

A model rewrite — different voice and ordering than the shipped file, same
discipline. What matters for grading is the constraints, not the style:

```markdown
# notifications — service context

One job: turn accepted `NotificationEvent` payloads into lines of
`notifications.log`. No sends, no queues — the log IS the product.

## Hard rules
- Validation is the contract: an event either matches
  `contracts/notification.schema.json` or nothing is logged. No partial writes.
- `notifications.log` is append-only, one JSON line per accepted event. Never
  reorder, never rewrite, never commit it.
- This service calls nobody. Payments calls us; we answer. If a change seems to
  need another service's code, it belongs to that service's agent.

## Where things are
- `src/main.py` — routes (`POST /events`, `GET /events?refund_id=`)
- `src/events.py` — the validation + append logic; start reading here
- `tests/test_events.py` — accept/reject pairs; extend per behavior change
- `fixtures/notification_*.json` — one fixture per payload shape, named so
  `contracts/validate.py` picks them up

## Commands (run from this directory)
- deps:  `../../.venv/bin/python3 -m pip install -r requirements.txt`
- run:   `../../.venv/bin/python3 -m uvicorn src.main:app --port "$NOTIFICATIONS_PORT"`
- test:  `../../.venv/bin/python3 -m pytest tests/` (must pass standalone)
```

Constraint checks the instructor should demand:

- `wc -l services/notifications/CLAUDE.md` well under 150 (the model above is ~28;
  the shipped file is 40).
- Zero duplication against root: the root file (55 lines) owns the contract-first
  rule, the venv/pytest conventions, the port map, and commit style — none of those
  may reappear in the service file. The rewrite above references the schema by path
  (that is pointing, not duplicating) and states only notifications-specific rules.
  A quick audit: for each rule in the service file ask "does this apply to gateway
  too?" — if yes, it is misplaced.

Lazy-loading proof. Fresh session at the repo root, then:

```text
> /context          # note the Memory files list: root CLAUDE.md only
> Read services/notifications/README.md and summarize it in one sentence.
> /context          # services/notifications/CLAUDE.md has joined the list
```

Real evidence of the same sequence (payments variant, print mode, hook log): after
the read, the `InstructionsLoaded` hook fired with

```text
"file_path":".../services/payments/CLAUDE.md","load_reason":"nested_traversal",
"trigger_file_path":".../services/payments/README.md"
```

and before it, only the root file's `session_start` event existed. In interactive
sessions the `/context` Memory-files list shows the same two states; in print-mode
continued sessions the hook log is the reliable witness (see the Lab 4 solution's
caveat). A behavioral cross-check that needs no instrumentation: the rewritten
service file changes the agent's answers — in the live control run the session
quoted the service `CLAUDE.md`'s command conventions when critiquing the README,
proof the lazy-loaded rules were actually in play.

## Hard solution

Part 1 — sibling isolation over a whole session: register the Demo 3
`InstructionsLoaded` hook in `.claude/settings.local.json`, work several turns
strictly inside notifications (reads, small edits, tests), then:

```bash
grep notifications instructions-loaded.log   # present — nested_traversal
grep gateway instructions-loaded.log || echo "gateway CLAUDE.md never loaded"
grep payments instructions-loaded.log || echo "payments CLAUDE.md never loaded"
```

Real run (Demo 3 capture plus the 2026-07-24 re-runs): the sibling greps come back
empty every time — rule three holds for as long as you never read a sibling's file.

Part 2 — `claudeMdExcludes`. Add the exclusion to
`.claude/settings.local.json` alongside the hook:

```json
{
  "claudeMdExcludes": ["**/services/gateway/CLAUDE.md"],
  "hooks": {
    "InstructionsLoaded": [
      { "matcher": "*",
        "hooks": [ { "type": "command",
                     "command": "cat >> \"$CLAUDE_PROJECT_DIR\"/instructions-loaded.log" } ] }
    ]
  }
}
```

Restart, then force the load that rule two would normally trigger:

```text
> Read services/gateway/README.md and summarize the service in one sentence.
```

Real result: the summary comes back, and the log shows the exclusion held —

```text
$ grep -c gateway instructions-loaded.log
0
$ grep -o '"file_path":"[^"]*CLAUDE.md"' instructions-loaded.log
"file_path":"/private/tmp/refund-monorepo/CLAUDE.md"        # root only
```

Control from the same day, same machine, without the exclusion: the identical
gateway read produced a `nested_traversal` event for
`services/gateway/CLAUDE.md`. One setting, one suppressed load.

**The pattern form matters (observed live, 2.1.218).** Two plausible-looking values
failed before the glob succeeded: `"services/gateway/CLAUDE.md"` (bare relative
path) and `"services/gateway"` / `"services/gateway/**"` (directory forms) — with
each of those the gateway file still loaded. The loader matches patterns against
the file's absolute path, so use a `**/`-anchored glob:
`"**/services/gateway/CLAUDE.md"`. This is the single most likely reason a
student's exclusion "does not work".

Clean up after the lab: delete `.claude/settings.local.json` and
`instructions-loaded.log` (both are local-only; nothing to commit).

## What students get wrong

1. **A `claudeMdExcludes` entry that silently never matches** — bare relative
   paths and directory forms fail; only the `**/` glob held in the reference runs.
   The hook log turns "it seems excluded" into a checkable 0-vs-1 grep.
2. **Duplicating root rules into the service file** ("just to be safe"). It
   defeats the token math the next lab measures, and duplicated rules drift — the
   copy Claude reads last wins unpredictably. The per-rule audit question ("does
   this apply to every service?") catches it fast.
3. **Proving lazy loading with a contaminated session.** If the session already
   read a notifications file in an earlier turn, the "before" `/context` reading
   already contains the nested file and the before/after shows nothing. `/clear`
   first, then measure, then read, then measure.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
