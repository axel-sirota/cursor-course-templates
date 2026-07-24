# Lab 9 solution — The Real Thing (capstone)

Source lab: `materials/fragments/capstone.html`. The reference walkthrough is the
sample monorepo itself: the six checklist steps below were performed on the
python-fastapi variant (instructor scratch copy, `/private/tmp/refund-monorepo`),
and each step's verification gate output is recorded. Students on the Easy tier
reproduce this; the Hard tier transposes it to their own repo.

- **Easy:** run the six-step checklist against the sample monorepo variant matching your stack, every gate passing before you tick the step.
- **Hard:** run the checklist against your actual repo, with a real backlog ticket as the step-5 parallel implementation.

## Easy solution — the six steps as performed, with gate outputs

**Step 1: Detect the stack.** `/detect-stack` at the repo root. The report must
say: Python / FastAPI, three services under `services/` (gateway, payments,
notifications), tests via pytest through the repo venv, one service per pytest run.
Gate check against ground truth rather than vibes: the run and test commands in the
root `CLAUDE.md` port map and the suites in step 4 below. If the report misses the
one-pytest-run-per-service constraint (each service has its own `src` package), fix
the generated context before moving on.

**Step 2 — Nested CLAUDE.md files.** Already authored for all three services in the
sample repo; the gate is proving the loading behavior. Line budget check (executed
2026-07-24): root 55 lines, notifications 40, gateway 42, payments 66 — all inside
the 200/150 budgets, zero duplicated rules between levels. Loading gate, from the
real captured run (`materials/captured/demo3-instructions-log.txt`): root file loads
at `session_start`; `services/payments/CLAUDE.md` loads with
`load_reason: "nested_traversal"` only after a payments file is read; grep for the
gateway file returns nothing. Memory-files cost of the layout (re-measured
2026-07-24): 817 tokens on `main` vs 2.6k on `flat-claude-md`.

**Step 3 — Scoped agents + path_guard.** The three implementer agents ship with the
guard wired; the gate is watching a cross-service edit die. Executed 2026-07-24 with
the hook's own self-test (same code path as a live `PreToolUse` event, also verified
with real event JSON on stdin):

```text
$ python3 .claude/hooks/path_guard.py services/notifications --self-test services/gateway/src/main.py
BLOCKED path_guard: services/gateway/src/main.py is outside your service scope (services/notifications)
exit=2
$ python3 .claude/hooks/path_guard.py services/notifications --self-test services/notifications/src/events.py
exit=0
```

**Step 4 — Worktree settings.** The shipped `settings.json` already carries
`"baseRef": "head"` and `symlinkDirectories: [".venv"]`. Gate — a fresh worktree
runs the suite green without reinstalling dependencies — executed 2026-07-24: created
a fresh worktree, `.venv` symlinked in (as `symlinkDirectories` does per agent run),
`.env` copied (as `.worktreeinclude` does):

```text
$ (cd <worktree>/services/payments && ../../.venv/bin/python3 -m pytest -q)
13 passed
```

No pip install, immediate green — the survival-kit settings are what make that true.

**Step 5 — Parallel implementation.** Performed as the captured Demo 5 run:
`/implement-across-services specs/feature-refunds.md` implementing Part 1.5, three
agents in one message, ~4 minutes wall clock. Gate: each agent finished on its own
`worktree-*` branch and each branch touched only its own service — per-commit stats
in `materials/captured/demo5-git-graph.txt` and the Lab 5 solution file.

**Step 6 — Merge and measure.** Merged payments → notifications → gateway with
`contracts/validate.sh` after each merge (the graph with three merge commits is in
the same capture). Gate outputs re-executed 2026-07-24 on the merged result:

```text
$ for s in services/*/; do (cd "$s" && ../../.venv/bin/python3 -m pytest -q); done
gateway 7 passed · notifications 11 passed · payments 13 passed

$ for s in payments notifications gateway; do bash contracts/validate.sh services/$s; done
8/8 fixtures PASS, exit=0 for all three

Token number: Memory files 817 (nested) vs 2.6k (flat) = ~69% saved on the category.
```

All six gates green — that is the finished Easy tier. The success line of the lab
("two agents implemented in parallel on separate branches and both merged cleanly")
is steps 5–6's gates.

## Hard solution — transposing to the student's repo

Same six steps; what changes is captured by the fragment's adaptation table. The
instructor-relevant judgment calls per step:

1. `/detect-stack` matters more here — its report decides which adaptation row
   applies. Most common correction needed: monorepos whose services do not live
   under a uniform `services/` root; fix the generated context before anything else.
2. Two services minimum, root file under 200 lines, service files under 150, zero
   duplication. The gate is the same `/context` (or `InstructionsLoaded` log) check
   as the sample repo.
3. Copy `path_guard.py` verbatim; the only edit is the service path argument in each
   agent's frontmatter hook. The self-test invocation above is the fastest gate on
   any repo — no session needed.
4. The row that bites: java-spring must *not* symlink `target/` (each worktree
   builds its own; `~/.m2` is already per-user), go-gin usually needs no symlink at
   all. The gate is unchanged: fresh worktree, test suite green, no dependency
   reinstall.
5. A real two-service ticket, `/implement-across-services` adapted to the repo's
   service names. Watch the activity log, not the agents. Gate: separate branches,
   each service's tests green on its own branch.
6. Provider service merges before consumer. Gate: clean merge, full suite green, and
   a concrete before/after Memory-files number against the pre-capstone baseline the
   student recorded in Lab 4.

Time-box guidance: steps 1–4 are ~20 minutes on a cooperative repo; if a student's
repo fights step 1 or 4 (exotic layout, heavyweight builds), have them finish the
Easy tier in class and take the Hard tier home — the take-home card in the fragment
covers exactly that.

## What students get wrong

1. **Ticking a step whose gate did not pass** — usually step 2 (the nested file
   "should" load; nobody checked the log) or step 4 (the worktree ran tests green
   because the student ran them in the main checkout by accident — check the cwd in
   the test output path). A skipped gate here resurfaces as a debugging session in
   step 5, which is the most expensive place to discover it.
2. **Adapting path_guard by rewriting it** instead of changing the path argument.
   The hook matches path *segments* precisely so worktree-absolute paths still
   match; rewrites regularly break that and either block everything or fence
   nothing. Copy verbatim, change only the argument, prove it with `--self-test` in
   both directions.
3. **Picking a step-5 ticket with contract churn in it.** If the two services need
   to negotiate a payload shape mid-flight, parallel agents guess differently and
   merge time turns into arbitration — that is Lab 5 Hard's lesson. For the
   capstone, pick a ticket whose contract is already settled; settle it first if
   not.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
