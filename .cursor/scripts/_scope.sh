#!/usr/bin/env bash
# _scope.sh — run a persona hook script only when the event belongs to that persona.
#
# Usage (written into .cursor/hooks.json by /set-persona):
#   .cursor/scripts/_scope.sh <role> <script-path>
#
# Rules:
#   afterFileEdit        -> run only if the edited file is under workspaces/<role>/
#   stop                 -> run only if .cursor/.active-session contains <role>
#   anything else        -> always run (e.g. beforeShellExecution safety guards)
#
# stdin is passed through to the wrapped script unchanged; its stdout and exit code are returned.

set -uo pipefail

ROLE="${1:-}"
SCRIPT="${2:-}"

if [ -z "$ROLE" ] || [ -z "$SCRIPT" ]; then
  echo "[_scope] usage: _scope.sh <role> <script>" >&2
  exit 0
fi

if [ ! -x "$SCRIPT" ]; then
  echo "[_scope] $SCRIPT not found or not executable, skipping" >&2
  exit 0
fi

INPUT=$(cat)

field() {
  echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('$1',''))" 2>/dev/null || true
}

EVENT=$(field hook_event_name)

case "$EVENT" in
  afterFileEdit)
    # Payload shape varies across Cursor versions: top-level file_path, tool_input.file_path or tool_input.path.
    FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); t=d.get('tool_input') or {}; print(d.get('file_path') or t.get('file_path') or t.get('path') or '')" 2>/dev/null || true)
    case "$FILE_PATH" in
      workspaces/"$ROLE"/*|*/workspaces/"$ROLE"/*) ;;
      *) exit 0 ;;
    esac
    ;;
  stop)
    ACTIVE=$(cat .cursor/.active-session 2>/dev/null | tr -d '[:space:]')
    if [ "$ACTIVE" != "$ROLE" ]; then
      exit 0
    fi
    ;;
esac

echo "$INPUT" | "$SCRIPT"
