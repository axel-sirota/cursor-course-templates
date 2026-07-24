# Lab 5 solution — Run It and Race It (parallel implementation)

Source lab: `materials/fragments/parallel-implementation.html`. The work item is
**Part 1.5 — your turn** of `specs/feature-refunds.md` (refund status lookup across
all three services); Part 1 ships implemented, Part 2 is reserved for Lab 8.

- **Easy:** write down a sequential-time estimate, run `/implement-across-services specs/feature-refunds.md`, time it, and verify each agent's changes landed on its own branch touching only its own service.
- **Hard:** edit the spec so two services need the same contract change, re-run, and land the merges so `contracts/validate.sh` passes after *every* merge — without ever letting an agent merge its own branch.

## Easy solution

Estimate first (typical student answer: three sequential agent runs at 3–5 minutes
each ≈ 10–15 minutes). Then:

```bash
cd ~/labs/refund-monorepo
claude
> /implement-across-services specs/feature-refunds.md
```

Real wall clock from the captured run (`materials/captured/demo5-git-graph.txt`):
about 4 minutes end to end — first agent tool call 02:42:56Z, last logged tool call
02:46:09Z, plus the merge/report turns. Roughly the time of the slowest single agent,
i.e. a third of the sequential estimate.

While it runs, `tail -f logs/tool_usage.jsonl` in a second terminal shows the three
streams interleaving within the same seconds, each line attributable by the
`agent-<id>` segment of its `target` path
(`materials/captured/demo5-activity-tail.txt`; note the observed 2.1.218 caveat — the
`agent` field logs `main` for every entry, so the worktree path in `target` is the
attribution, exactly as the fragment narrates).

Verification, branch by branch. History shape after the run (real capture):

```text
$ git log --oneline --graph
*   42cb63f Merge gateway: proxy GET /refunds/{refund_id} to payments
|\
| * ceb70c8 gateway: proxy GET /refunds/{refund_id} to payments
* |   f547c09 Merge notifications: filter GET /events by optional refund_id
|\ \
| * | c2bc908 notifications: filter GET /events by optional refund_id
| |/
* |   64c29df Merge payments: GET /refunds/{refund_id} status lookup
...
```

Each branch touches only its own service — checked with `git show --stat` on the
three agent commits (re-run 2026-07-24 on the scratch copy):

```text
0514a5e payments: add GET /refunds/{refund_id} status lookup
 services/payments/README.md | fixtures/refund_result_rejected.json |
 src/refunds.py | src/store.py | tests/test_refund_lookup.py        # payments/ only

c2bc908 notifications: filter GET /events by optional refund_id
 services/notifications/{CLAUDE.md, README.md, fixtures/..., src/events.py,
 tests/test_events.py}                                              # notifications/ only

ceb70c8 gateway: proxy GET /refunds/{refund_id} to payments
 services/gateway/{CLAUDE.md, README.md, fixtures/refund_result.json,
 src/refunds.py, tests/test_refunds.py}                             # gateway/ only
```

Success gate, re-executed 2026-07-24 on the merged result:

```text
$ for s in services/*/; do (cd "$s" && ../../.venv/bin/python3 -m pytest -q); done
gateway:        7 passed
notifications: 11 passed
payments:      13 passed

$ for s in payments notifications gateway; do bash contracts/validate.sh services/$s; done
all fixtures PASS, exit=0 for all three services
```

(Immediately after the captured Lab 5-scope run the counts were 8/8/7; the scratch
copy has since absorbed the Part 2 team work, hence 13/11/7 today. Students' numbers
right after their run should match the captured 8/8/7.)

## Hard solution

The edit: in `specs/feature-refunds.md` Part 1.5, require a shared contract change,
for example a required `requested_at` string on `RefundResult` that payments must
emit and notifications must record with its events. Two services now depend on one
schema edit.

The trap the tier is built around: the implementer agents cannot make the contract
change. Their `path_guard` PreToolUse hook fences each one inside its own
`services/<name>/` — an agent that tries to edit `contracts/refund.schema.json` gets
`BLOCKED path_guard: ... outside your service scope` (this exact conflict was
observed for real in the Demo 8 captured run, where the teammate flagged it and
handed the schema edit up to the lead). The design intent: contract changes belong to
the lead, settled *before* the fan-out.

Working sequence:

1. **Lead commits the schema change first**, on the base branch, before or right
   after spawning: add `requested_at` to `RefundResult`'s `required` and
   `properties`. Every agent worktree branches from HEAD (`baseRef: "head"`), so all
   three agents see the tightened contract from the start.
2. Run `/implement-across-services specs/feature-refunds.md` as before. Payments'
   slice includes emitting the field; notifications' slice includes recording it;
   gateway proxies unchanged.
3. Merge in dependency order — payments, notifications, gateway — running
   `bash contracts/validate.sh services/<name>` after each merge. Because the schema
   landed at the base, validation passes at every intermediate point, not just the
   last one.

What it looks like when done wrong (the point of the tier): if the schema change
instead rides inside one agent's branch — or the lead merges notifications before the
schema commit is reachable — the intermediate validate fails with exactly the
Lab 6-style line, e.g.
`FAIL fixtures/refund_result.json: field "requested_at" is required but missing.`
(mechanism executed for real in the Lab 6 Hard reference run). The fix is never "let
the notifications agent merge first" — agents never merge. The fix is reordering the
lead's merges so the providing commit lands before the consuming one, exactly like
the real Part 2 landing order in the scratch history: `e5b2fa4 contracts: ...` →
merge payments → merge notifications.

## What students get wrong

1. **The fan-out silently degrades to sequential.** If the three Agent calls do not
   go out in a single message, the run still "works" but takes the sequential time
   and the race is meaningless. The `CRITICAL: run these in PARALLEL` line in the
   command file is what prevents this; students who paraphrase the command into their
   own prompt usually lose it. Check `logs/tool_usage.jsonl` — interleaved timestamps
   are the proof of parallelism.
2. **Expecting parallel to be cheaper in tokens.** It is cheaper in wall clock only;
   three contexts each load the spec and contracts. Students comparing `/usage`
   before and after conclude something is broken. Wall-clock vs tokens is the
   fragment's explicit trade.
3. **In the Hard tier, letting an agent "just fix" the contract.** Either the
   path_guard blocks it (and the student weakens the guard to push through — exactly
   backwards), or with a weakened guard two agents guess different schema shapes and
   merge time becomes negotiation. The contract change is settled once, by the lead,
   at the base.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
