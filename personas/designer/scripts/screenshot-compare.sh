#!/usr/bin/env bash
# screenshot-compare.sh
# Triggered by the stop hook at session end.
# Creates the responsive screenshot folder if missing and prints an advisory message.
# Hooks run from the repo root; designer work lives in workspaces/designer/.
# Non-blocking (exits 0).

set -euo pipefail

# Use the designer workspace when it exists, else fall back to cwd
if [ -d "workspaces/designer" ]; then
  BASE="workspaces/designer"
else
  BASE="."
fi

# Ensure docs/responsive/ exists (where the responsive-checker agent saves screenshots)
mkdir -p "$BASE/docs/responsive" 2>/dev/null || true

# Advisory message
echo "[screenshot-compare] Session ended. Run the responsive-checker agent to save breakpoint screenshots to $BASE/docs/responsive/ before opening a PR." >&2

# Advisory only, always exit 0
exit 0
