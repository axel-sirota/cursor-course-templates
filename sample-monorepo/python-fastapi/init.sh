#!/usr/bin/env bash
# init.sh — turn this copied directory into the standalone git repo used by the labs.
#
# Run this AFTER copying the variant directory out of the course repo:
#
#   cp -R sample-monorepo/python-fastapi ~/labs/refund-monorepo
#   cd ~/labs/refund-monorepo
#   ./init.sh
#
# The script is idempotent: run it twice and the second run changes nothing.

set -euo pipefail

cd "$(dirname "$0")"

# ---------------------------------------------------------------------------
# Guard: refuse to run inside the course repo checkout.
# Inside the course repo this directory sits at <repo>/sample-monorepo/<variant>,
# so the parent dir is named "sample-monorepo" and ../../.git exists.
# ---------------------------------------------------------------------------
parent_name="$(basename "$(cd .. && pwd)")"
if { [ -e ../../.git ] && [ "$parent_name" = "sample-monorepo" ]; } \
   || [ -f ../COURSE_TEMPLATE ] || [ -f COURSE_TEMPLATE ]; then
  echo "This directory is still inside the course repo — init.sh will not run here."
  echo ""
  echo "Copy it out first, then run init.sh from the copy:"
  echo "  cp -R \"$PWD\" ~/labs/refund-monorepo"
  echo "  cd ~/labs/refund-monorepo"
  echo "  ./init.sh"
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 1: git init + first commit (skipped if already done)
# ---------------------------------------------------------------------------
if [ -d .git ]; then
  echo "Git repo already initialized — skipping git init."
else
  git init -b main
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example."
fi

if ! git rev-parse --verify -q HEAD >/dev/null; then
  git add -A
  git commit -m "chore: init sample monorepo"
  echo "Created initial commit on main."
fi

# ---------------------------------------------------------------------------
# Step 2: build the flat-claude-md branch (used in the /context comparison lab).
# It squashes root CLAUDE.md + every services/*/CLAUDE.md into ONE root file,
# so you can compare context loading against the per-service layout on main.
# ---------------------------------------------------------------------------
build_flat_branch() {
  local first_service_md="services/gateway/CLAUDE.md"
  if [ ! -f CLAUDE.md ] || [ ! -f "$first_service_md" ]; then
    echo "WARNING: CLAUDE.md files are not present yet — skipping the flat-claude-md branch."
    echo "         Re-run ./init.sh once they exist and the branch will be built."
    return 0
  fi

  if git rev-parse --verify -q flat-claude-md >/dev/null; then
    echo "Branch flat-claude-md already exists — skipping."
    return 0
  fi

  # The CLAUDE.md files may be untracked (init ran before they existed, re-run after adding
  # them). Commit them on main first so the flat branch can `git rm` tracked files safely.
  if [ -n "$(git status --porcelain -- CLAUDE.md services/*/CLAUDE.md 2>/dev/null)" ]; then
    git add CLAUDE.md services/*/CLAUDE.md
    git commit -q -m "docs: nested CLAUDE.md files"
  fi

  git checkout -b flat-claude-md

  local flat_file
  flat_file="$(mktemp)"
  cat CLAUDE.md >"$flat_file"
  local svc_md svc_name
  for svc_md in services/*/CLAUDE.md; do
    [ -f "$svc_md" ] || continue
    svc_name="$(basename "$(dirname "$svc_md")")"
    {
      echo ""
      echo "## Service: $svc_name"
      echo ""
      cat "$svc_md"
    } >>"$flat_file"
  done
  mv "$flat_file" CLAUDE.md

  git rm -q services/*/CLAUDE.md
  git add CLAUDE.md
  git commit -m "flat CLAUDE.md variant for /context comparison"
  git checkout main
  echo "Built branch flat-claude-md (back on main)."
}
build_flat_branch

# ---------------------------------------------------------------------------
# Next steps
# ---------------------------------------------------------------------------
echo ""
echo "Done. Next steps:"
echo "  1. cd $(pwd)"
echo "  2. python3 -m venv .venv && .venv/bin/python3 -m pip install -U pip"
echo "  3. claude"
