#!/usr/bin/env bash
# protect-raw.sh: afterFileEdit hook for the accountant persona.
# Warns loudly when a file under data/raw/ was edited. Source extracts are read-only.
# The edit has already happened, so this cannot block it. It tells you how to undo it.
# Non-blocking: always exits 0. Messages go to stderr.

set -uo pipefail

INPUT=""
if [ ! -t 0 ]; then
  INPUT="$(cat)"
fi

FILE=""
if [ -n "$INPUT" ]; then
  FILE="$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(d, dict):
    sys.exit(0)
t = d.get("tool_input") or {}
if not isinstance(t, dict):
    t = {}
print(d.get("file_path") or t.get("file_path") or t.get("path") or "")
' 2>/dev/null || true)"
fi
FILE="${FILE:-${FILE_PATH:-}}"

if [ -z "$FILE" ]; then
  exit 0
fi

case "$FILE" in
  data/raw/*|*/data/raw/*)
    {
      echo ""
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "!! WARNING [protect-raw]: a source file in data/raw/ was edited."
      echo "!!   File: $FILE"
      echo "!! data/raw/ is read-only. Source extracts are audit evidence."
      echo "!! Undo it:   git checkout -- \"$FILE\""
      echo "!!   (new, untracked file: move it to data/interim/ instead)"
      echo "!! Put work copies in data/interim/ and results in output/."
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo ""
    } >&2
    ;;
esac

exit 0
