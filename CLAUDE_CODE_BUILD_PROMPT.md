# Claude Code Build Prompt — Course 102 Materials

This file is the regenerability record for **Course 102 — Parallel Development**.
Pasting the prompt below into Claude Code rebuilds the 102 materials from an
empty slate. It documents HOW the course is built — deliverables, invariants,
wave order, and the four research corrections that form the course's factual
spine. It is documentation, not marketing.

---

## The prompt

Build the materials for "Course 102 — Parallel Development: Subagents,
Worktrees & Monorepos", a 180-minute follow-on to Course 101, inside the
course-templates repo. Produce every deliverable below, honoring every
invariant, in the stated wave order.

### Deliverables

- **A — Sample monorepo, two variants.** `sample-monorepo/python-fastapi/` and
  `sample-monorepo/node-express/`: each a self-initializing practice monorepo
  (`./init.sh`) with `contracts/`, `services/`, `specs/`, and `.claude/`
  settings, designed to be copied OUT of this repo before use.
- **B — Agent pack.** The subagent definitions and hooks the labs rely on,
  under the sample monorepo's `.claude/` (agents, per-agent PreToolUse
  write-scope hooks, settings).
- **C — Guide: skeleton + 11 fragments + assembly.**
  `materials/claude-code-102-guide.html` starts as a skeleton with one empty
  `<section>` per section id containing a `FRAGMENT-SLOT` comment. Eleven
  fragment files in `materials/fragments/<section-id>.html` (ids: intro,
  subagent-architecture, worktree-isolation, nested-claude-md, token-budget,
  parallel-implementation, contract-hooks, sparse-checkout, agent-teams,
  capstone, references) are written in parallel, then ONE assembler task
  stitches them into the guide verbatim.
- **D — Docs.** README "Course 102" section (materials map + 180-minute
  structure), QUICKSTART "102 prerequisites" section, `student_runbook.md`,
  and this build prompt.
- **E — Instructor materials.** `materials/instructor/`: lab solutions, demo
  capture transcripts, and timing notes. Students never receive these.

### Invariants

1. **Fragment rule.** Section authors write ONLY
   `materials/fragments/<section-id>.html`; exactly one assembler task edits
   the assembled guide. Fragments remain the source of truth after assembly —
   to change a section, edit its fragment and re-assemble; never hand-edit the
   assembled guide's section bodies.
2. **Student/instructor split.** Demos carry FULL solutions (commands, code,
   expected output). Labs carry NO solutions — only Easy/Hard tier callouts
   and a "You succeeded when…" checklist; solutions live only in
   `materials/instructor/`.
3. **101 house style.** Callouts use `callout callout-info|tip|warning` with a
   `callout-title` inner div; diagrams are `<div class="mermaid">` with exactly
   ONE div per diagram id (two-panel diagrams use mermaid `subgraph` blocks,
   never two divs); diagram-first teaching; no AI-tells in prose.

### Wave order

1. **Wave 0 — Foundations (frozen before anything runs in parallel):**
   contracts and schemas, monorepo skeletons and `.claude/` settings, the
   guide skeleton with its FRAGMENT-SLOT sections, and the fragment
   convention. Once frozen, no parallel task may modify them.
2. **Wave 1 — Mass parallel:** the 11 fragment tasks, the agent pack, and the
   docs task, each an atomic autonomous agent on its own worktree branch
   (`wf/c102/<task-id>`), committing on its branch without pushing or merging.
3. **Wave 2 — Integration:** real demo captures into `materials/captured/`,
   fragment assembly into the guide, instructor materials, and the final
   verify pass. The master merges all branches.

### The four research corrections (the course's factual spine)

1. **Subagent worktrees branch from the repo's DEFAULT branch, not the session
   HEAD.** A worktree spawned for a subagent is created from the default
   branch by default; if you want worktrees created from the current session
   HEAD, set `worktree.baseRef` to `"head"`. Every lab that layers subagent
   work on in-session commits depends on this setting.
2. **Agent Teams do NOT isolate teammates in worktrees.** Teammates share one
   working tree, so parallel safety comes from partitioning work by file
   ownership, not from filesystem isolation. Teams are also NOT locked to
   Opus 4.6 — Sonnet teammates are the recommended configuration.
3. **Write-scoping is a per-agent PreToolUse hook, not a permissions field.**
   Permission allowlists gate TOOLS, not paths; constraining WHERE an agent
   may write requires a PreToolUse hook that inspects the target path and
   denies out-of-scope writes.
4. **Token savings are MEASURED, never asserted.** Every savings claim in the
   materials comes from a before/after comparison of `/context` Memory-files
   deltas; the measured real-world range is 40–92%, and no number outside a
   capture may appear in the guide.

Build to the definition of done: every deliverable exists, every verify
command in the task cards passes, the fragment rule was never violated, and
the assembled guide renders with all 12 mermaid diagrams (D1–D11 plus the
capstone flow).
