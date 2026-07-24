#!/usr/bin/env python3
"""asset_plan.py — plan-time SHARED-ASSET conflict planner for the course-build workflow pair.

Course-build adaptation of ticket-ocr's ddl_plan.py. The collision class in a course repo is not SQL
migrations but SHARED DELIVERABLE FILES: two parallel worktree tasks both authoring
materials/claude-code-102-guide.html, sample-monorepo/.claude/settings.json, a contracts/ schema, or
README.md. Each card declares its `asset_intents` (which shared assets it authors); this planner
builds a per-asset owner map and applies 3 rules:

  1. FOLD  — ≥2 cards author the same asset → ONE owner keeps it (the card stays/becomes
             phase: foundation), the other cards' intents move onto the owner and they flip to
             phase: content (they consume the asset). --apply rewrites the cards.
  2. HARD  — ≥2 cards declare `create` of the SAME asset with contradictory `details`
             (two different skeletons for one file) → HARD CONFLICT → report + exit 2. --apply
             refuses to fold while a HARD CONFLICT is present; the human reconciles first.
  3. ORDER — a card `extend`s an asset another card `create`s → ordering edge creator-card →
             extender-card (build the creator first; the extender bases on its merged result).

THE FRAGMENT RULE (the big one for this repo): the HTML guide is ONE file with ~11 sections.
Parallel section tasks must NOT each edit the guide — they write materials/fragments/<id>.html and
ONE assembler card owns the guide file. This planner FLAGS (as a fold) any case where ≥2 cards list
the same .html in `asset_intents`; the fix is usually "fragment + assembler", not raw folding.

Card schema (course v2) — plan/tasks/<id>.card.yaml:
  id: w1-c03            # stable, wave-prefixed
  title: "HTML section: nested CLAUDE.md"
  type: content         # content | code | diagram | docs
  priority: P0          # P0 | P1 | P2
  section: C-html-guide # deliverable (A-monorepo | B-agent-pack | C-html-guide | D-docs | E-buildprompt)
  files_touched: [materials/fragments/nested-claude-md.html]   # real paths; prefix new files "new:"
  shared_resources: []  # coarse locks (rarely needed once fragments are used) | none
  depends_on: []        # other card ids
  wave: 1
  phase: content        # foundation = authors a shared asset | content = consumes frozen foundations
  verify_cmds: ["grep -q 'id=\"nested-claude-md\"' materials/fragments/nested-claude-md.html"]
  human_owner: axel
  brief: |              # the FULL task spec — embedded verbatim into the worktree TRANSITION.md,
    ...                 # because plans/ is gitignored and does NOT exist inside task worktrees.
  # foundation-phase ONLY:
  asset_intents:
    - object: materials/claude-code-102-guide.html
      operation: create        # create | extend
      details: {kind: html-skeleton, sections: 11}

Usage:  asset_plan.py <plan/tasks-dir> [--apply]
Exit:   0 ok · 2 HARD CONFLICT present · 3 bad input.
Output: plan/asset_conflict_report.md (next to the tasks/ dir) with an "## Ordering edges" section
        formatted "- <card-id> → <card-id>" (load_wave.py parses exactly this).
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


class CardParseError(Exception):
    pass


# ---- card loader (shared with load_wave.py — exactly ONE parser) -----------------------------

def _unquote(s: str) -> str:
    """Strip exactly ONE matching outer quote pair. Never use str.strip("'\\"") here — it eats a
    trailing shell quote (e.g. the closing ' of `sh -c '...'`) and silently corrupts verify_cmds.
    Double-quoted YAML scalars also get their backslash-escapes resolved (\\" -> ")."""
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        body = s[1:-1]
        if s[0] == '"':
            body = body.replace('\\"', '"').replace("\\\\", "\\")
        return body
    return s


def _tiny_yaml(text: str, fname: str = "?") -> dict:
    """Minimal fallback parser for the card subset when pyyaml is absent: scalars, flat lists
    ("- item"), one level of list-of-dicts (asset_intents), and a literal block (brief: |).
    Fail-closed on anything it can't parse."""
    data: dict = {}
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if line.startswith((" ", "\t")):
            raise CardParseError(f"{fname}: unexpected indent at line {i + 1} (install pyyaml)")
        if ":" not in line:
            raise CardParseError(f"{fname}: not key:value at line {i + 1}")
        key, _, rest = line.partition(":")
        key, rest = key.strip(), rest.strip()
        if rest == "|":  # literal block
            block, i = [], i + 1
            while i < n and (not lines[i].strip() or lines[i].startswith("  ")):
                block.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            data[key] = "\n".join(block).rstrip("\n")
            continue
        if rest:  # inline scalar / inline list
            if rest.startswith("[") and rest.endswith("]"):
                inner = rest[1:-1].strip()
                data[key] = [_unquote(s) for s in inner.split(",") if s.strip()] if inner else []
            else:
                data[key] = _unquote(rest)
            i += 1
            continue
        # block list (flat or list-of-dicts)
        items: list = []
        i += 1
        while i < n and lines[i].startswith("  -"):
            item_line = lines[i].strip()[1:].strip()
            if ":" in item_line and not item_line.startswith(("'", '"')):
                d: dict = {}
                k2, _, v2 = item_line.partition(":")
                d[k2.strip()] = _unquote(v2)
                i += 1
                while i < n and lines[i].startswith("    ") and ":" in lines[i]:
                    k3, _, v3 = lines[i].strip().partition(":")
                    v3 = v3.strip()
                    if v3.startswith("{") and v3.endswith("}"):
                        dd = {}
                        for pair in v3[1:-1].split(","):
                            if ":" in pair:
                                pk, _, pv = pair.partition(":")
                                dd[pk.strip()] = _unquote(pv)
                        d[k3.strip()] = dd
                    else:
                        d[k3.strip()] = _unquote(v3)
                    i += 1
                items.append(d)
            else:
                items.append(_unquote(item_line))
                i += 1
        data[key] = items
    return data


def _load_cards(tasks_dir: Path) -> list[dict]:
    cards = []
    for f in sorted(tasks_dir.glob("*.card.yaml")):
        text = f.read_text(encoding="utf-8")
        if yaml is not None:
            try:
                data = yaml.safe_load(text) or {}
            except Exception as e:
                raise CardParseError(f"{f.name}: {e}") from e
        else:
            data = _tiny_yaml(text, f.name)
        if not isinstance(data, dict) or not data.get("id"):
            raise CardParseError(f"{f.name}: no id")
        data["_path"] = str(f)
        cards.append(data)
    return cards


def _cid(card: dict) -> str:
    return str(card.get("id", "?")).strip()


def _intents(card: dict) -> list[dict]:
    out = []
    for it in card.get("asset_intents") or []:
        if isinstance(it, dict) and str(it.get("object", "")).strip():
            out.append(it)
    return out


# ---- the 3-rule analysis ---------------------------------------------------------------------

def analyze(cards: list[dict]) -> dict:
    """Return {owners, folds, hard_conflicts, ordering_edges}."""
    by_object: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for c in cards:
        for it in _intents(c):
            by_object[str(it["object"]).strip()].append((_cid(c), it))

    owners: dict[str, str] = {}
    folds: list[dict] = []
    hard: list[str] = []
    edges: list[tuple[str, str]] = []

    for obj, pairs in sorted(by_object.items()):
        creators = [(cid, it) for cid, it in pairs if str(it.get("operation", "create")) == "create"]
        extenders = [(cid, it) for cid, it in pairs if str(it.get("operation")) == "extend"]

        # Rule 2 — contradictory creates
        if len(creators) > 1:
            details = {str(it.get("details", {})) for _, it in creators}
            if len(details) > 1:
                hard.append(
                    f"HARD CONFLICT on `{obj}`: cards {sorted(c for c, _ in creators)} each `create` "
                    f"it with different details — reconcile ONE skeleton/owner by hand."
                )
                continue

        # Rule 1 — one owner per asset
        if len(pairs) > 1:
            owner = creators[0][0] if creators else sorted(c for c, _ in pairs)[0]
            owners[obj] = owner
            losers = sorted({cid for cid, _ in pairs} - {owner})
            folds.append({"object": obj, "owner": owner, "folded": losers})
            # Rule 3 for the losers that extend
            for cid, it in extenders:
                if cid != owner:
                    edges.append((owner, cid))
        else:
            owners[obj] = pairs[0][0]
            # Rule 3 — a lone extender of an object someone else creates in another card
            if extenders and not creators:
                pass  # extend with no creator in plan → the asset must already exist on base; fine.

    # Rule 3 across objects: extend-edges when creator and extender are different cards
    for obj, pairs in by_object.items():
        creator_ids = [cid for cid, it in pairs if str(it.get("operation", "create")) == "create"]
        for cid, it in pairs:
            if str(it.get("operation")) == "extend" and creator_ids and cid not in creator_ids:
                for cr in creator_ids:
                    if (cr, cid) not in edges:
                        edges.append((cr, cid))

    return {"owners": owners, "folds": folds, "hard_conflicts": hard, "ordering_edges": edges}


def apply_folds(cards: list[dict], analysis: dict) -> list[str]:
    """Rewrite cards: the owner keeps/gains phase foundation + all intents for its objects; folded
    cards lose those intents and flip to content if nothing remains. Refuses under HARD CONFLICT."""
    if analysis["hard_conflicts"]:
        return ["REFUSED --apply: HARD CONFLICT present — reconcile first, then re-run."]
    actions: list[str] = []
    by_id = {_cid(c): c for c in cards}
    for fold in analysis["folds"]:
        obj, owner_id = fold["object"], fold["owner"]
        owner = by_id[owner_id]
        moved = []
        for lid in fold["folded"]:
            loser = by_id[lid]
            keep, move = [], []
            for it in _intents(loser):
                (move if str(it["object"]).strip() == obj else keep).append(it)
            if move:
                loser["asset_intents"] = keep
                owner.setdefault("asset_intents", [])
                owner["asset_intents"].extend(move)
                moved.append(lid)
            if not keep:
                loser["phase"] = "content"
                loser.pop("asset_intents", None)
        owner["phase"] = "foundation"
        actions.append(f"folded `{obj}` → owner {owner_id} (from {moved}); losers → content")
    # write back
    if yaml is None:
        actions.append("WARN: pyyaml absent — cards NOT rewritten; apply the folds by hand.")
        return actions
    for c in cards:
        p = Path(c.pop("_path"))
        p.write_text(yaml.safe_dump(c, sort_keys=False, allow_unicode=True), encoding="utf-8")
        c["_path"] = str(p)
    return actions


def write_report(plan_dir: Path, analysis: dict, actions: list[str]) -> Path:
    lines = ["# Asset conflict report (asset_plan.py)", ""]
    if analysis["hard_conflicts"]:
        lines.append("## HARD CONFLICT")
        lines += [f"- {h}" for h in analysis["hard_conflicts"]]
        lines.append("")
    lines.append("## Asset owners (one owner per shared asset)")
    lines += [f"- `{o}` → {c}" for o, c in sorted(analysis["owners"].items())] or ["- (none declared)"]
    lines.append("")
    if analysis["folds"]:
        lines.append("## Folds (multi-author assets folded to one owner)")
        lines += [f"- `{f['object']}`: owner {f['owner']}, folded {f['folded']}" for f in analysis["folds"]]
        lines.append("")
    lines.append("## Ordering edges")
    lines += [f"- {a} → {b}" for a, b in analysis["ordering_edges"]] or ["- (none)"]
    lines.append("")
    if actions:
        lines.append("## --apply actions")
        lines += [f"- {a}" for a in actions]
        lines.append("")
    out = plan_dir / "asset_conflict_report.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    do_apply = "--apply" in argv
    if not args:
        print("usage: asset_plan.py <plan/tasks-dir> [--apply]", file=sys.stderr)
        return 3
    tasks_dir = Path(args[0])
    if tasks_dir.name != "tasks" and (tasks_dir / "tasks").is_dir():
        tasks_dir = tasks_dir / "tasks"
    if not tasks_dir.is_dir():
        print(f"ERROR: {tasks_dir} is not a directory", file=sys.stderr)
        return 3
    try:
        cards = _load_cards(tasks_dir)
    except CardParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    if not cards:
        print(f"no .card.yaml files in {tasks_dir}", file=sys.stderr)
        return 3

    analysis = analyze(cards)
    actions = apply_folds(cards, analysis) if do_apply else []
    report = write_report(tasks_dir.parent, analysis, actions)
    print(f"report → {report}")
    for h in analysis["hard_conflicts"]:
        print(h, file=sys.stderr)
    if yaml is None:
        print("ℹ pyyaml not available — fallback parser used; install pyyaml for canonical parsing.",
              file=sys.stderr)
    return 2 if analysis["hard_conflicts"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
