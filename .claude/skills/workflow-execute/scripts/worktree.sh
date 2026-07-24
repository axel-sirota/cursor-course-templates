#!/usr/bin/env bash
# worktree.sh — per-agent isolated worktree setup/teardown for /workflow-execute (course-build).
#
# Usage:
#   worktree.sh up   <task-slug> <plan-slug>   # create worktree + branch off current HEAD
#   worktree.sh down <task-slug> [--force]     # GUARDED remove (refuses to lose unmerged work)
#   worktree.sh path <task-slug>               # print the worktree path
set -uo pipefail

CMD="${1:?up|down|path}"
SLUG="${2:?task-slug}"
ROOT="$(git rev-parse --show-toplevel)"
REPO="$(basename "$ROOT")"
WT="$(dirname "$ROOT")/${REPO}-${SLUG}"

case "$CMD" in
  up)
    PLAN_SLUG="${3:?plan-slug (3rd arg)}"
    BR="wf/${PLAN_SLUG}/${SLUG}"
    cd "$ROOT"
    git worktree add "$WT" -b "$BR" HEAD || { echo "worktree add failed (branch $BR may exist)" >&2; exit 2; }
    # shared, gitignored things the worktree does not inherit (only if they exist at root)
    [ -e "$ROOT/.venv" ] && ln -sfn "$ROOT/.venv" "$WT/.venv"
    [ -e "$ROOT/.env" ]  && ln -sfn "$ROOT/.env"  "$WT/.env"
    [ -d "$ROOT/node_modules" ] && ln -sfn "$ROOT/node_modules" "$WT/node_modules"
    # keep symlinks out of git status inside the worktree
    GITDIR="$(git -C "$WT" rev-parse --git-dir)"
    mkdir -p "$GITDIR/info"
    { echo ".venv"; echo ".env"; echo "node_modules"; echo "TRANSITION.md"; } \
      >> "$GITDIR/info/exclude" 2>/dev/null || true
    echo "$WT (branch $BR)"
    ;;
  down)
    FORCE=0; [ "${3:-}" = "--force" ] && FORCE=1
    cd "$ROOT"
    if [ ! -d "$WT" ]; then echo "no worktree at $WT" >&2; exit 0; fi
    BR="$(git -C "$WT" rev-parse --abbrev-ref HEAD 2>/dev/null)"
    # GUARDED teardown: never silently destroy dirty/unmerged task work. Snapshot a bundle first.
    if [ "$FORCE" != "1" ]; then
      DIRTY="$(git -C "$WT" status --porcelain 2>/dev/null | grep -vE '\.env|\.venv|node_modules|TRANSITION\.md' || true)"
      if [ -n "$DIRTY" ]; then
        echo "REFUSING down: worktree $WT has uncommitted changes:" >&2
        echo "$DIRTY" >&2
        echo "  commit them, or re-run with --force (LOSES them)." >&2
        exit 3
      fi
      # is the branch merged into its feature branch? infer feat from the BR prefix.
      FEAT="${BR#wf/}"; FEAT="feat/${FEAT%%/*}"
      TIP="$(git -C "$WT" rev-parse HEAD 2>/dev/null)"
      if git rev-parse --verify "$FEAT" >/dev/null 2>&1; then
        if ! git merge-base --is-ancestor "$TIP" "$FEAT" 2>/dev/null; then
          BUNDLE="$ROOT/.worktree-snapshots"; mkdir -p "$BUNDLE"
          git -C "$ROOT" bundle create "$BUNDLE/${SLUG}-${TIP:0:8}.bundle" "$BR" 2>/dev/null \
            && echo ">> $BR not merged into $FEAT — snapshotted to $BUNDLE/${SLUG}-${TIP:0:8}.bundle" >&2
          echo "REFUSING down: $BR ($TIP) is NOT merged into $FEAT. Bundle saved. Re-run --force to discard." >&2
          exit 3
        fi
      else
        echo ">> WARN: can't find $FEAT to verify merge; snapshotting before delete." >&2
        BUNDLE="$ROOT/.worktree-snapshots"; mkdir -p "$BUNDLE"
        git -C "$ROOT" bundle create "$BUNDLE/${SLUG}-${TIP:0:8}.bundle" "$BR" 2>/dev/null || true
      fi
    fi
    git worktree remove --force "$WT" 2>/dev/null || echo "worktree remove failed for $WT" >&2
    [ -n "${BR:-}" ] && [ "$BR" != "HEAD" ] && git branch -D "$BR" 2>/dev/null || true
    echo "removed $WT (branch $BR)"
    ;;
  path)
    echo "$WT"
    ;;
  *) echo "unknown cmd: $CMD" >&2; exit 2;;
esac
