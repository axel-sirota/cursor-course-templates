#!/usr/bin/env bash
# no-inline-styles.sh
# Fires on afterFileEdit for .tsx/.jsx files.
# Warns to stderr about inline style={{ }} attributes. Advisory only (exits 0).

set -euo pipefail

# Read file_path from stdin JSON
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || true)

# Exit silently if no file path
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only fire on .tsx and .jsx files
case "$FILE_PATH" in
  *.tsx|*.jsx)
    ;;
  *)
    exit 0
    ;;
esac

# Exit silently if file does not exist
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# Check for inline style={{ }} attributes
INLINE_HITS=$(grep -n 'style=\s*{{' "$FILE_PATH" || true)
if [ -n "$INLINE_HITS" ]; then
  echo "[no-inline-styles] WARNING: Inline style attribute(s) found in $FILE_PATH — use className with design tokens instead:" >&2
  echo "$INLINE_HITS" >&2
fi

# Advisory only — always exit 0
exit 0
