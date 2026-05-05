#!/usr/bin/env bash
# type-check.sh — afterFileEdit hook
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

# Derive project root (directory containing the edited file, walk up to find config)
PROJECT_ROOT=$(dirname "$FILE_PATH")
# Walk up to find project-level config (up to 5 levels)
for _ in 1 2 3 4 5; do
  if [ -f "$PROJECT_ROOT/pyproject.toml" ] || [ -f "$PROJECT_ROOT/mypy.ini" ] || \
     [ -f "$PROJECT_ROOT/tsconfig.json" ] || [ -f "$PROJECT_ROOT/go.mod" ]; then
    break
  fi
  PARENT=$(dirname "$PROJECT_ROOT")
  [ "$PARENT" = "$PROJECT_ROOT" ] && break
  PROJECT_ROOT="$PARENT"
done

case "$EXT" in
  py)
    if command -v mypy >/dev/null 2>&1; then
      if [ -f "$PROJECT_ROOT/mypy.ini" ] || [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
        mypy "$FILE_PATH" >&2 || true
      else
        echo "[type-check] No mypy config found — skipping type check for $FILE_PATH" >&2
      fi
    else
      echo "[type-check] mypy not available — skipping Python type check for $FILE_PATH" >&2
    fi
    ;;
  ts|tsx)
    if command -v npx >/dev/null 2>&1; then
      if [ -f "$PROJECT_ROOT/tsconfig.json" ]; then
        npx tsc --noEmit >&2 || true
      else
        echo "[type-check] No tsconfig.json found — skipping TypeScript type check for $FILE_PATH" >&2
      fi
    else
      echo "[type-check] npx not available — skipping TypeScript type check for $FILE_PATH" >&2
    fi
    ;;
  go)
    if command -v go >/dev/null 2>&1; then
      go vet ./... >&2 || true
    else
      echo "[type-check] go not available — skipping Go vet for $FILE_PATH" >&2
    fi
    ;;
  *)
    # Not a target file type — exit silently
    exit 0
    ;;
esac

exit 0
