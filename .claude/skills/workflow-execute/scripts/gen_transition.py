#!/usr/bin/env python3
"""gen_transition.py — write TRANSITION.md into each task worktree. Course-build edition.

Card-driven and generic (the ticket-ocr original hardcoded one epic's task table). For every card in
the target wave, finds the worktree at ../<repo>-<slug> and writes its TRANSITION.md: the agent's
complete, autonomous brief.

CRITICAL DESIGN POINT: `plans/` is GITIGNORED in this repo, so the plan directory does NOT exist
inside a task worktree (worktrees check out tracked files only). Therefore the card's `brief` field
must contain the FULL task spec, and this script EMBEDS it verbatim — the agent needs nothing outside
its worktree + this file.

Usage: gen_transition.py <plan-dir> --wave N [--plan-slug <slug>]
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

_PLAN_LOADER = Path(__file__).resolve().parents[2] / "workflow-plan" / "scripts" / "asset_plan.py"


def _planner():
    spec = importlib.util.spec_from_file_location("asset_plan", _PLAN_LOADER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RULES = """\
## Hard rules (read first — you are an ATOMIC, AUTONOMOUS build agent)
- You own exactly ONE task. This repo is a COURSE-TEMPLATES repo — it is **NOT an SDD/kryla repo**:
  no `/kryla.*` steps, no markers, no pipeline ceremony. Build → verify → commit.
- **Do NOT ask for human approval. Do NOT pause.** Everything you need is in THIS file — the task
  went through planning, asset-conflict analysis, and plan audit. Execute end-to-end and finish.
- **FRAGMENT RULE**: never edit `materials/claude-code-102-guide.html` (or any shared foundation
  asset: contracts/ schemas, sample-monorepo settings, README) unless YOUR card owns it via
  `asset_intents`. HTML section tasks write `materials/fragments/<section-id>.html`; one assembler
  task owns the guide.
- Course-quality bar: match the 101 house style (callouts `callout-info|tip|warning`, Easy/Hard lab
  tiers with "You succeeded when…", `<div class="mermaid">` diagrams, no AI-tells, diagram-first).
  Demos carry full solutions; labs carry NO solutions (those go only in instructor materials).
- If your task includes runnable code (scripts, hooks, sample services), verify it actually runs.
  Python via `.venv/bin/python3` if a venv exists, else `python3`. Run YOUR card's verify_cmds
  (below) before declaring green — a verify_cmd that fails means you are NOT done.
- **Commit** on THIS branch. Do **NOT** push. Do **NOT** merge — the master merges your branch.
- Touching a shared file your card lists is fine — the master resolves overlap at merge. Do not
  refactor unrelated files.
- When done, report: green/red, branch, files changed, verify_cmds run + their results, and any note
  the master needs for merging.
"""


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    wave = None
    if "--wave" in argv:
        i = argv.index("--wave")
        if i + 1 < len(argv):
            wave = int(argv[i + 1])
    plan_slug = None
    if "--plan-slug" in argv:
        i = argv.index("--plan-slug")
        if i + 1 < len(argv):
            plan_slug = argv[i + 1]
    if not args or wave is None:
        print("usage: gen_transition.py <plan-dir> --wave N [--plan-slug <slug>]", file=sys.stderr)
        return 3

    plan_dir = Path(args[0])
    if not (plan_dir / "tasks").is_dir() and (plan_dir / "plan" / "tasks").is_dir():
        plan_dir = plan_dir / "plan"
    planner = _planner()
    cards = planner._load_cards(plan_dir / "tasks")

    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    repo = root.name
    plan_slug = plan_slug or plan_dir.parent.name

    written = 0
    for c in cards:
        w = c.get("wave")
        try:
            w = int(re.search(r"\d+", str(w)).group()) if w is not None else None
        except AttributeError:
            w = None
        if w != wave:
            continue
        slug = planner._cid(c)
        wt = root.parent / f"{repo}-{slug}"
        if not wt.exists():
            print(f"!! worktree missing for {slug}: {wt} (run worktree.sh up first)", file=sys.stderr)
            continue
        brief = str(c.get("brief") or "").strip() or "(no brief on the card — STOP and report; the planner must fill `brief`)"
        verify = "\n".join(f"- `{v}`" for v in (c.get("verify_cmds") or [])) or "- (none declared)"
        files = "\n".join(f"- `{f}`" for f in (c.get("files_touched") or [])) or "- (none declared)"
        phase = str(c.get("phase", "content"))
        phase_rules = (
            "**FOUNDATION task**: you AUTHOR the shared asset(s) declared in your card's "
            "`asset_intents` — and ONLY those. Other tasks build against your output after the "
            "barrier; keep the interface exactly as the brief specifies."
            if phase == "foundation"
            else "**CONTENT task**: the foundations (contracts, skeletons, settings) are FROZEN on "
            "your base branch. Build against them. Do NOT create or modify a shared foundation "
            "asset; if one is missing or wrong, STOP and report — never fix it yourself."
        )
        content = f"""# TRANSITION — {slug}  (Wave {wave}, section {c.get('section', '?')})

You are the build agent for **{slug} — {c.get('title', '')}**. Work ONLY inside this worktree:
`{wt}` (branch `wf/{plan_slug}/{slug}`).

{RULES}

## Your phase
{phase_rules}

## Files you are expected to touch
{files}

## Verify commands (run ALL before reporting green)
{verify}

## YOUR TASK (complete spec — plans/ does not exist in this worktree; this is everything)
{brief}

## Definition of done
Every deliverable in the brief exists, every verify command passes, the fragment rule is honored,
and your work is committed on this branch. Then report back to the master. Do not push, do not
merge, do not ask for approval.
"""
        (wt / "TRANSITION.md").write_text(content, encoding="utf-8")
        written += 1
        print(f"✓ {slug}: TRANSITION.md ({len(brief)} chars of brief)")
    print(f"\n{written} transition files written for wave {wave}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
