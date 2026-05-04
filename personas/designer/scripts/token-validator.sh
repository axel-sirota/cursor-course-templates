#!/usr/bin/env bash
# token-validator.sh
# Fires on afterFileEdit for .css/.scss/.tsx/.jsx/.vue/.svelte files.
# Warns to stderr about hardcoded color or spacing values. Advisory only (exits 0).

set -euo pipefail

# Read file_path from stdin JSON
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || true)

# Exit silently if no file path
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only fire on supported style/component file types
case "$FILE_PATH" in
  *.css|*.scss|*.tsx|*.jsx|*.vue|*.svelte)
    ;;
  *)
    exit 0
    ;;
esac

# Exit silently if file does not exist
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

WARNED=0

# Check for hardcoded hex colors (outside comment lines)
HEX_HITS=$(grep -n '#[0-9a-fA-F]\{3,6\}\b' "$FILE_PATH" | grep -v '^\s*//' | grep -v '^\s*\*' || true)
if [ -n "$HEX_HITS" ]; then
  echo "[token-validator] WARNING: Hardcoded hex color(s) found in $FILE_PATH — use design tokens instead:" >&2
  echo "$HEX_HITS" >&2
  WARNED=1
fi

# Check for hardcoded px values in spacing properties (excluding 0px and 1px)
SPACING_HITS=$(grep -nE '(margin|padding|gap):\s*[2-9][0-9]*px|[0-9]{2,}px' "$FILE_PATH" | grep -v '^\s*//' | grep -v '^\s*\*' || true)
if [ -n "$SPACING_HITS" ]; then
  echo "[token-validator] WARNING: Hardcoded spacing value(s) found in $FILE_PATH — use spacing tokens instead:" >&2
  echo "$SPACING_HITS" >&2
  WARNED=1
fi

# Advisory only — always exit 0
exit 0
