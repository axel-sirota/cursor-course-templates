# Final Review Report — Course 102 (w2-i05)

Reviewed: student guide, instructor edition (rebuilt twice), 11 fragments, 9 solution
files, sample-monorepo (python-fastapi + node-express), README, QUICKSTART, captured
demo outputs. Fragments were treated as the source of truth; every fragment edit was
mirrored into `materials/claude-code-102-guide.html`, and the instructor edition was
rebuilt from the updated guide as the last step.

## Routed fixes R1–R4 — all applied

| Fix | Where | Status |
|-----|-------|--------|
| R1 — /context Memory-Files blind-spot sentence | Lab 3 Hard (`fragments/nested-claude-md.html`) and Lab 4 Hard (`fragments/token-budget.html`), mirrored in the guide | DONE |
| R2 — Lab 2 Hard clone instruction (`git clone ~/labs/refund-monorepo lab2-clone`; no-remote fallback of baseRef "fresh") | `fragments/worktree-isolation.html`, mirrored in the guide | DONE |
| R3 — intro h2 numbered "1." to match sidebar ("1. Introduction") and 101 house style | `fragments/intro.html`, guide line 445; sidebar and mobile TOC already numbered | DONE |
| R4 — Lab 8 success criterion reworded: default (Easy-tier) teammates have team tools and do peer-message; only restricted implementer-definition teammates relay via the lead | `fragments/agent-teams.html`, mirrored in the guide | DONE |

All four fixes verified present in the rebuilt instructor edition.

## Lens 1 — Technical accuracy

Fixed in place (4):

1. **Quoted command lines drifted from the shipped file** (`/implement-across-services`):
   the guide quoted `CRITICAL: run these…` unbolded/lowercase and compressed the merge
   phase into a single invented line. Replaced both with the as-shipped text from
   `sample-monorepo/python-fastapi/.claude/commands/implement-across-services.md`
   (`**CRITICAL**: Run these…` and the full `**4. MERGE PHASE**` bullet block).
   Severity: medium (students grep for these lines).
2. **Catchup described as "four steps"; the shipped `catchup.md` runs five** (summarize
   and declare-loaded-memory are separate steps). Guide + fragment now list five steps
   matching the shipped command, including the empty-diff fallback condition.
   Severity: medium.
3. **Unsourced savings assertion** — "Published real-world savings … range from 40% to
   92%" replaced with the course's own measured number (68.6% Memory-files reduction,
   captured in Demo 4). Savings are now measured everywhere, never asserted.
   Severity: medium.
4. **Instructor edition's 101-guide reference link was broken** — `claude-code-guide.html`
   resolved one directory too deep from `materials/instructor/`. Build script now
   rewrites it to `../claude-code-guide.html`. Severity: low.

Verified correct, no change needed:

- Worktree gotcha: default worktrees branch from the repo default branch; the
  `worktree.baseRef: "head"` fix is documented, shipped in both variants'
  `settings.json`, and proven in Demo 2 / Lab 2 / the Lab 2 solution.
- 2.1.218 live observations honored: worktree auto-cleanup non-occurrence is caveated
  in both the concept text and Demo 2 (and the Lab 2 solution teaches "check, then
  clean"); the lazy-load /context blind spot is caveated in section 5 and Demo 4, now
  reinforced in both lab Hard tiers via R1.
- Agent Teams: "Teams do not isolate teammates in worktrees" warning callout present;
  not Opus-locked ("not tied to any model", Sonnet recommended and used); the
  restricted-definition relay observation (31 lead↔teammate messages, no peer
  messages) is in Demo 8, the instructor Demo-8 notes, and the Lab 8 solution; default
  teammates peer-messaging now stated via R4 and demonstrated in the Lab 8 Easy
  reference run (4 peer messages).
- Write-scoping: framed as per-agent `PreToolUse` hooks throughout; "allowlists gate
  tools, not paths" stated verbatim in Lab 1 Easy and the warning callout.
- Exact key names verified everywhere: `worktree.sparsePaths`, `worktree.baseRef`,
  `symlinkDirectories`, `claudeMdExcludes`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`
  (no snake_case variants anywhere).
- Reference URLs: all nine `code.claude.com/docs/en/{sub-agents, worktrees,
  large-codebases, agent-teams, agents, memory, context-window, costs, hooks}` exact;
  ref-10 is the relative 101-guide link (correct in the student guide, now corrected
  in the instructor edition).
- Canonical blocks vs shipped files: payments-implementer `PreToolUse` (matcher
  `Edit|Write`, `path_guard.py services/payments`) and `Stop`
  (`validate.sh services/payments`) blocks match
  `sample-monorepo/python-fastapi/.claude/agents/payments-implementer.md`
  byte-for-byte on the load-bearing lines; command-file quotes reconciled (item 1).
- Sample-monorepo consistency: ports 8000/8001/8002 identical across both variants;
  `.worktreeinclude` ships `.env`; `.gitignore` ships `.claude/worktrees/`; node
  variant ships `baseRef: "head"` + `symlinkDirectories: ["node_modules"]` and a root
  `package.json` with `"workspaces": ["services/*"]` — all as the guide claims.
  `contracts/validate.py` exists (Lab 6 Hard's target). Demo 8 fragment quotes match
  `materials/captured/demo8-team-transcript.txt` verbatim.

Needs-human (2, minor):

- The intro motivation diagram's token figures (20k/25k/15k vs 8k/9k/7k) are
  illustrative, not captured measurements. It reads as a schematic and the measured
  claim arrives in Demo 4, but if the "never asserted" bar is applied strictly, the
  labels could be reworded to ranges or marked illustrative.
- Two doc-cited quantitative claims — the SubagentStop 8-block cap (ref-9) and the
  "team ≈ 7× a single session" cost figure (ref-8) — carry citations but were not
  re-verified against the live docs in this offline pass.

## Lens 2 — Pedagogy & consistency

- **Timing adds up**: 15+10+10+10+10+25+15+10+30+35+10 = 180. README's block table
  (15/40/80/35/10) sums to 180 and maps exactly onto the per-section minutes. The
  instructor edition now carries a timing tag on all 11 sections — R3's numbering
  change had silently dropped the intro's 15-min tag (build script keyed the intro on
  being unnumbered); fixed in the build script and rebuilt. [fixed]
- **Lab structure**: all 9 labs have Easy + Hard + "You succeeded when". Two house-style
  deviations fixed: Lab 1's success line was unbolded plain text; Lab 5's was wrapped
  in a callout-tip instead of the standard paragraph. Both normalized in fragment +
  guide. [fixed]
- **No solution leakage**: zero `callout-solution` / solution text in the student
  guide; solutions exist only under `materials/instructor/`. [verified]
- **Demos**: all 8 demos embed real captured output (no placeholder markers found);
  11 capture files shipped in `materials/captured/`. The only "placeholder" hit is an
  unused `.screenshot-placeholder` CSS rule inherited from the 101 template — cosmetic,
  left in place for template parity. [verified / noted]
- **Cross-file consistency**: service names, paths, init.sh flow, per-service
  requirements, and npm-workspaces install instructions agree across both monorepo
  variants, both guides, README, and QUICKSTART. QUICKSTART's 2.1.203 Bash-confinement
  prerequisite matches the guide's worktree section. [verified]
- **Part 1.5**: the spec's `## Part 1.5 — your turn (Demo 5 / Lab 5)` is referenced
  correctly in Demo 5 and Lab 5; Part 2 is correctly fenced to the teams lab. [verified]

## Lens 3 — AI-tell sweep

Grep sweep (delve, seamlessly, robust, comprehensive, "important to note", "worth
noting", leverage, crucial, furthermore, moreover, "in conclusion", "dive/deep dive"
filler) over the student guide, all fragments, instructor additions, and all 9
solution files: **zero hits**. No lines with 3+ em-dashes, no empty headers, no
over-bulleted sections found. Solutions read direct and concrete
(instructor-to-engineer), with real run economics and observed deviations. No fixes
required under this lens.

## Build verification

- Instructor edition rebuilt after all Phase 1 + Phase 3 edits.
- `instructor edition` banner present; 10 `callout-solution` blocks (9 lab solutions
  + Demo-8 run notes) ≥ 9; no `FRAGMENT-SLOT`; 11 timing tags summing to 180 min;
  101-guide link relative-correct.

Verdict: READY
