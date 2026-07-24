---
name: workflow-plan
description: PLAN a wave-structured course-build epic from the course blueprint. Takes plans/blueprint.md (or any deliverable list) and produces the `plan/` directory that /workflow-execute consumes — deliverable breakdown → task cards (.card.yaml with files/brief/verify_cmds/asset-intents) → a SHARED-ASSET conflict analysis (catches the everyone-edits-the-one-HTML-guide class AT PLAN TIME via the fragment rule) → human-curated dependency-ordered waves → INDEX.md. This is the PLANNER half of the pair; /workflow-execute is the RUNNER. Two human gates: scope triage, then approve the waves + asset conflict report. Usage: /workflow-plan <blueprint-file | deliverable-list> [--epic <slug>]
argument-hint: "<blueprint-file | deliverable-list> [--epic <slug>]"
disable-model-invocation: false
user-invocable: true
---

# workflow-plan — course-build PLANNER

Turns the course blueprint into a wave-structured plan that `/workflow-execute` runs. Adapted from
the ticket-ocr workflow pair; the domain here is COURSE MATERIALS (HTML guides, sample monorepos,
agents, hooks, docs), not app code. This repo is **NOT an SDD/kryla repo** — no pipeline ceremony.

`$ARGUMENTS` = `<blueprint-file | deliverable-list> [--epic <slug>]`. The epic slug defaults to the
input filename stem; the plan lands in `plans/<epic>/` (gitignored — see THE GITIGNORE CONSTRAINT).

## The collision class this planner exists for
In ticket-ocr it was parallel agents each authoring the same DB migration. Here it is parallel agents
each editing the SAME SHARED DELIVERABLE: the single-file HTML guide (~11 sections in ONE file!),
`sample-monorepo/.claude/settings.json`, `contracts/` schemas, README. The fix is identical in shape:
**declared intent + one owner per asset, resolved at PLAN time** — plus the domain-specific
**FRAGMENT RULE**: section tasks write `materials/fragments/<section-id>.html`; exactly ONE assembler
card owns the guide file and stitches fragments in.

## THE GITIGNORE CONSTRAINT (course-repo specific — affects card design)
`plans/` is gitignored, so the plan directory does NOT exist inside task worktrees. Therefore every
card MUST carry its FULL task spec in the `brief:` field — `gen_transition.py` embeds it verbatim
into each worktree's TRANSITION.md. A card whose brief says "see blueprint section 2.1" is BROKEN:
the agent cannot see the blueprint. Copy the content in.

## The output contract — `plans/<epic>/`
```
plans/<epic>/
  RAW_FINDINGS.md            # deliverable breakdown, labeled (id, source blueprint point, section)
  plan/
    INDEX.md                 # human-readable wave rationale + the embedded asset conflict report
    tasks/<task-id>.card.yaml    # the MACHINE CONTRACT /workflow-execute reads
    asset_conflict_report.md # asset_plan.py output (owners, folds, ordering edges)
```

## The pipeline

### Step 1 — Intake (blueprint → findings)
Read the input VERBATIM (normally `plans/blueprint.md` + `plans/course-102-research-plan.md`).
Extract discrete buildable units → `RAW_FINDINGS.md`: id, the blueprint point it comes from, section
(deliverable A-monorepo | B-agent-pack | C-html-guide | D-docs | E-buildprompt), and scope notes.
**[HUMAN GATE 1]** Show the list; Axel triages scope (drop, split fat units, confirm priorities —
e.g. "one stack variant or two?", "instructor HTML now or later?"). Do not proceed until ratified.

### Step 2 — Section (group by deliverable — the parallel axis)
Cluster findings into sections by deliverable. Sections fan out in parallel later. The known shape
for the 102 build (from the parallelizable-units analysis):
- **Wave 0 — foundations** (sequential-ish, small): contract schemas + validate.sh, monorepo
  skeleton + settings + init.sh + specs, HTML guide skeleton (copied from 101, sections stubbed).
- **Wave 1 — mass parallel**: 6 service implementations (3 services × 2 stacks), CLAUDE.md files,
  agents, hooks, commands, 11 HTML section fragments (+ their mermaid diagrams), README/QUICKSTART,
  build prompt.
- **Wave 2 — integration**: live verification run (critical path), lab solutions ×9, `flat-claude-md`
  + `solutions` branches, demo-output patch pass.
- **Wave 3 — assembly & review**: guide assembly from fragments, instructor HTML, coherence review
  lenses, AI-tell sweep.

### Step 3 — Emit CARDS (the machine contract)
Every task becomes `plan/tasks/<id>.card.yaml`. Schema (course v2 — see `scripts/asset_plan.py`
docstring for the annotated version):
```yaml
id: w1-c03
title: "HTML fragment: nested CLAUDE.md section"
type: content              # content | code | diagram | docs
priority: P0
section: C-html-guide      # A-monorepo | B-agent-pack | C-html-guide | D-docs | E-buildprompt
files_touched: [materials/fragments/nested-claude-md.html]    # REAL paths; prefix new files "new:"
shared_resources: []       # coarse serialize-locks; rarely needed once fragments are used
depends_on: []             # other card ids
wave: 1
phase: content             # foundation (authors a shared asset) | content (consumes foundations)
verify_cmds: ["grep -q 'id=\"nested-claude-md\"' materials/fragments/nested-claude-md.html"]
human_owner: axel
brief: |
  <THE FULL TASK SPEC — self-contained; the worktree agent sees ONLY this. Include the blueprint
  point verbatim, the Easy/Hard lab text requirements, the mermaid diagram spec, the house-style
  rules that apply, and the research-plan corrections relevant to this section.>
# foundation-phase ONLY:
asset_intents:
  - object: materials/claude-code-102-guide.html
    operation: create      # create | extend
    details: {kind: html-skeleton, sections: 11}
```
Every card MUST have ≥1 real `verify_cmds` (a grep for required ids/callouts, a script run, a JSON
parse, `bash -n`, `python3 -m py_compile`, frontmatter checks…). A card with no runnable verify is a
card whose fake-green cannot be caught.

### Step 4 — SHARED-ASSET PLANNING (the crown jewel, run `--apply`)
```bash
python3 .claude/skills/workflow-plan/scripts/asset_plan.py plans/<epic>/plan/tasks/ --apply
```
Three rules: (1) ≥2 cards author one asset → FOLD to one owner, losers become `content`;
(2) contradictory `create`s of the same asset → HARD CONFLICT → halt for the human; (3) an `extend`
of an asset another card `create`s → ordering edge creator→extender. `--apply` rewrites the cards;
it refuses to fold while a HARD CONFLICT is present. Output: `plan/asset_conflict_report.md`
(embedded into INDEX.md for Gate 2). Any wave where ≥2 cards list the same `.html` in
`files_touched` = the fragment rule was skipped — restructure into fragments + one assembler.

### Step 5 — Human-curated waves (NOT a pure topo-sort)
Group tasks into dependency-ordered waves; keep the Wave 0-3 default shape above. Emit
`plan/INDEX.md` (wave list + rationale + embedded asset report).

**THE RUNTIME-DEPENDENCY RULE (inherited from ticket-ocr Wave-2 — the hardest lesson).** A
`depends_on` between two CONTENT cards in the SAME wave is a TRAP: tasks build in parallel worktrees
off the wave's START commit, so B cannot consume A's unmerged output. Course-build instances:
- lab-solution cards depend on the live-verification run → verification is Wave 2 FIRST, solutions after.
- the guide-assembly card depends on ALL fragment cards → assembly is Wave 3, fragments Wave 1.
- instructor-HTML depends on student-HTML + solutions → Wave 3, after both.
Distinguish: an INTERFACE dependency (B reads a frozen contract/skeleton from Wave 0) is SAFE — the
foundation→barrier→content phasing handles it. An OUTPUT dependency (B needs A's produced file) is
NOT — re-wave it, or merge A+B into one card. At Gate 2, scan every intra-wave `depends_on` and
classify it.

**[HUMAN GATE 2]** Axel approves: the wave grouping (incl. the runtime-dependency scan), the asset
owners, and the conflict report (esp. any HARD CONFLICT). Do not finalize until ratified.

### Step 6 — FINAL whole-plan audit (MANDATORY before hand-off)
**A. PATH VERIFICATION.** Every `files_touched` is LLM-proposed and WILL drift. For each card:
existing paths must EXIST (`git ls-files` / `ls`); new files must carry the `new:` prefix and land in
a real parent dir. Check the known drift patterns for THIS repo: materials live in `materials/` (not
`docs/`), commands in `.claude/commands/`, stack content under `stacks/<stack>/`. A wrong path = a
worktree agent thrashing.
**B. ADVERSARIAL WHOLE-PLAN REVIEW.** Spawn a fresh adversarial review agent (or codex if available)
over ALL cards + the real tree + `plans/blueprint.md`: every blueprint point covered by exactly one
card? Any card not tracing to a blueprint point? Briefs self-contained (no "see blueprint")? Every
card's verify_cmds runnable? Intra-wave runtime deps? Fragment rule honored? Verdict → 
`plan/PLAN_REVIEW.md`; fold findings back. The plan is execution-ready ONLY on READY.
**C. LOADER SELF-CHECK.** `python3 .claude/skills/workflow-execute/scripts/load_wave.py
plans/<epic>/plan --wave N` for EVERY wave — each must exit 0. Non-zero = fix here, never in the runner.

## Hand-off to the runner
When ratified AND Step 6 passed: `/workflow-execute plans/<epic>/plan --wave 0`. The runner reads the
cards (`phase`, `asset_intents`, `files_touched`, `depends_on`, `verify_cmds`, `brief`) — it does NOT
re-derive them from prose. **FROZEN-WAVE INVARIANT:** once execution starts, wave numbers never
change; re-planning only appends NEW tasks to FUTURE waves.

## Hard rules
1. **Two human gates** — scope triage (G1) + plan-approval-with-asset-report (G2). Axel is the domain
   oracle (course pedagogy, persona/stack scope, what ships to students vs instructor). The planner
   PROPOSES; the human RATIFIES.
2. **Contention is prevented at PLAN time** by the asset planner + the fragment rule — NOT discovered
   as merge hell on one 90KB HTML file.
3. **One owner per shared asset.** The guide file, each contract schema, each settings file, README —
   exactly one authoring card each.
4. **Briefs are self-contained** (the gitignore constraint). No card may reference plans/ content.
5. **Every card has runnable verify_cmds.** No unverifiable cards.
6. **Student/instructor split is a plan-level property**: lab-solution content only ever appears in
   cards whose files_touched are under `materials/instructor/` or the `solutions` branch tasks.

## Reference
- The runner: `.claude/skills/workflow-execute/skill.md` (consumes this skill's `plan/` output).
- Course inputs: `plans/blueprint.md` (point-by-point spec), `plans/course-102-research-plan.md`
  (validated facts + corrections every card must honor).
- Origin: adapted from ticket-ocr's workflow pair (`~/repos/pocs/ticket-ocr/.claude/skills/`) — the
  DDL planner became `asset_plan.py`; migrations→shared assets, schema/consume→foundation/content.
