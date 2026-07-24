#!/usr/bin/env python3
"""migration_reconcile.py — make a wave's alembic migrations concordant (workflow-execute Step 0.5).

The safety-net the Wave-1 disaster needed: after the SCHEMA phase merges, several worktrees may have
each authored a migration with a colliding/placeholder revision id and/or duplicate DDL (because
worktrees are isolated — agents can't see each other). This linearizes them into ONE clean chain.

Cheap when clean: if there's a single linear head, no dup revision ids, and no duplicate DDL, it is a
no-op and exits 0. It only rewrites files when it detects collisions/dups.

Usage:  migration_reconcile.py <wave-tag> [--since <base-rev>] [--expect-migrations] [--apply]
        --since <base-rev>: only reconcile migrations authored on TOP of <base-rev> (the wave's base
        head, e.g. the prior wave's tip). Without it the script scans ALL migrations, which will
        false-positive on the healthy historical create→alter→drop evolution of the same object.
        ALWAYS pass --since <head-before-this-wave> in a real wave run.
        --expect-migrations: the wave had ≥1 schema task → finding ZERO wave migrations is a FAILURE
        (fail-closed), never a silent no-op.
        --apply: perform the SAFE mechanical rewrite — regenerate colliding revision ids + re-chain
        strictly linear, then write the sentinel. Duplicate DDL is NEVER auto-resolved (which body
        survives is semantic) → stays fail-closed (exit 2). The drift gate must still pass after.
Exit:   0 = concordant / cleanly rewritten (sentinel written) · 2 = unresolved (manual fix) · 3 = bad env

What it does NOT do: run `alembic upgrade` against a shared/prod DB. Migrations are authored by
Claude, APPLIED BY AXEL. Model-sync verification uses the repo's existing
`tests/integration/test_UP_infra_foundations_alembic_drift.py` (V29) against a throwaway DB the
caller provides via DATABASE_URL/TEST_DB_NAME — this script only reconciles the FILES.

Algorithm (codex o3): heads→merge-or-rechain · parse each revision · dedup by hashing
(table, column, op_type) · regen placeholder/dup ids · re-chain down_revision strictly linear.
"""

from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

# script lives at <repo>/.claude/skills/workflow-execute/scripts/ → 4 levels up to repo root
ROOT = Path(__file__).resolve().parents[4]
VERSIONS = ROOT / "migrations" / "versions"

REV_RE = re.compile(r'^revision(?::\s*str)?\s*=\s*[\'"]([^\'"]+)[\'"]', re.M)
DOWN_RE = re.compile(r'^down_revision(?::[^=]+)?\s*=\s*[\'"]?([^\'"\n]+)[\'"]?', re.M)
# Precise DDL signature: create_table(name) → ("create_table", name); add_column("table", Column("col"))
# → ("add_column", "table.col"). We MUST include the column for add_column or every migration that
# touches the same table false-flags as a duplicate (the bug that flagged the healthy history).
CREATE_TABLE_RE = re.compile(r'op\.create_table\(\s*["\']([^"\']+)["\']')
ADD_COLUMN_RE = re.compile(
    r'op\.add_column\(\s*["\']([^"\']+)["\']\s*,\s*sa\.Column\(\s*["\']([^"\']+)["\']'
)
CREATE_INDEX_RE = re.compile(r'op\.create_index\(\s*["\']([^"\']+)["\']')
CREATE_UNIQUE_RE = re.compile(r'op\.create_unique_constraint\(\s*["\']([^"\']+)["\']')

# Set by --expect-migrations: when the wave HAD schema tasks, zero wave migrations is a FAILURE.
EXPECT_MIGRATIONS = False
# Set by --apply: perform the SAFE mechanical rewrite (regen colliding ids + linearize the chain)
# instead of only reporting. Duplicate DDL is never auto-resolved (semantic) — fail-closed.
APPLY = False


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _migration_files() -> list[Path]:
    return sorted(VERSIONS.glob("*.py"))


def _rev_of(text: str) -> str | None:
    m = REV_RE.search(text)
    return m.group(1) if m else None


def _down_of(text: str) -> tuple[str, ...]:
    """down_revision can be None, a single rev, OR a tuple/list (a MERGE migration with ≥2 parents).
    Return a tuple of parent revisions (empty for base). Adversarial #3: the old single-string parse
    silently dropped merge migrations from the wave walk → false 'no migrations' / false-clean."""
    # tuple/list form: down_revision = ("a", "b")  or  ["a", "b"]
    mt = re.search(r"down_revision[^=]*=\s*[\(\[]([^)\]]*)[\)\]]", text)
    if mt:
        return tuple(
            p.strip().strip("'\"") for p in mt.group(1).split(",") if p.strip().strip("'\"")
        )
    m = DOWN_RE.search(text)
    if not m:
        return ()
    v = m.group(1).strip()
    return () if v in ("None", "") else (v,)


def _ddl_sig(text: str) -> set[tuple[str, str]]:
    """PRECISE set of (op_type, object) this migration performs — for duplicate detection.

    add_column uses table.column (NOT just table) so two migrations adding DIFFERENT columns to the
    same table are NOT flagged as duplicates. Only a literal same-(op, object) in two files is a dup.
    """
    sigs: set[tuple[str, str]] = set()
    sigs |= {("create_table", n) for n in CREATE_TABLE_RE.findall(text)}
    sigs |= {("add_column", f"{tbl}.{col}") for tbl, col in ADD_COLUMN_RE.findall(text)}
    sigs |= {("create_index", n) for n in CREATE_INDEX_RE.findall(text)}
    sigs |= {("create_unique_constraint", n) for n in CREATE_UNIQUE_RE.findall(text)}
    return sigs


def _new_id(seed: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_DNS, seed).hex[:12]


def _alembic_heads() -> list[str] | None:
    """Return alembic's head revisions (authoritative — accounts for merge migrations). None if
    alembic can't run here (env not set up); the caller then falls back to the file-scan heuristic."""
    import subprocess

    try:
        r = subprocess.run(
            ["alembic", "heads"], cwd=ROOT, capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            return None
        return [ln.split()[0] for ln in r.stdout.splitlines() if ln.strip() and "(head)" in ln]
    except Exception:
        return None


def _wave_migrations(all_info: list[dict], since: str | None) -> list[dict]:
    """The migrations introduced ON TOP of `since` (this wave's new ones). Without `since`, returns
    all (caller is warned this false-positives on history)."""
    if not since:
        return all_info
    by_rev = {it["rev"]: it for it in all_info}
    # A migration is "in the wave" if ANY path from it through down_revision parents (tuples
    # included — merge migrations have several) reaches `since`. BFS over all parents.
    wave = []
    for it in all_info:
        stack, seen, found = [it], set(), False
        while stack and not found:
            cur = stack.pop()
            if cur["rev"] in seen:
                continue
            seen.add(cur["rev"])
            for parent in cur["down"]:  # tuple of parent revisions
                if parent == since:
                    found = True
                    break
                p = by_rev.get(parent)
                if p:
                    stack.append(p)
        if found:
            wave.append(it)
    return wave


def reconcile(wave_tag: str, since: str | None = None) -> int:
    if not VERSIONS.is_dir():
        print(f"ERROR: {VERSIONS} not found", file=sys.stderr)
        return 3

    files = _migration_files()
    all_info = []
    for f in files:
        t = _read(f)
        rev = _rev_of(t)
        if rev is None:
            continue
        all_info.append({"file": f, "rev": rev, "down": _down_of(t), "ddl": _ddl_sig(t), "text": t})

    info = _wave_migrations(all_info, since)
    if since and not info:
        # FAIL-CLOSED (adversarial #3): if the wave was SUPPOSED to produce migrations (schema tasks
        # existed) but we found ZERO on top of `since`, that's a broken state — a wrong --since, a
        # migration that didn't merge, or a down_revision the walk couldn't follow (tuple/merge rev).
        # Writing migrations.ok here would lift the barrier on broken DDL. Refuse unless the caller
        # explicitly asserts the wave has no schema work.
        if EXPECT_MIGRATIONS:
            print(
                f"✗ FAIL-CLOSED: --expect-migrations set but ZERO wave migrations found on top of "
                f"{since}. Either --since is wrong (pass the PRE-wave head, not post-schema-merge), a "
                f"schema task's migration didn't merge, or a down_revision is a tuple/merge rev the "
                f"walk can't follow. NOT writing migrations.ok — the barrier stays down.",
                file=sys.stderr,
            )
            return 2
        _write_ok(
            wave_tag, f"no new migrations on top of {since} — no-op (no schema work asserted)"
        )
        print(f"✓ no wave migrations on top of {since} (no-op).")
        return 0
    if not since:
        print(
            "⚠ no --since given: scanning ALL migrations (will false-positive on history); pass "
            "--since <prior-wave-head> in a real run.",
            file=sys.stderr,
        )

    # 1. Detect colliding revision ids
    seen_rev: dict[str, list] = {}
    for it in info:
        seen_rev.setdefault(it["rev"], []).append(it)
    collisions = {r: v for r, v in seen_rev.items() if len(v) > 1}

    # 2. Detect duplicate DDL across DIFFERENT files (same (op, object) authored twice)
    sig_owner: dict[tuple[str, str], list] = {}
    for it in info:
        for sig in it["ddl"]:
            sig_owner.setdefault(sig, []).append(it)
    dup_ddl = {s: v for s, v in sig_owner.items() if len({id(x) for x in v}) > 1}

    # Heads via alembic itself (correctly accounts for already-merged branches — regex can't).
    heads = _alembic_heads()

    # FILE-LEVEL multi-head detection (the 2026-06-12 first_test miss): when alembic can't run from
    # the repo root (no env sourced) `_alembic_heads()` returns None, and the old `heads is None or
    # len<=1` clause SILENTLY SKIPPED the multi-head check — 5 schema migrations all chained off the
    # SAME down_revision (a 5-way fork) sailed through as "concordant". So we ALSO detect forks purely
    # from the files: any down_revision shared by ≥2 WAVE migrations is a multi-head, no alembic needed.
    down_owners: dict[str, list] = {}
    for it in info:
        for parent in it["down"]:  # tuple of parents (merge migrations have several)
            down_owners.setdefault(parent, []).append(it)
    file_forks = {p: v for p, v in down_owners.items() if len(v) > 1}
    # also: ≥2 wave migrations that are NObody's parent = ≥2 tips = a multi-head, even with distinct downs
    wave_revs = {it["rev"] for it in info}
    referenced = {p for it in info for p in it["down"]}
    tips = [it for it in info if it["rev"] not in referenced or it["rev"] not in wave_revs]
    multi_head = bool(file_forks) or (heads is not None and len(heads) > 1) or len(tips) > 1

    clean = not collisions and not dup_ddl and not multi_head
    if clean:
        _write_ok(wave_tag, f"single head, no dup ids, no dup DDL — no-op (alembic heads={heads})")
        print(f"✓ migrations already concordant (no-op). heads={heads}")
        return 0
    if file_forks and (heads is None or len(heads) <= 1):
        print(
            "⚠ MULTI-HEAD detected from FILES (alembic couldn't confirm — heads="
            f"{heads}): these down_revisions are shared by ≥2 wave migrations → a fork that must be "
            "linearized:",
            file=sys.stderr,
        )
        for parent, v in file_forks.items():
            print(f"    {parent} ← {[x['file'].name for x in v]}", file=sys.stderr)

    # --- there IS work to do; report precisely and DO NOT silently rewrite history ---
    print("⚠ MIGRATION RECONCILIATION NEEDED:")
    if collisions:
        print("  colliding revision ids:")
        for r, v in collisions.items():
            print(f"    {r}: {[x['file'].name for x in v]}")
    if dup_ddl:
        print(
            "  duplicate DDL (same object created/altered in >1 migration — collapse to ONE owner):"
        )
        for (op, name), v in dup_ddl.items():
            print(f"    {op} {name}: {[x['file'].name for x in v]}")
    if heads and len(heads) > 1:
        print(
            f"  MULTIPLE HEADS (alembic): {heads} → linearize (chain each off the previous, single tip)."
        )

    # --- --apply: perform the SAFE mechanical part of the rewrite ---------------------------------
    # Auto-fixable: colliding revision ids + a non-linear down_revision chain. NOT auto-fixable:
    # duplicate DDL (which file's BODY survives is a semantic call) — that stays fail-closed even
    # under --apply, because a wrong auto-merge would ship the wrong schema.
    if APPLY:
        if dup_ddl:
            print(
                "\n✗ --apply CANNOT auto-resolve duplicate DDL (choosing which migration body keeps the "
                "object is a semantic decision). Resolve the dup by hand, then re-run. NO sentinel — "
                "barrier stays down (fail-closed).",
                file=sys.stderr,
            )
            return 2
        actions = _apply_rewrite(info, collisions, since)
        if actions is None:
            print(
                "\n✗ --apply could not linearize (could not determine the base head to chain off). "
                "Pass --since <prior-wave-head>. NO sentinel — fail-closed.",
                file=sys.stderr,
            )
            return 2
        # re-verify: re-read and confirm (a) no remaining id collisions AND (b) the wave is now a
        # SINGLE linear chain — no down_revision shared by ≥2 wave files (the multi-head we just fixed).
        info2 = []
        for f in _migration_files():
            t = _read(f)
            rev = _rev_of(t)
            if rev:
                info2.append({"rev": rev, "down": _down_of(t)})
        seen2: dict[str, int] = {}
        for it in info2:
            seen2[it["rev"]] = seen2.get(it["rev"], 0) + 1
        if any(n > 1 for n in seen2.values()):
            print(
                "\n✗ --apply ran but revision ids still collide — NOT writing sentinel (fail-closed).",
                file=sys.stderr,
            )
            return 2
        wave_revs2 = {it["rev"] for it in info}
        down2: dict[str, int] = {}
        for it in info2:
            if it["rev"] in wave_revs2:  # only the wave's migrations
                for p in it["down"]:
                    down2[p] = down2.get(p, 0) + 1
        if any(n > 1 for n in down2.values()):
            print(
                "\n✗ --apply ran but a down_revision is STILL shared by ≥2 wave migrations (multi-head "
                "not fully linearized) — NOT writing sentinel (fail-closed).",
                file=sys.stderr,
            )
            return 2
        for a in actions:
            print(f"  ✎ {a}", file=sys.stderr)
        _write_ok(
            wave_tag,
            f"--apply rewrote {len(actions)} file(s): regenerated colliding ids + linearized chain. "
            f"RUN the alembic-drift gate on a throwaway DB before applying.",
        )
        print(
            "\n✓ --apply done (ids regenerated, chain linearized). Sentinel written. "
            "You MUST still run test_UP_infra_foundations_alembic_drift on a throwaway DB "
            "(empty autogenerate diff) before Axel applies — the rewrite is structural, not semantic.",
            file=sys.stderr,
        )
        return 0

    print(
        "\nThis script DETECTS and REPORTS (run with --apply to auto-fix colliding ids + linearize). "
        "The canonical resolution per docs/researches/wave-migration-redesign.md:\n"
        "  - keep ONE migration per (op,object); drop the duplicate create/add from the other files\n"
        f"  - give each surviving migration a UNIQUE id (e.g. uuid5-of-slug → {_new_id('example-slug')})\n"
        "  - re-chain down_revision strictly linear off the prior wave head\n"
        "  - then run the repo's alembic-drift gate (test_UP_infra_foundations_alembic_drift) on a "
        "throwaway DB; it must report an EMPTY autogenerate diff.\n"
        "NO sentinel written — the barrier does NOT lift until this is resolved + the drift gate is green.",
        file=sys.stderr,
    )
    return 2


def _rewrite_rev(text: str, new_rev: str) -> str:
    """Replace the `revision = '...'` value (and a matching down_revision pointer is handled by the
    caller via the chain rewrite). Only the revision line is touched here."""
    return REV_RE.sub(f"revision = '{new_rev}'", text, count=1)


def _rewrite_down(text: str, new_down: str | None) -> str:
    repl = "None" if new_down is None else repr(new_down)
    if DOWN_RE.search(text):
        return DOWN_RE.sub(f"down_revision = {repl}", text, count=1)
    return text  # no down_revision line to rewrite (shouldn't happen for a real migration)


def _apply_rewrite(info: list[dict], collisions: dict, since: str | None) -> list[str] | None:
    """SAFE mechanical rewrite: regenerate any colliding revision id to a unique uuid5-of-filename id,
    then re-chain the wave's migrations into ONE strictly-linear chain off `since` (the prior-wave
    head). Returns the list of actions, or None if it cannot determine the base to chain off.
    Does NOT touch migration bodies (no DDL changes) — purely id + down_revision linearization."""
    actions: list[str] = []
    # order the wave migrations deterministically by filename so the linear chain is stable
    wave = sorted(info, key=lambda it: it["file"].name)
    if not wave:
        return actions

    # 1. regenerate colliding ids (the #1 Wave-1 cause: many files sharing a placeholder id).
    # Several files may share ONE colliding rev string, so remap per-FILE (a unique target each).
    colliding_revs = set(collisions.keys())
    new_rev_of: dict[Path, str] = {}
    for it in wave:
        if it["rev"] in colliding_revs:
            nid = _new_id(it["file"].name)
            new_rev_of[it["file"]] = nid
            actions.append(f"{it['file'].name}: revision {it['rev']} → {nid} (was colliding)")
        else:
            new_rev_of[it["file"]] = it["rev"]

    # 2. determine the base to chain off: explicit --since, else the wave's lowest down_revision that
    #    points OUTSIDE the wave (a parent not authored this wave).
    wave_revs = {it["rev"] for it in wave}
    base = since
    if base is None:
        external_parents = [p for it in wave for p in it["down"] if p and p not in wave_revs]
        base = external_parents[0] if external_parents else None
    if base is None:
        return None

    # 3. re-chain strictly linear: file[0].down = base; file[i].down = new_rev_of[file[i-1]]
    prev = base
    for it in wave:
        text = _read(it["file"])
        text = _rewrite_rev(text, new_rev_of[it["file"]])
        text = _rewrite_down(text, prev)
        it["file"].write_text(text, encoding="utf-8")
        actions.append(f"{it['file'].name}: down_revision → {prev}")
        prev = new_rev_of[it["file"]]
    return actions


def _write_ok(wave_tag: str, why: str) -> None:
    d = ROOT / f"wave_{wave_tag}"
    d.mkdir(exist_ok=True)
    (d / "migrations.ok").write_text(f"reconciled: {why}\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    global EXPECT_MIGRATIONS, APPLY
    if len(argv) < 2:
        print(
            "usage: migration_reconcile.py <wave-tag> [--since <base-rev>] [--expect-migrations] "
            "[--apply]",
            file=sys.stderr,
        )
        return 3
    since = None
    if "--since" in argv:
        i = argv.index("--since")
        since = argv[i + 1] if i + 1 < len(argv) else None
    # --expect-migrations: the wave HAD schema tasks → finding zero is a FAILURE (fail-closed),
    # never a silent no-op. The skill passes this whenever the schema phase had ≥1 task.
    EXPECT_MIGRATIONS = "--expect-migrations" in argv
    # --apply: auto-fix colliding ids + linearize (SAFE structural rewrite); dup DDL stays fail-closed.
    APPLY = "--apply" in argv
    return reconcile(argv[1], since)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
