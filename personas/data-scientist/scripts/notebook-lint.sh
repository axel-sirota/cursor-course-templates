#!/usr/bin/env bash
# notebook-lint.sh — Advisory check: warn if a notebook has not been run to completion.
# Triggered by afterFileEdit hook. Reads file_path from stdin (JSON) or $FILE_PATH env var.
# Requires: jq
# Non-blocking: exits 0 always, warnings go to stderr.

set -euo pipefail

# Parse file_path from JSON stdin if available, otherwise fall back to env var
if [ -t 0 ]; then
  # No stdin — use environment variable
  FILE="${FILE_PATH:-}"
else
  # Read JSON from stdin
  INPUT="$(cat)"
  FILE="$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || true)"
fi

# Exit silently if no file path provided
if [ -z "$FILE" ]; then
  exit 0
fi

# Only fire on .ipynb files
case "$FILE" in
  *.ipynb) ;;
  *) exit 0 ;;
esac

# Exit if file does not exist
if [ ! -f "$FILE" ]; then
  exit 0
fi

# Require jq
if ! command -v jq &>/dev/null; then
  echo "WARNING [notebook-lint]: jq not found — install with: brew install jq / apt install jq" >&2
  exit 0
fi

# Count total cells
TOTAL_CELLS="$(jq '.cells | length' "$FILE" 2>/dev/null || echo 0)"

if [ "$TOTAL_CELLS" -eq 0 ]; then
  exit 0
fi

# Get max execution_count (treating null as 0)
MAX_EXEC="$(jq '[.cells[].execution_count // 0] | max' "$FILE" 2>/dev/null || echo 0)"

# Check if any cell has null execution_count (unexecuted cells)
NULL_COUNT="$(jq '[.cells[] | select(.cell_type == "code") | select(.execution_count == null)] | length' "$FILE" 2>/dev/null || echo 0)"

# Warn if notebook appears not to have been run to completion
if [ "$NULL_COUNT" -gt 0 ]; then
  echo "WARNING [notebook-lint]: $FILE has $NULL_COUNT unexecuted code cell(s) (execution_count is null)" >&2
  echo "  Clear all outputs and re-run the notebook top-to-bottom before handoff." >&2
fi

if [ "$MAX_EXEC" -lt "$TOTAL_CELLS" ] && [ "$NULL_COUNT" -eq 0 ]; then
  echo "WARNING [notebook-lint]: $FILE max execution_count ($MAX_EXEC) is less than total cells ($TOTAL_CELLS)" >&2
  echo "  The notebook may not have been run completely. Re-run top-to-bottom before handoff." >&2
fi

exit 0
