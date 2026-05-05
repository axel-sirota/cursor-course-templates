#!/usr/bin/env bash
# block-destructive.sh — beforeShellExecution hook
# Reads command from stdin JSON.
# Returns JSON with permission: deny for destructive commands, allow otherwise.
# This is the ONLY blocking hook — all others are advisory.

set -euo pipefail

# Read stdin JSON
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || true)

deny() {
  local msg="$1"
  python3 -c "
import json
print(json.dumps({
  'continue': True,
  'permission': 'deny',
  'userMessage': '$msg',
  'agentMessage': 'Command blocked by block-destructive.sh hook: $msg'
}))
"
  exit 0
}

allow() {
  python3 -c "import json; print(json.dumps({'continue': True, 'permission': 'allow'}))"
  exit 0
}

# Deny-list checks (order: most dangerous first)

# rm -rf on root, home, or current directory
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+/($|\s)'; then
  deny "Blocked: rm -rf / is not allowed"
fi
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+~'; then
  deny "Blocked: rm -rf ~ is not allowed"
fi
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+\.($|\s)'; then
  deny "Blocked: rm -rf . is not allowed"
fi

# git push --force / git push -f
if echo "$COMMAND" | grep -qE 'git\s+push\s+(.*\s)?--force(\s|$)'; then
  deny "Blocked: git push --force is not allowed"
fi
if echo "$COMMAND" | grep -qE 'git\s+push\s+(.*\s)?-f\s'; then
  deny "Blocked: git push -f is not allowed"
fi

# git reset --hard origin
if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard\s+origin'; then
  deny "Blocked: git reset --hard origin is not allowed"
fi

# SQL destructive statements
if echo "$COMMAND" | grep -qiE 'DROP\s+DATABASE'; then
  deny "Blocked: DROP DATABASE is not allowed"
fi
if echo "$COMMAND" | grep -qiE 'DROP\s+TABLE'; then
  deny "Blocked: DROP TABLE is not allowed"
fi
if echo "$COMMAND" | grep -qiE 'TRUNCATE\s+TABLE'; then
  deny "Blocked: TRUNCATE TABLE is not allowed"
fi

# sudo rm
if echo "$COMMAND" | grep -qE 'sudo\s+rm'; then
  deny "Blocked: sudo rm is not allowed"
fi

# mkfs
if echo "$COMMAND" | grep -qE '(^|\s)mkfs'; then
  deny "Blocked: mkfs is not allowed"
fi

# dd if=
if echo "$COMMAND" | grep -qE '(^|\s)dd\s+if='; then
  deny "Blocked: dd if= is not allowed"
fi

# Default: allow
allow
