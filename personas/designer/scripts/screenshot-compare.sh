#!/usr/bin/env bash
# screenshot-compare.sh
# Triggered by the stop hook at session end.
# Creates docs/screenshots/ if missing and prints an advisory message.
# Non-blocking (exits 0).

set -euo pipefail

# Ensure docs/screenshots/ exists
mkdir -p docs/screenshots

# Advisory message
echo "[screenshot-compare] Session ended. Run /responsive-checker to generate breakpoint screenshots before opening a PR." >&2

# Advisory only — always exit 0
exit 0
