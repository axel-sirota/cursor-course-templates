#!/usr/bin/env python3
"""ddl_plan.py — the SEMANTIC DDL PLANNER for /workflow-plan (the crown jewel of the skill pair).

Reads the wave's task cards (plan/tasks/*.card.yaml), builds a per-object OPERATION TIMELINE across
all cards' `ddl_intents`, and applies 5 conflict rules (converged via the Opus×codex-o3 GAN — see
docs/researches/workflow-skill-pair-design.md). Catches the Wave-1 migration-collision class AT PLAN
TIME, before any worktree forks — which simple object-name set-intersection could not.

The 5 rules:
  1. Multiple ops/cards on ONE object → FOLD into ONE ordered schema-owner card (the others become
     `consume`). With --apply this REWRITES the card files; without it, it only reports the fold.
  2. Type / nullability / default / length disagreement on the same object → HARD CONFLICT, halt.
  3. rename X→Y → flag every card still referencing X (object, fk_target, OR default SQL) + an
     ordering edge X→Y, and list the consumer cards whose reference must be rewritten.
  4. create_enum then a column using that enum → ordering edge.
  5. fk_target OR a default that references another created object (fk, nextval('seq'), an enum cast)
     → ordering edge target→op (the FK-to-a-table-created-this-wave class — Alembic dies "relation
     does not exist" under parallel apply).

Usage:
  ddl_plan.py <tasks-dir>            # analyse; write ddl_conflict_report.md next to tasks/
  ddl_plan.py <tasks-dir> --apply    # ALSO fold multi-owner objects → rewrite the loser cards to
                                     # `consume` and assign one schema-owner (mutates *.card.yaml)
Exit:
  0 = no conflicts / cleanly folded · 2 = HARD CONFLICT or un-foldable (human must reconcile) ·
  3 = bad input / a ddl_intents card whose details could not be parsed (fail-closed — never green
      on a degraded parse, else an unsafe plan would pass).

This script reasons over DECLARED intent — it writes no migrations and touches no DB. It is the
PLAN-time guard; the runner's migration_reconcile.py is the runtime LAST-RESORT backstop.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # we fall back to a tiny parser below


# ---- minimal card loader (works even without pyyaml) -------------------------------------------
class CardParseError(Exception):
    """A card with ddl_intents whose `details` could not be parsed — must fail closed, not green."""


def _load_cards(tasks_dir: Path) -> list[dict]:
    cards = []
    for f in sorted(tasks_dir.glob("*.card.yaml")):
        text = f.read_text(encoding="utf-8")
        if yaml is not None:
            data = yaml.safe_load(text) or {}
        else:
            data = _tiny_yaml(text, f.name)
        data["__file"] = f.name
        cards.append(data)
    return cards


def _coerce_scalar(v: str):
    """Type a bare YAML scalar: bools, ints, null, quoted strings, inline [lists]."""
    s = v.strip()
    if s == "" or s in ("~", "null", "None"):
        return None
    low = s.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_coerce_scalar(x) for x in _split_top_commas(inner)]
    if s.startswith("{") and s.endswith("}"):
        return _parse_inline_map(s)
    if (s[0] == s[-1]) and s[0] in ("'", '"') and len(s) >= 2:
        return s[1:-1]
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _split_top_commas(s: str) -> list[str]:
    """Split on commas that are NOT inside nested [], {}, or quotes."""
    parts, depth, q, buf = [], 0, "", []
    for ch in s:
        if q:
            buf.append(ch)
            if ch == q:
                q = ""
            continue
        if ch in ("'", '"'):
            q = ch
            buf.append(ch)
        elif ch in "[{":
            depth += 1
            buf.append(ch)
        elif ch in "]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return [p for p in parts]


def _parse_inline_map(s: str) -> dict:
    """Parse an inline `{k: v, k2: v2}` map (the form `details:` uses in the card schema)."""
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    out: dict = {}
    for pair in _split_top_commas(s):
        if ":" not in pair:
            continue
        k, v = pair.split(":", 1)
        out[k.strip().strip("'\"")] = _coerce_scalar(v)
    return out


def _tiny_yaml(text: str, fname: str = "?") -> dict:
    """Last-resort parser for the SUBSET of YAML our cards use: flat scalars + the ddl_intents list
    of {object, operation, details:{...}} maps. Prefer pyyaml; this only exists so the planner runs
    in a bare env. It FULLY parses the inline `details` map (so Rules 2/4/5 are not degraded) and
    raises CardParseError if a ddl_intents card has a `details:` it cannot parse → fail-closed."""
    out: dict = {"ddl_intents": []}
    cur_intent: dict | None = None
    in_intents = False
    saw_ddl_intent = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("ddl_intents:"):
            in_intents = True
            continue
        if in_intents:
            stripped = line.strip()
            if stripped.startswith("- object:"):
                if cur_intent:
                    out["ddl_intents"].append(cur_intent)
                cur_intent = {"object": _coerce_scalar(stripped.split(":", 1)[1])}
                saw_ddl_intent = True
            elif cur_intent is not None and stripped.startswith(("operation:", "details:")):
                k, v = stripped.split(":", 1)
                key = k.strip()
                if key == "details":
                    parsed = _parse_inline_map(v) if v.strip() else {}
                    if v.strip() and not parsed:
                        raise CardParseError(
                            f"{fname}: could not parse `details:` ({v.strip()!r}). Install pyyaml "
                            f"for full analysis — refusing to green a degraded plan."
                        )
                    cur_intent["details"] = parsed
                else:
                    cur_intent[key] = _coerce_scalar(v)
            elif not line.startswith(" "):  # dedented → intents block ended
                in_intents = False
                if cur_intent:
                    out["ddl_intents"].append(cur_intent)
                    cur_intent = None
        if not in_intents and ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = _coerce_scalar(v)
    if cur_intent:
        out["ddl_intents"].append(cur_intent)
    # A card declaring ddl_intents but every intent missing `details` while a `details:` token was
    # present is suspicious — but the per-line raise above already fail-closes the real degrade case.
    _ = saw_ddl_intent
    return out


def _intents(card: dict) -> list[dict]:
    return card.get("ddl_intents") or []


def _details(intent: dict) -> dict:
    d = intent.get("details")
    return d if isinstance(d, dict) else {}


def _cid(card: dict) -> str:
    return str(card.get("id", card.get("__file", "?")))


# ---- the 5 rules -------------------------------------------------------------------------------
def analyse(cards: list[dict]) -> tuple[list[str], list[str], dict, dict]:
    """Return (hard_conflicts, warnings, ordering_edges, folds).
    hard_conflicts ⇒ exit 2. folds maps object → {owner, losers} for --apply to rewrite."""
    hard: list[str] = []
    warn: list[str] = []
    edges: dict[str, set[str]] = defaultdict(set)  # object -> objects that must precede it
    folds: dict[str, dict] = {}  # object -> {"owner": cid, "losers": [cid,...]}

    # object -> list of (card_id, operation, details)
    timeline: dict[str, list[tuple[str, str, dict]]] = defaultdict(list)
    created_objects: set[str] = set()
    for c in cards:
        cid = _cid(c)
        for it in _intents(c):
            obj = str(it.get("object", "")).strip()
            op = str(it.get("operation", "")).strip()
            timeline[obj].append((cid, op, _details(it)))
            if op in ("create_table", "create_enum"):
                created_objects.add(obj)

    # Rule 1 — multiple cards touching one object → FOLD to one schema-owner
    for obj, ops in timeline.items():
        cards_for_obj = [cid for cid, _, _ in ops]
        distinct = sorted(set(cards_for_obj))
        if len(distinct) > 1:
            # owner = the card that CREATES the object if one exists, else the first by id (stable).
            creators = [cid for cid, op, _ in ops if op in ("create_table", "create_enum", "add")]
            owner = sorted(creators)[0] if creators else distinct[0]
            losers = [c for c in distinct if c != owner]
            folds[obj] = {"owner": owner, "losers": losers}
            warn.append(
                f"RULE 1 (multi-owner): object '{obj}' is touched by {len(distinct)} cards "
                f"{distinct} ({[op for _, op, _ in ops]}). FOLD → schema-owner '{owner}'; "
                f"{losers} become `consume`. (--apply rewrites the cards.)"
            )

    # Rule 2 — IRRECONCILABLE shape disagreement on the SAME object → HARD CONFLICT.
    # The GAN drew a sharp line (gan_c3 rows): an ADD-nullable→ALTER-NOT-NULL SEQUENCE is NOT a
    # clash — it's a legitimate expand/contract timeline that Rule 1 FOLDS into one ordered owner.
    # A clash is when the shape genuinely cannot be sequenced:
    #   • `type` disagreement across ANY two defining ops (int4 vs bigint) — irreconcilable; you
    #     can't have two authors silently pick different column types. HARD always.
    #   • `nullable`/`default`/`length`/precision disagreement among ops of the SAME KIND (≥2 `add`,
    #     or ≥2 `alter`) — two same-stage authors contradict each other. HARD.
    #   An add/alter MIX differing only on nullable/default is a sequence → left to Rule 1's fold.
    for obj, ops in timeline.items():
        defs = [(op, d) for _, op, d in ops if op in ("add", "alter", "create_table") and d]
        cids = sorted({cid for cid, _, _ in ops})
        # type: clash across any defining ops
        types = {_norm(d["type"]) for op, d in defs if d.get("type") is not None}
        if len(types) > 1:
            hard.append(
                f"RULE 2 (type clash): object '{obj}' declared with conflicting type "
                f"{sorted(map(str, types))} across {cids}. Irreconcilable — the human must pick the "
                f"intended type before waves freeze."
            )
        # nullable/default/length: clash only WITHIN the same operation kind (same-stage contradiction)
        for field in ("nullable", "default", "length", "precision", "scale"):
            for kind in ("add", "alter", "create_table"):
                vals = {
                    _norm(d[field]) for op, d in defs if op == kind and d.get(field) is not None
                }
                if len(vals) > 1:
                    hard.append(
                        f"RULE 2 ({field} clash): object '{obj}' has ≥2 `{kind}` ops declaring "
                        f"conflicting {field} {sorted(map(str, vals))} across {cids}. Two same-stage "
                        f"authors contradict — the human must reconcile before waves freeze."
                    )

    # Rule 3 — rename X→Y → ordering edge + flag every card still referencing X (obj/fk/default)
    renamed: dict[str, tuple[str, str]] = {}  # old -> (new, owner_cid)
    for obj, ops in timeline.items():
        for cid, op, d in ops:
            if op == "rename":
                old = str(d.get("from") or obj).strip()
                new = str(d.get("to") or d.get("new") or "").strip()
                if new:
                    renamed[old] = (new, cid)
                    edges.setdefault(new, set()).add(
                        old
                    )  # the rename must precede consumers of new
    for old, (new, owner) in renamed.items():
        for c in cards:
            cid = _cid(c)
            for it in _intents(c):
                if it.get("operation") == "rename":
                    continue
                if _references(it, old):
                    warn.append(
                        f"RULE 3 (rename): '{old}' → '{new}' (card {owner}), but card {cid} still "
                        f"references '{old}' (object/fk_target/default). Rewrite that reference to "
                        f"'{new}'."
                    )

    # Rule 4 — create_enum then a column USING that enum → ordering edge
    for obj, ops in timeline.items():
        for cid, op, d in ops:
            etype = str(d.get("type", "") or "")
            if op in ("add", "alter", "create_table") and etype and etype in created_objects:
                edges[obj].add(etype)
                warn.append(
                    f"RULE 4 (enum order): {cid} adds '{obj}' using enum '{etype}' — the enum must "
                    f"be created first. Ordering edge {etype} → {obj}."
                )

    # Rule 5 — fk_target OR default referencing another created object → ordering edge target→op
    for obj, ops in timeline.items():
        for cid, op, d in ops:
            for ref in _referenced_objects(d):
                ref_table = ref.split(".")[0]
                if (
                    ref_table
                    and ref_table != obj.split(".")[0]
                    and any(ref_table == o.split(".")[0] for o in created_objects)
                ):
                    edges[obj].add(ref_table)
                    warn.append(
                        f"RULE 5 (ref order): {cid}'s '{obj}' references '{ref}' (fk/default), and "
                        f"its target '{ref_table}' is created THIS wave. Ordering edge "
                        f"{ref_table} → {obj} (else Alembic 'relation does not exist' under "
                        f"parallel apply)."
                    )

    return hard, warn, {k: sorted(v) for k, v in edges.items()}, folds


def _norm(v) -> str:
    """Normalise a scalar for clash comparison (case/whitespace-insensitive)."""
    if isinstance(v, bool):
        return str(v).lower()
    return str(v).strip().lower()


def _references(intent: dict, name: str) -> bool:
    """Does this intent reference `name` anywhere (object, fk_target, or default SQL text)?"""
    if str(intent.get("object", "")).strip() == name:
        return True
    return name in _referenced_objects(intent.get("details") or intent, raw=True)


def _referenced_objects(details: dict, raw: bool = False):
    """Objects this DDL points at via fk_target or a default expression.
    fk_target → the referenced table.column; default `nextval('x_seq')`/`'val'::enum_t` → x_seq/enum_t.
    With raw=True returns the joined text (for substring membership in _references)."""
    if not isinstance(details, dict):
        return "" if raw else []
    refs: list[str] = []
    fk = str(details.get("fk_target", "") or "")
    if fk:
        refs.append(fk)
    default = str(details.get("default", "") or "")
    if default:
        import re

        for m in re.findall(r"nextval\(\s*'([^']+)'", default):
            refs.append(m)
        for m in re.findall(r"::\s*([A-Za-z_][A-Za-z0-9_]*)", default):  # ::enum_type cast
            refs.append(m)
        refs.append(default)  # keep the raw text so rename-in-default is catchable
    typ = str(details.get("type", "") or "")
    if typ:
        refs.append(typ)
    if raw:
        return " ".join(refs)
    # structured: only the parsed object names, not the raw default blob
    return [r for r in refs if r and r != default]


# ---- --apply: fold multi-owner objects, MOVE their DDL onto one owner -----------------------------
def apply_folds(tasks_dir: Path, cards: list[dict], folds: dict) -> list[str]:
    """For each folded object, ensure exactly ONE schema-owner authors ALL of its DDL: TRANSFER the
    loser cards' ddl_intents for that object ONTO the owner (preserving create→add→alter order), then
    strip them from the losers. A loser with no remaining schema intents flips to `consume`. The DDL
    is never DROPPED — a NOT-NULL alter on the loser becomes a second op on the owner so the
    constraint still ships (gan_c3: 'Rule 1 folds the two ops into one ordered schema task').
    Rewrites the *.card.yaml files. Returns a list of actions taken."""
    actions: list[str] = []
    by_id = {_cid(c): c for c in cards}
    loser_objects: dict[str, set[str]] = defaultdict(set)  # cid -> set of objects to strip+transfer
    touched: set[str] = set()

    # stable op precedence so the owner's chain is create_table/create_enum → add → alter → rename → drop
    op_rank = {"create_table": 0, "create_enum": 0, "add": 1, "alter": 2, "rename": 3, "drop": 4}

    for obj, fold in folds.items():
        owner = by_id.get(fold["owner"])
        if owner is None:
            continue
        touched.add(fold["owner"])
        if owner.get("phase") != "schema":
            owner["phase"] = "schema"
            actions.append(f"set {fold['owner']}.phase=schema (schema-owner of {obj})")
        owner_intents = list(_intents(owner))
        # gather this object's intents from EVERY card (owner + losers), dedup, order
        all_for_obj: list[dict] = []
        for c in cards:
            for it in _intents(c):
                if str(it.get("object", "")).strip() == obj:
                    all_for_obj.append(it)
        # dedup identical (operation, details) intents (two cards declaring the same add)
        seen_sig = set()
        merged_for_obj = []
        for it in sorted(all_for_obj, key=lambda i: op_rank.get(str(i.get("operation", "")), 9)):
            sig = (str(it.get("operation", "")), repr(it.get("details")))
            if sig in seen_sig:
                continue
            seen_sig.add(sig)
            merged_for_obj.append(it)
        # owner keeps its OTHER-object intents + the merged chain for this object
        owner_other = [it for it in owner_intents if str(it.get("object", "")).strip() != obj]
        owner["ddl_intents"] = owner_other + merged_for_obj
        if len(merged_for_obj) > 1:
            actions.append(
                f"folded {len(merged_for_obj)} ops on '{obj}' onto owner {fold['owner']} "
                f"(order: {[i.get('operation') for i in merged_for_obj]})"
            )
        for loser in fold["losers"]:
            loser_objects[loser].add(obj)

    for cid, objs in loser_objects.items():
        card = by_id.get(cid)
        if card is None:
            continue
        touched.add(cid)
        kept = [it for it in _intents(card) if str(it.get("object", "")).strip() not in objs]
        stripped = len(_intents(card)) - len(kept)
        card["ddl_intents"] = kept
        actions.append(
            f"moved {stripped} ddl_intent(s) for {sorted(objs)} off {cid} onto the owner (now a consumer)"
        )
        if not kept:
            card["phase"] = "consume"
            actions.append(f"set {cid}.phase=consume (no remaining schema intents)")

    for c in cards:
        if _cid(c) in touched:
            _write_card(tasks_dir, c)
    return actions


def _write_card(tasks_dir: Path, card: dict) -> None:
    fname = card.get("__file")
    if not fname:
        return
    out = {k: v for k, v in card.items() if not k.startswith("__")}
    path = tasks_dir / fname
    if yaml is not None:
        path.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    else:
        path.write_text(_dump_tiny(out), encoding="utf-8")


def _dump_tiny(card: dict) -> str:
    """Minimal YAML emitter for the card subset (used only when pyyaml is absent)."""
    lines: list[str] = []
    for k, v in card.items():
        if k == "ddl_intents":
            lines.append("ddl_intents:")
            for it in v or []:
                obj = it.get("object", "")
                lines.append(f"  - object: {obj}")
                if "operation" in it:
                    lines.append(f"    operation: {it['operation']}")
                if isinstance(it.get("details"), dict) and it["details"]:
                    inner = ", ".join(f"{ik}: {iv!r}" for ik, iv in it["details"].items())
                    lines.append(f"    details: {{{inner}}}")
        elif isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n"


def _report(cards: list[dict], hard: list[str], warn: list[str], edges: dict, folds: dict) -> str:
    schema_cards = [_cid(c) for c in cards if c.get("phase") == "schema"]
    out = ["# DDL conflict report (semantic DDL planner — workflow-plan Step 6)\n"]
    out.append(f"- cards analysed: {len(cards)}  · schema-phase cards: {schema_cards}\n")
    if hard:
        out.append("## ❌ HARD CONFLICTS — human must reconcile BEFORE waves freeze")
        out += [f"- {h}" for h in hard]
        out.append("")
    if folds:
        out.append("## ▶ Schema-owner assignment (Rule 1 folds)")
        for obj, f in folds.items():
            out.append(f"- `{obj}` → owner **{f['owner']}**; consumers: {f['losers']}")
        out.append("")
    if warn:
        out.append("## ⚠ Resolutions the planner applied / requires")
        out += [f"- {w}" for w in warn]
        out.append("")
    if edges:
        out.append("## Ordering edges within the schema phase (predecessor → dependent)")
        for dep, befores in edges.items():
            for b in befores:
                out.append(f"- {b}  →  {dep}")
        out.append("")
    if not (hard or warn):
        out.append("## ✓ No DDL conflicts — the schema phase is contention-free.")
    out.append(
        "\n> The schema-owner card authors ALL listed DDL in ONE ordered migration chain "
        "(deterministic slug-derived revision ids). Consumers read the columns/tables, never create "
        "them. The runner's migration_reconcile.py is the last-resort backstop."
    )
    return "\n".join(out) + "\n"


def _embed_in_index(plan_dir: Path, report: str) -> None:
    """Glue (o3 #7): embed the report into plan/INDEX.md so the Gate-2 human sees it. Replaces a
    prior embedded block (delimited) or appends one."""
    index = plan_dir / "INDEX.md"
    begin = "<!-- BEGIN ddl_conflict_report (auto-embedded by ddl_plan.py) -->"
    end = "<!-- END ddl_conflict_report -->"
    block = f"{begin}\n{report}\n{end}\n"
    if index.exists():
        text = index.read_text(encoding="utf-8")
        if begin in text and end in text:
            pre = text.split(begin)[0]
            post = text.split(end, 1)[1]
            index.write_text(pre + block + post, encoding="utf-8")
        else:
            index.write_text(
                text.rstrip() + "\n\n## DDL conflict report\n" + block, encoding="utf-8"
            )
    else:
        index.write_text("# Plan INDEX\n\n## DDL conflict report\n" + block, encoding="utf-8")


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    do_apply = "--apply" in argv
    if not args:
        print("usage: ddl_plan.py <tasks-dir> [--apply]", file=sys.stderr)
        return 3
    tasks_dir = Path(args[0])
    if not tasks_dir.is_dir():
        print(f"ERROR: {tasks_dir} is not a directory of *.card.yaml", file=sys.stderr)
        return 3
    try:
        cards = _load_cards(tasks_dir)
    except CardParseError as e:
        print(f"✗ FAIL-CLOSED: {e}", file=sys.stderr)
        return 3
    if not cards:
        print(f"no .card.yaml files in {tasks_dir}", file=sys.stderr)
        return 3

    hard, warn, edges, folds = analyse(cards)

    applied: list[str] = []
    if do_apply and folds and not hard:
        applied = apply_folds(tasks_dir, cards, folds)
        # re-analyse the rewritten cards so the report reflects the post-fold reality
        cards = _load_cards(tasks_dir)
        hard, warn, edges, folds = analyse(cards)
    elif do_apply and hard:
        print(
            "✗ NOT applying folds: HARD CONFLICT present — the human must reconcile types/nullability "
            "first (a fold would bake in a wrong shape).",
            file=sys.stderr,
        )

    report = _report(cards, hard, warn, edges, folds)
    out_path = tasks_dir.parent / "ddl_conflict_report.md"
    out_path.write_text(report, encoding="utf-8")
    _embed_in_index(tasks_dir.parent, report)
    print(report)
    if applied:
        print("\n--apply actions:", file=sys.stderr)
        for a in applied:
            print(f"  - {a}", file=sys.stderr)
    print(f"\n→ wrote {out_path} + embedded into {tasks_dir.parent / 'INDEX.md'}", file=sys.stderr)
    if yaml is None:
        print(
            "ℹ pyyaml not available — used the fallback parser (details fully parsed; fail-closed on "
            "any unparseable details). Install pyyaml for canonical parsing.",
            file=sys.stderr,
        )
    return 2 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
