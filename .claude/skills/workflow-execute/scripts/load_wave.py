#!/usr/bin/env python3
"""load_wave.py — the RUNNER's card reader (the contract with /workflow-plan). Course-build edition.

Loads plan/tasks/*.card.yaml for one wave and emits the structured execution plan the master drives
from. It REUSES the planner's card loader (asset_plan.py:_load_cards) so the runner and planner parse
the identical schema — exactly one parser, never two that can drift.

Emits (text by default, --json for machine):
  - foundation_tasks / content_tasks  : split by card `phase` (foundation authors shared assets —
                                        contracts, skeletons, settings; content consumes them)
  - has_foundation                    : bool — the wave needs the foundation → barrier → content split
  - lock_groups                       : {resource:[ids]} from shared_resources (serialize these)
  - ordering_edges                    : card-id build order (creator → extender), parsed from
                                        plan/asset_conflict_report.md "## Ordering edges"
  - overlaps                          : files_touched ∩ across tasks (merge-conflict sites; a .html
                                        overlap usually means the FRAGMENT RULE was skipped — fix the
                                        plan, don't merge-wrestle one guide file)
  - merge_order                       : topo order of depends_on (master merges in this order)
  - verify_cmds[<id>]                 : that task's per-task verify commands
  - briefs[<id>]                      : the card's embedded task spec (fed into TRANSITION.md,
                                        because plans/ is gitignored and absent from worktrees)

Usage:  load_wave.py <plan-dir> --wave N [--json]
Exit:   0 ok · 2 UNSAFE (HARD CONFLICT unresolved, or a content card still carrying asset_intents)
        · 3 bad input.

A non-zero exit means /workflow-execute must NOT start the wave — fix the plan in /workflow-plan
first. This is the gate that stops a broken plan from reaching worktrees.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Reuse the planner's ONE card loader so planner+runner never drift on the schema.
_PLAN_LOADER = Path(__file__).resolve().parents[2] / "workflow-plan" / "scripts" / "asset_plan.py"


def _load_planner_module():
    spec = importlib.util.spec_from_file_location("asset_plan", _PLAN_LOADER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load planner card loader at {_PLAN_LOADER}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _wave_of(card: dict) -> int | None:
    w = card.get("wave")
    if w is None:
        return None
    try:
        return int(w)
    except (TypeError, ValueError):
        m = re.search(r"\d+", str(w))
        return int(m.group()) if m else None


def _toposort(ids: list[str], deps: dict[str, list[str]]) -> list[str]:
    """Stable topo order of ids by depends_on. Cycles → remaining appended in id order (the planner's
    human-curated waves already broke real cycles; this is a safety net)."""
    order: list[str] = []
    remaining = set(ids)
    while remaining:
        ready = sorted(i for i in remaining if all(d not in remaining for d in deps.get(i, [])))
        if not ready:
            order.extend(sorted(remaining))
            break
        order.extend(ready)
        remaining -= set(ready)
    return order


def _ordering_edges(plan_dir: Path, wave_ids: set[str]) -> list[tuple[str, str]]:
    """Parse asset_conflict_report.md "## Ordering edges" ("- A → B", card ids). The report is
    GLOBAL (all waves); keep only edges whose endpoints include a card of THIS wave."""
    report = plan_dir / "asset_conflict_report.md"
    edges: list[tuple[str, str]] = []
    if not report.exists():
        return edges
    in_section = False
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Ordering edges"):
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            m = re.match(r"\s*-\s*(.+?)\s*→\s*(.+?)\s*$", line)
            if m:
                pred, dep = m.group(1).strip(), m.group(2).strip()
                if pred in wave_ids or dep in wave_ids:
                    edges.append((pred, dep))
    return edges


def build_plan(plan_dir: Path, wave: int) -> tuple[dict, list[str]]:
    """Return (execution_plan, problems). problems non-empty ⇒ the wave is unsafe to run."""
    planner = _load_planner_module()
    tasks_dir = plan_dir / "tasks"
    if not tasks_dir.is_dir():
        return {}, [f"no tasks dir at {tasks_dir}"]
    try:
        all_cards = planner._load_cards(tasks_dir)
    except planner.CardParseError as e:
        return {}, [f"card parse failed (fail-closed): {e}"]

    cards = [c for c in all_cards if _wave_of(c) == wave]
    problems: list[str] = []
    if not cards:
        return {}, [
            f"no cards for wave {wave} (found waves: "
            f"{sorted({_wave_of(c) for c in all_cards if _wave_of(c) is not None})})"
        ]

    def cid(c):
        return planner._cid(c)

    foundation_tasks, content_tasks = [], []
    for c in cards:
        phase = str(c.get("phase", "content")).strip()
        (foundation_tasks if phase == "foundation" else content_tasks).append(cid(c))
        # INTEGRITY: a content card must NOT carry asset_intents (the planner should have folded them).
        if phase != "foundation" and planner._intents(c):
            problems.append(
                f"INTEGRITY: card {cid(c)} is phase=content but still declares asset_intents "
                f"{[i.get('object') for i in planner._intents(c)]} — re-run `asset_plan.py --apply` "
                f"to fold it onto a foundation owner before executing."
            )

    # If the planner left a HARD CONFLICT in the report, the wave is not safe to run.
    report = plan_dir / "asset_conflict_report.md"
    if report.exists() and "HARD CONFLICT" in report.read_text(encoding="utf-8"):
        problems.append(
            "HARD CONFLICT present in asset_conflict_report.md — reconcile in /workflow-plan "
            "(Gate 2) before /workflow-execute runs this wave."
        )

    lock_groups: dict[str, list[str]] = defaultdict(list)
    deps: dict[str, list[str]] = {}
    files_by_task: dict[str, list[str]] = {}
    for c in cards:
        i = cid(c)
        for lock in c.get("shared_resources") or []:
            lock = str(lock).strip()
            if lock and lock != "none":
                lock_groups[lock].append(i)
        deps[i] = [str(d).strip() for d in (c.get("depends_on") or [])]
        files_by_task[i] = [str(f).strip() for f in (c.get("files_touched") or [])]

    # overlaps: which files ≥2 tasks touch (merge-conflict sites the master must resolve)
    file_owners: dict[str, list[str]] = defaultdict(list)
    for t, fs in files_by_task.items():
        for f in fs:
            file_owners[f].append(t)
    overlaps = {f: sorted(ts) for f, ts in file_owners.items() if len(ts) > 1}

    wave_ids = {cid(c) for c in cards}
    plan = {
        "wave": wave,
        "foundation_tasks": sorted(foundation_tasks),
        "content_tasks": sorted(content_tasks),
        "has_foundation": bool(foundation_tasks),
        "lock_groups": {k: sorted(v) for k, v in lock_groups.items() if len(v) > 1},
        "ordering_edges": _ordering_edges(plan_dir, wave_ids),
        "overlaps": overlaps,
        "merge_order": _toposort([cid(c) for c in cards], deps),
        "verify_cmds": {cid(c): (c.get("verify_cmds") or []) for c in cards},
        "briefs": {cid(c): str(c.get("brief") or "") for c in cards},
    }
    return plan, problems


def _print_text(plan: dict, problems: list[str]) -> None:
    print(f"# Wave {plan.get('wave')} execution plan (from the cards)\n")
    if problems:
        print("## ❌ UNSAFE TO RUN — fix in /workflow-plan first")
        for p in problems:
            print(f"- {p}")
        print()
    print(f"foundation-phase tasks ({len(plan.get('foundation_tasks', []))}): {plan.get('foundation_tasks')}")
    print(f"content-phase tasks ({len(plan.get('content_tasks', []))}): {plan.get('content_tasks')}")
    print(f"has_foundation (barrier before content): {plan.get('has_foundation')}")
    if plan.get("lock_groups"):
        print("\nshared-resource lock groups (SERIALIZE within these):")
        for lock, ids in plan["lock_groups"].items():
            print(f"  {lock}: {ids}")
    if plan.get("ordering_edges"):
        print("\nordering edges (build predecessor BEFORE dependent):")
        for a, b in plan["ordering_edges"]:
            print(f"  {a}  →  {b}")
    if plan.get("overlaps"):
        print("\nfile overlaps (master resolves at merge — a .html overlap = fragment rule skipped):")
        for f, ts in plan["overlaps"].items():
            print(f"  {f}: {ts}")
    print(f"\nmerge order (depends_on topo): {plan.get('merge_order')}")


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    as_json = "--json" in argv
    wave = None
    if "--wave" in argv:
        i = argv.index("--wave")
        if i + 1 < len(argv):
            try:
                wave = int(argv[i + 1])
            except ValueError:
                wave = None
    if not args or wave is None:
        print("usage: load_wave.py <plan-dir> --wave N [--json]", file=sys.stderr)
        return 3
    plan_dir = Path(args[0])
    # accept either the plan/ dir or its parent (plans/<epic>/)
    if not (plan_dir / "tasks").is_dir() and (plan_dir / "plan" / "tasks").is_dir():
        plan_dir = plan_dir / "plan"
    if not plan_dir.is_dir():
        print(f"ERROR: {plan_dir} is not a plan directory", file=sys.stderr)
        return 3

    plan, problems = build_plan(plan_dir, wave)
    if not plan:
        for p in problems:
            print(f"ERROR: {p}", file=sys.stderr)
        return 3
    if as_json:
        print(json.dumps({"plan": plan, "problems": problems}, indent=2))
    else:
        _print_text(plan, problems)
    return 2 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
