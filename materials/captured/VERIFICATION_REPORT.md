# Wave-2 Live Verification Report — w2-i01-verify-run

Environment: macOS (darwin 25.5), Claude Code CLI **2.1.218**, Python 3.14.5 (venv),
Node v24.16.0. Scratch copy: `/private/tmp/refund-monorepo` (copied out of
`sample-monorepo/python-fastapi` per its own design; `./init.sh` run there).

Every demo below was exercised for real against the Wave-1 assets. Captures are
trimmed terminal/transcript output from those runs — nothing is reconstructed
(including Demo 8, which ran live with the experimental teams flag).

## Setup verification

- `./init.sh` in the scratch copy: git init + initial commit + `.env` — worked first try,
  idempotence guard and course-repo guard both present. **It really built the
  `flat-claude-md` branch from the Wave-1 CLAUDE.md files** (4 files squashed into one
  root file, service files removed on that branch) — the Demo 4 dependency holds.
- venv + `pip install` of all three services' requirements: clean (fastapi 0.139.2,
  pydantic 2.13.4, pytest 9.1.1 on Python 3.14).
- Baseline suites before any demo: gateway 4 passed, notifications 5 passed,
  payments 4 passed.
- Part 1.5 verified NOT implemented before Demo 5 (no `GET /refunds/{refund_id}`
  route in payments or gateway, no `refund_id` filter in notifications) — the
  "your turn" slice was intact, as the spec promises.

## Per-demo results

### Demo 1 — scoped payments agent · **PASS** · `demo1-transcript.txt`
Delegated "add an amount-format check to payments" to `payments-implementer`.
Reads roamed to contracts/ and the spec; every Edit/Write stayed inside
`services/payments/`; suite went 4 → 27 passed; the agent ended with the exact
machine-checkable JSON completion report its definition demands. path_guard never
had to fire (nothing strayed).

### Demo 2 — worktree isolation · **PASS** · `demo2-worktree-list.txt`
`changelog-scribe` agent (frontmatter exactly as the fragment) ran while a second
terminal captured `git worktree list` mid-run: agent worktree + `worktree-*` branch
present, **both at the same commit as HEAD (cc106e8), proving `baseRef: "head"`**
(HEAD was a fresh commit, not the initial one); main checkout stayed clean during
the run. Deviation for w2-i02: after a genuine no-change run, the worktree and
branch were NOT auto-removed on 2.1.218 — the worktree survives holding only the
`.venv` symlink from `symlinkDirectories`, and cleanup is manual
(`git worktree remove` + `git branch -D`). The fragment's step-5 expected output
needs patching to match.

### Demo 3 — InstructionsLoaded lazy-load · **PASS** · `demo3-instructions-log.txt`
Used the exact hook JSON from `materials/fragments/nested-claude-md.html` in
`.claude/settings.local.json`. The event exists on 2.1.218 and fired for real:
root `CLAUDE.md` with `load_reason:"session_start"` at launch;
`services/payments/CLAUDE.md` with `load_reason:"nested_traversal"` +
`trigger_file_path` the payments README the session read; gateway's file never
appeared. All three loading rules on the record.

### Demo 4 — /context flat vs nested · **PASS** · `demo4-context-before.txt`, `demo4-context-after.txt`
Measured with `--setting-sources project,local` so only the repo's own memory is
counted. Memory-files category: **flat-claude-md 2.6k tokens (one fat root file)
vs main 817 tokens (root only) — a 68.6% (~69%) reduction** on that category.
Behavior note for w2-i02: after the lazy load, the nested payments file did NOT
join the `/context` Memory Files table in a continued print-mode session — its
tokens ride in Messages (8 → 4.2k). The fragment's "has joined the list" claim
should be softened or re-verified interactively; the InstructionsLoaded log
(Demo 3) is the reliable lazy-load evidence.

### Demo 5 — /implement-across-services · **PASS** · `demo5-activity-tail.txt`, `demo5-git-graph.txt`
The command read the spec, spawned all three implementers in parallel (3 agent
worktrees live at once), implemented exactly the Part 1.5 slice, and merged
sequentially in dependency order with `contracts/validate.sh` after each merge.
Post-merge suites: payments 8, notifications 8, gateway 7 — all passed, including
the new Part 1.5 tests. Git graph shows the three-branch signature the fragment
narrates. ~4 minutes wall clock. Note: `tool_usage.jsonl`'s `agent` field logs
"main" for every row (CLAUDE_AGENT_NAME is unset on 2.1.218); interleaving is
attributed via the worktree path in `target`, which is what the fragment's prose
already says — but `agent_activity.py`'s docstring oversells the env var.

### Demo 6 — contract gate · **FIXED** · `demo6-gate-fail.txt`, `demo6-gate-pass.txt`
**Wave-1 bug found and fixed.** As shipped, the gate could never block:
Stop/SubagentStop hooks only block on **exit code 2** and feed **stderr** back to
the agent, but `contracts/validate.sh` exited 1 on contract violations and printed
to stdout. Verified live — with the shipped script, the notifications agent
stopped cleanly with the intentional `refund.done` violation still in place (the
agent definitions even promise "blocks the stop (exit 2)"; the wrapper never
delivered it). **Fix applied in this worktree** to both variants
(`sample-monorepo/python-fastapi/contracts/validate.sh` and
`sample-monorepo/node-express/contracts/validate.sh`): on validation errors the
wrapper now emits the report to stderr and exits 2; success behavior unchanged
(exit 0, stdout); `validate.py` untouched. Re-run after the fix: the gate blocked
the agent's stop with the verbatim feedback line, blocked a second stop attempt,
the agent fixed `refund.done` → `refund.approved`, re-validated (`PASS`, exit 0,
5 tests passed) and the stop went through. Bonus real evidence: in a run where the
agent was forbidden to edit, the gate fired 8 times and then released — matching
the documented at-most-8 cap.

### Demo 7 — sparsePaths · **PASS** · `demo7-du.txt`
Added `"sparsePaths": [".claude", "services/payments", "contracts"]` to the
worktree block, spawned a payments worktree agent. All three rules held: listed
dirs only, root-level files present (plus `.env` via `.worktreeinclude` and the
`.venv` symlink), `specs/` and the two sibling services not on disk;
`git sparse-checkout list` shows exactly the three paths. Sizes: 548K working
files in the main checkout vs 136K in the sparse worktree (47M vs 136K if you
count `.venv`/`.git`, which the symlink and worktree machinery share).

### Demo 8 — agent teams · **PASS** (real run, not reconstructed) · `demo8-team-transcript.txt`
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` works in this environment; the
3-teammate contract-change scenario ran ONCE, live, with the fragment's exact
instructor prompt. Captured for real: task-board creation with ownership and
blocking dependencies, the plan-approval gate on the schema task, mailbox
messages, unblock-on-completion, and the lead's synthesis (Part 2 landed as a
coherent set: schema → payments → notifications; 31 tests passed across services;
live end-to-end POST /refunds carrying `"reason":"refund_approved"`). Two
deviations w2-i02 must fold in: (1) teammate-to-teammate DIRECT messages did not
occur — the shipped agent definitions' `tools` allowlists omit team tools, so all
31 mailbox messages were lead ↔ teammate relays; (2) the demo prompt assigns
`contracts/notification.schema.json` to payments-implementer, but that agent's
own path_guard hook fences it inside `services/payments/` — the lead had to apply
the approved schema diff itself. Either give teammates the team tools + a wider
guard for this lab, or rewrite the demo narration to match the relay pattern.

### node-express variant smoke · **PASS** (no capture required)
`node --check` clean on all 10 service .js files; fixed `validate.sh` runs on the
node variant too: gateway 1 PASS, payments 2 PASS, notifications 1 PASS, exit 0
each. (The node variant ships without the intentional violation — consistent with
the fragment, which pins Demo 6 to the python variant.)

## Wave-1 files changed by this task

- `sample-monorepo/python-fastapi/contracts/validate.sh` — exit 2 + stderr on
  violation (Demo 6 gate bug, described above).
- `sample-monorepo/node-express/contracts/validate.sh` — same fix, same reason.

## Notes for the master / w2-i02

1. **Payments emission-rule inconsistency (not fixed here — needs an owner's
   call).** `services/payments/src/refunds.py` emits a NotificationEvent only on
   the approved path and its tests assert zero events on rejection, while
   `services/payments/CLAUDE.md`, the payments README intro, and the spec's Part 1
   criterion ("every decision produces exactly one NotificationEvent") say every
   decision emits. **Five independent agent runs flagged this unprompted** during
   the demos — it WILL distract students live. Recommend either aligning the three
   docs to the code (approval-only, simplest; note an unknown payment has no
   recipient to notify, so "every decision emits" cannot hold under the current
   schema) or extending the code+tests. Doc-only fix touches spec + CLAUDE.md +
   README in both variants; not this card's asset.
2. Fragment patches implied by real captures (w2-i02's job, listed in the capture
   files themselves): Demo 2 no-change auto-cleanup claim; Demo 4 "joined the
   list" claim; Demo 5 `agent` field caveat; Demo 8 peer-message shape and
   schema-ownership conflict.
3. All capture files live in `materials/captured/` and carry `#`-comment context
   headers designed to be dropped or kept by w2-i02 when pasting into the guide's
   demo blocks.
