---
name: workflow-execute
description: EXECUTE a wave-structured course-build plan (the `plan/` directory produced by /workflow-plan) as a worktree-per-task build→verify→merge panel. Each task gets its OWN git worktree, so tasks in a wave run in parallel even if they touch the same files — overlap is resolved by the MASTER (sole merger) when merging each finished branch back into the feature branch. Per task: create worktree → gen_transition writes the self-contained brief → agent builds → adversarial per-task review re-running verify_cmds → serial in-script merge with is-ancestor post-condition. After all of a wave merges: a whole-wave audit against plans/blueprint.md. This is the RUNNER half of the pair; /workflow-plan is the PLANNER. Usage: /workflow-execute <plan-dir> [--wave N] [--dry-run]
argument-hint: "<plan-dir> [--wave N] [--dry-run]"
disable-model-invocation: false
user-invocable: true
---

# workflow-execute — course-build RUNNER

The execution half of the workflow pair. **`/workflow-plan` is the PLANNER** — it produces
`plans/<epic>/plan/` (`.card.yaml` cards + INDEX.md + the asset conflict report) that THIS skill
consumes. Adapted from ticket-ocr's runner: no SDD/kryla ritual (this is a course repo), no
migrations (the collision class here is shared deliverable files), no Docker tiers.

`$ARGUMENTS` = `<plan-dir> [--wave N] [--dry-run]`.

## Read the CARDS via `load_wave.py` — don't re-derive from prose
FIRST thing, always:
```bash
python3 .claude/skills/workflow-execute/scripts/load_wave.py plans/<epic>/plan --wave <N> --json
```
- **Exit 2 = UNSAFE — STOP.** HARD CONFLICT still in `asset_conflict_report.md`, or a `content` card
  still carrying `asset_intents`. Go back to `/workflow-plan` (re-run `asset_plan.py --apply`,
  re-ratify Gate 2). This loader is the gate that stops a broken plan from reaching worktrees.
- **Exit 0** → drive from the JSON:
  - `foundation_tasks` / `content_tasks` → the two phases (foundation authors shared assets —
    contracts, skeletons, settings; content consumes them). You HONOR this split, never re-classify.
  - `has_foundation` → the wave needs the foundation → barrier → content sequencing (below).
  - `ordering_edges` → build order within a phase (creator card before extender card).
  - `lock_groups` → tasks sharing a lock must not run concurrently — serialize them.
  - `overlaps` → files ≥2 tasks touch = where the merger resolves conflicts. **A `.html` overlap
    means the FRAGMENT RULE was skipped — fix the plan, don't merge-wrestle one guide file.**
  - `merge_order` → the `depends_on` topo order you merge in.
  - `verify_cmds[<id>]` / `briefs[<id>]` → per-task verification + the embedded spec.

**FROZEN-WAVE INVARIANT:** once a wave starts, wave numbers never change; re-planning only appends
new tasks to future waves. Keeps resume + traceability deterministic.

## The mental model — worktree-per-TASK, master is the merger
**One git worktree per task. The worktree IS the isolation.** Tasks in a wave parallelize because
each runs in its own worktree on its own branch — two tasks touching the same file is fine; overlap
resolves at MERGE time by the single merger. Per-task pipeline (all tasks of a wave run concurrently):
```
create worktree → gen_transition writes TRANSITION.md → agent builds → adversarial review
(re-runs verify_cmds) → MASTER merges into feat + resolves conflicts
```
After ALL of a wave is merged: whole-wave audit vs `plans/blueprint.md` → next wave. Two audit
points: per-task (gates each branch before merge) and wave-level (reviews the merged whole — the
cross-task seams no per-task review can see).

## Step 0 — Parse the wave (always `--dry-run` first)
Run the loader, list each task (id + title + files), the phase split, the overlaps. Emit and STOP if
`--dry-run`. Sanity-scan: every task's brief non-empty (the gitignore constraint — plans/ does not
exist in worktrees, the brief is ALL the agent gets), every task has verify_cmds.

## Step 0.5 — Foundation discipline (the barrier)
If `has_foundation` and the wave ALSO has content tasks: run the FOUNDATION tasks first as their own
fanout (they author the shared assets: contracts, HTML skeleton, monorepo skeleton, settings), merge
them, THEN create the content worktrees — so content tasks base off the MERGED foundations. In
practice: invoke the named workflow twice (foundation-only plan first, then content-only), or put
foundations in their own earlier wave at plan time (preferred — the 102 plan's Wave 0 IS the
foundation wave). Content agents get the hard rule: **never create/modify a shared foundation asset;
if one is missing or wrong, STOP and report** — the planner assigned exactly one owner per asset.

## Step 1 — Create worktrees + transition files
```bash
.claude/skills/workflow-execute/scripts/worktree.sh up <task-slug> <plan-slug>   # off feat HEAD
python3 .claude/skills/workflow-execute/scripts/gen_transition.py plans/<epic>/plan --wave <N> --plan-slug <plan-slug>
```
`worktree.sh up` branches `wf/<plan-slug>/<task-slug>` off the CURRENT feature-branch HEAD and
symlinks `.venv`/`.env`/`node_modules` if they exist. `gen_transition.py` writes each worktree's
TRANSITION.md from the card: the hard rules (autonomous, no pausing, fragment rule, house style,
commit-don't-merge), the phase rules, the verify_cmds, and the card's FULL embedded `brief`.

Each agent: reads TRANSITION.md IN FULL → builds the deliverable to the 101 house style (callouts,
Easy/Hard labs WITHOUT solutions + "You succeeded when…", demos WITH solutions, mermaid diagrams,
no AI-tells) → runs ALL its verify_cmds → commits on its branch (never `plans/`, never
TRANSITION.md) → reports green/red + branch + files + verify results. It does NOT push or merge.

## Step 2 — Run the wave via the NAMED workflow (do NOT author a per-wave script)
ONE canonical 4-phase workflow at **`.claude/workflows/wave-execute.js`** (build → review → MERGE →
audit, all in-script), resolvable by name and driven ENTIRELY by args:
```js
// 1. plan = load_wave.py output .plan
// 2.
Workflow({
  name: 'wave-execute',
  args: {
    plan,                          // load_wave.py's .plan (tasks/merge_order/overlaps/verify_cmds/briefs)
    feat: 'feat/course-102-build', // merge target (never main)
    base: '<pre-wave SHA>',        // for the audit diff (git diff base..feat)
    epicDir: 'plans/<epic>',       // where WAVE<N>_AUDIT.md lands
    repo: '<abs repo root>',
    planSlug: '<plan-slug>',
  },
})
```
Resumable (`resumeFromRunId` — cached agents + the idempotent is-ancestor merge mean a resume re-does
nothing). You never edit the workflow per wave — only args change. Foreground Agent calls only for a
tiny wave (≤2 tasks); never background hand-spawned build agents (600s watchdog).

## Step 3 — Per-task review (inside the fanout, before merge)
The review agent re-runs the task's verify_cmds ITSELF (fake-green guard — never trust the builder's
green), checks the fragment rule (content task diff must not touch the guide file / contracts /
settings / README), checks the house style (callout classes, lab tiers without solutions, mermaid
present where the blueprint says), and checks factual claims against the research-plan corrections
(baseRef default, teams≠worktrees, hook-based write-scoping, measure-don't-assert savings).
`mergeReady` only when all pass. RED → bounce back to the same worktree to fix, re-review.

## Step 4 — MERGE: in-script, serial, post-condition-verified
The workflow's merge phase is a deterministic serial loop — ONE merge-agent, `merge_order`, into
FEAT (never main), `--no-ff`. After each merge it ASSERTS `git merge-base --is-ancestor` (a
hand-rolled merge loop outside the workflow once silently dropped 10/14 branches — the post-condition
catches that class immediately). Hard conflict → abort that merge, STOP for the human. Conflict
resolution keeps BOTH sides' content — diff the hunk against both parents; never drop a side's
sections.

**STALE-FORK RE-VERIFY.** Each task verified on its OWN fork, not on the moving feat. After every
merge (especially conflict-resolved ones), re-run the just-merged task's verify_cmds AND the
already-merged tasks' verify_cmds on the new feat HEAD. Green→red = the merge broke an integration
(e.g. two fragments claiming the same section id, an agent file renamed out from under a command).

**SHARED-SKELETON GUARD** (the conftest analog): a task editing an inherited shared base — the 101
CSS/skeleton, root CLAUDE.md, `.claude/settings.json` of the sample monorepo — changes behavior for
every other deliverable. After merging such a branch, re-run ALL merged verify_cmds, not just its own.

## Step 5 — WAVE-LEVEL audit (after all merges)
The workflow's audit phase reviews the WHOLE merged wave (`git diff base..feat`) against
`plans/blueprint.md` + `plans/course-102-research-plan.md`: blueprint coverage (sections, diagrams
D1-D11, demos, labs — nothing silently dropped), coherence (fragments fit skeleton ids/CSS, no
root/service CLAUDE.md duplication, student vs instructor split honored — lab solutions ONLY in
instructor materials), consistency (service names/paths/commands identical across monorepo, agents,
hooks, HTML), factuality (no dated claims the research plan corrected), and runnability (init.sh,
hooks, validate.sh actually execute). Verdict → `plans/<epic>/WAVE<N>_AUDIT.md`. Fix-panel any
finding (own worktrees), re-verify, re-merge, re-audit. **BUDGET GUARD:** cap fix rounds (max 3);
if the loop never dries, STOP and escalate to Axel instead of burning tokens.

## Step 6 — Resume / re-run
Interrupted? `Workflow({scriptPath, resumeFromRunId})` — cached agents return instantly, only
failed/new tasks re-run (TaskStop a stuck run first). A workflow that died after agents BUILT but
before they COMMITTED is RECOVERABLE: inspect each worktree's uncommitted work, audit it, commit on
its branch, merge as normal. Do NOT blind-re-run — the work exists.

## Step 7 — CLEANUP (per wave, after the audit is green)
```bash
.claude/skills/workflow-execute/scripts/worktree.sh down <task-slug>   # guarded: refuses to lose
                                                                       # unmerged work, bundles first
```

## Landmines (transferable hard rules, ticket-ocr-proven, course-adapted)
1. **Worktree-per-task is the isolation — same-file overlap is OK** (the master resolves at merge).
   EXCEPT the one-big-HTML class: that's plan-time fragments, not merge-time heroics.
2. **Single merger.** Exactly one serial merger (the in-script Step-4 loop), into FEAT, never main.
   The fanout never merges; build agents never push. Axel pushes to origin.
3. **Two audit points.** Per-task before merge; whole-wave after. The wave audit catches what
   per-task review CANNOT: the inert-half class (a lab shipped without its demo, a fragment without
   its sidebar entry, an agent without its command) only exists after merge.
4. **Branch off feat, merge back to feat** — never main.
5. **600s watchdog** is background-only — the Workflow engine path avoids it; any hand-spawned build
   agent must run foreground.
6. **Fake-green guard.** Reviewers re-run verify_cmds themselves; check the diff for weakened checks;
   demand real command output, not assertions.
7. **Fat tasks hang the engine** (pipeline awaits every item). Split them at plan time; if one
   straggles, run a per-task finisher workflow for just it rather than restarting the wave.
8. **Harness merge-conflict auto-commit**: a context-snapshot commit can land `<<<<<<<` markers if a
   merge conflicts mid-save → `git reset --hard <last-clean-merge>` and re-resolve.
9. **Never `git add plans/` or TRANSITION.md** — plans/ is gitignored by design (build scaffolding
   must not ship to students); TRANSITION.md is excluded per-worktree by worktree.sh.
10. **The student/instructor split is an invariant, not a style note.** Any lab solution found
    outside `materials/instructor/` (or the `solutions` branch) is a per-task review FAIL.

## Reference files
- Planner: `.claude/skills/workflow-plan/skill.md` (+ `scripts/asset_plan.py` — the card schema).
- Scripts: `scripts/load_wave.py` (card reader/gate), `scripts/gen_transition.py` (brief writer),
  `scripts/worktree.sh` (guarded worktree up/down).
- Canonical workflow: `.claude/workflows/wave-execute.js` (run by name; `templates/wave.workflow.js`
  is a pointer).
- Course inputs the audits check against: `plans/blueprint.md`, `plans/course-102-research-plan.md`.
