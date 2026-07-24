# Lab 8 solution — A Small Team of Your Own (agent teams)

Source lab: `materials/fragments/agent-teams.html`. Time-boxed to 15 minutes, one
tier per student, flag enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, Sonnet
teammates, shut the team down when done.

- **Easy:** spawn a team of 2 review-only teammates over the merged refunds feature, one lens each (contract compliance vs error handling), and read where their peer messages disagree and how it resolves.
- **Hard:** spawn 3 teammates to implement the Part 2 contract change with strict file-ownership partitioning, plus a `TaskCompleted` hook that runs the service tests and exits 2 on failure, reopening at least one task.

## Easy solution — fully executed

Reference run executed 2026-07-24 (claude 2.1.218, flag on, scratch copy with the
refunds feature merged). The kickoff prompt:

```text
Create an agent team to review the refunds feature (specs/feature-refunds.md, all
three services). Spawn exactly 2 teammates in review-only mode - they must not
create, edit, or delete any file. Teammate 1 reviews contract compliance: fixtures
and emitted payloads against contracts/*.schema.json. Teammate 2 reviews error
handling across gateway, payments, notifications. Each teammate must send at least
one direct peer message to the OTHER teammate (not to you) challenging or
confirming one specific finding, and wait for the reply before finishing. Then
collect both reviews, note where they disagreed and how it resolved, write nothing
to disk, shut the team down, and report a combined summary.
```

What happened, from the run's event stream: the lead spawned `contract-reviewer`
and `error-reviewer`, each ran its own review (reads, greps, and in-process
reproduction attempts via the venv), and four teammate-to-teammate messages crossed
the mailbox — the lab's success criterion, observed for real:

```text
✉ contract-reviewer → error-reviewer
   "Challenge: notify() swallows 422 contract rejections … httpx.HTTPStatusError
    is a subclass of httpx.HTTPError, so a 4xx from notifications is caught by
    the same except as a network failure — please agree or disagree."
✉ error-reviewer → contract-reviewer
   "Rulings on your 2 claims + empty-reason challenge … CLAIM 1 — AGREE, and it's
    in my lane. Verified the hierarchy on the installed httpx 0.28.1 …"
✉ contract-reviewer → error-reviewer
   "Ruling: empty reason is mine; minLength won't be enforced by the gate —
    contracts/validate.py implements only required/type/enum/minimum, so your
    proposed schema fix would be decorative."
✉ error-reviewer → contract-reviewer
   "Closing: accept your rulings, one retraction, one gift. RETRACTION, mine …
    I implied a malformed NOTIFICATIONS_URL would 500 the refund. I tested it —
    it does not."
```

The exchange did exactly what the fragment promises teams are for: a
cross-examination. One reviewer challenged the other's finding with a concrete
class-hierarchy argument, the other verified it against the installed library and
conceded; a proposed fix was rejected because the *gate* would not enforce it; one
claim was retracted after an actual test. No lead arbitration was needed — the
disagreements resolved peer-to-peer.

The lead's synthesis (trimmed) reported findings the existing gate and suite do not
catch — all 31 tests passing and 8/8 fixtures green at the time — including:
payments crashes surfacing as gateway 500s instead of 502s (`response.json()`
outside the `try`), no `NotificationEvent` producer for the `refund.rejected` enum
value, no idempotency (three consecutive full refunds all approved), and
`contracts/validate.py` enforcing only `required`/`type`/`enum`/`minimum` so most
schema tightenings would be decorative. It then shut both teammates down and
confirmed a clean tree.

Run economics for planning the session: about 13 minutes wall clock, roughly $3.4
of Sonnet-teammate tokens for a two-reviewer team — consistent with the fragment's
"a team is a multiple of a single session" warning. Two observed deviations worth
narrating (2.1.218, print mode): the shared task board from Demo 8's interactive
run did not materialize — the lead assigned each reviewer its lens at spawn and
closed them with `TaskStop`, so "claimed/completed tasks" evidence comes from the
lead's board summary rather than `TaskCreate` events; and "review-only" held for
tracked files but pytest runs still created gitignored `.pytest_cache/` — the
constraint is a prompt convention, not a mechanism (a `PreToolUse` guard is the
mechanical version, which is exactly the Hard tier's territory).

## Hard solution — instructor-judgment: token-heavy

Do not run this per-student in class (three Sonnet teammates plus a lead for
10–15 minutes per attempt, on top of Demo 8's own run — coordinate
tokens-per-minute with the org admin even for a single instructor run). The
reference for the transcript shape is the captured instructor run,
`materials/captured/demo8-team-transcript.txt`, which implemented the same Part 2
change this tier targets. Expected shape, in order:

1. **Board setup:** three tasks — schema+payments emit, notifications
   require+log, gateway pass-through+e2e — with the schema task blocking the other
   two, one owner each.
2. **Plan-approval gate:** the schema owner stops at the gate and presents its
   plan; the lead approves with scope adjustments.
3. **Unblocking cascade:** schema lands (`e5b2fa4` in the captured run), the two
   dependent tasks unblock, teammates sync their worktrees to the new base.
4. **Gated completion:** with the `TaskCompleted` hook wired (below), a completion
   whose service tests fail is reopened — students should watch at least one task
   bounce before the team converges.
5. **Synthesis:** one combined report — in the captured run, 31 tests green across
   the three services, 8/8 fixtures PASS, and a live end-to-end POST producing a
   logged notification carrying `"reason":"refund_approved"`.

The quality-gate hook, in the shape the fragment's table describes — same JSON
wiring as the contract gates, new event name, exit 2 reopens instead of blocking a
stop:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/team_gate.sh"
          }
        ]
      }
    ]
  }
}
```

where `team_gate.sh` runs the completing service's tests (derive the service from
the task description or run all three suites — on this repo the full sweep is
seconds) and exits 2 with the failure on stderr.

Two real-run corrections to fold into any Hard-tier briefing, both observed in the
captured Demo 8 run:

- **Teammates spawned from the shipped implementer definitions have no team
  tools** — their `tools` allowlist is `Read, Grep, Glob, Edit, Write, Bash`, so
  they cannot `SendMessage` or update the board; every coordination hop relays
  through the lead. For the peer-messaging behavior the lab wants, add the team
  tools to the teammate definitions for this lab (the Easy reference run's
  teammates had them, and messaged directly).
- **Ownership partitioning collides with path_guard:** "payments-implementer owns
  `contracts/notification.schema.json`" conflicts with its own PreToolUse fence on
  `services/payments`. In the captured run the teammate flagged it and the lead
  applied the approved schema diff itself. Either hand the schema task to the lead
  explicitly, or relax the guard for this lab — decide before the run, not during.

Success check, both tiers: the task list (or the lead's board summary) shows
claimed and completed tasks, and at least one teammate-to-teammate message exists —
the Easy reference run has four.

## What students get wrong

1. **Expecting worktree isolation from a team.** Teammates share the working
   directory; two teammates editing one file corrupt each other exactly like two
   developers on one checkout. Partition ownership in the task descriptions and
   say so explicitly — worktrees are the subagent story, not the team story.
2. **Spawning teammates from the implementer agent definitions and waiting for
   peer messages that never come** — the definitions' tool allowlist has no
   SendMessage. If the mailbox stays empty, check the teammates' tools before
   blaming the feature.
3. **Not shutting the team down.** Teammates idle at full-session weight, resume
   is blocked while in-process teammates run, and the next lab inherits a stale
   team (one team per session). "Shut the team down" belongs in the kickoff
   prompt, and students should verify the teammates are gone before moving on.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
