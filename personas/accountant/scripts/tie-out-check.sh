#!/usr/bin/env bash
# tie-out-check.sh: stop hook for the accountant persona.
# If output/ has files, run the tie-out tests (pytest -q tests/) so a broken tie-out
# is visible before the session ends. Non-blocking: always exits 0. Messages go to stderr.
#
# Hooks run from the repo root. The workspace defaults to workspaces/accountant;
# override with ACCOUNTANT_WORKSPACE. If run from inside the workspace, "." is used.

set -uo pipefail

# Drain hook JSON from stdin; this hook does not need it.
if [ ! -t 0 ]; then
  cat >/dev/null
fi

WS="${ACCOUNTANT_WORKSPACE:-workspaces/accountant}"
if [ ! -d "$WS" ]; then
  if [ -d "output" ]; then
    WS="."
  else
    exit 0
  fi
fi

cd "$WS" || exit 0

if [ ! -d output ] || [ -z "$(find output -type f ! -name '.*' 2>/dev/null | head -n 1)" ]; then
  exit 0
fi

if [ ! -d tests ]; then
  echo "ADVISORY [tie-out-check]: output/ has files but there is no tests/ folder. Nothing proves these reports tie. Add tie-out tests." >&2
  exit 0
fi

PY=""
for candidate in ".venv/bin/python3" "../../.venv/bin/python3" ".venv/Scripts/python.exe"; do
  if [ -x "$candidate" ]; then
    PY="$candidate"
    break
  fi
done
PY="${PY:-python3}"

if ! "$PY" -c "import pytest" >/dev/null 2>&1; then
  echo "ADVISORY [tie-out-check]: pytest is not installed for $PY. Install it, then run: pytest -q tests/" >&2
  exit 0
fi

echo "[tie-out-check] output/ has files. Running tie-out tests in $WS ..." >&2
if "$PY" -m pytest -q tests/ >&2 2>&1; then
  echo "[tie-out-check] PASS. Tie-out tests are green." >&2
else
  echo "WARNING [tie-out-check]: tie-out tests FAILED. Fix before handing off. Put this in the transition doc as the first next step." >&2
fi

exit 0
