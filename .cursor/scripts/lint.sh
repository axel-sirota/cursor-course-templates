#!/usr/bin/env bash
# lint.sh — afterFileEdit hook
# Reads file_path from stdin JSON. Non-blocking (exit 0 always).

set -euo pipefail

# Read stdin JSON
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || true)

# Exit immediately if no file path
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Determine extension
EXT="${FILE_PATH##*.}"

case "$EXT" in
  py)
    if command -v ruff >/dev/null 2>&1; then
      ruff check --fix "$FILE_PATH" >&2 || true
    else
      echo "[lint] ruff not available — skipping Python lint for $FILE_PATH" >&2
    fi
    ;;
  ts|tsx|js|jsx)
    if command -v npx >/dev/null 2>&1; then
      npx biome check --write "$FILE_PATH" >&2 || true
    else
      echo "[lint] npx not available — skipping JS/TS lint for $FILE_PATH" >&2
    fi
    ;;
  go)
    if command -v gofmt >/dev/null 2>&1; then
      gofmt -w "$FILE_PATH" || true
    else
      echo "[lint] gofmt not available — skipping Go format for $FILE_PATH" >&2
    fi
    ;;
  java)
    # No-op: defer to IDE formatter
    echo "[lint] Java file detected — skipping (use IDE formatter)" >&2
    ;;
  *)
    # Not a target file type — exit silently
    exit 0
    ;;
esac

exit 0
