#!/usr/bin/env bash
# invest-validator.sh
# Reads a file_path from stdin JSON.
# Fires only on markdown files under prds/ or docs/prds/ or specs/ or docs/specs/.
# Checks that every line starting with "As a" or "As an" contains
# both "I want" and "so that".
# All findings are advisory: warns to stderr, exits 0.

set -euo pipefail

# Read the full stdin payload
input=$(cat)

# Extract file_path from JSON
file_path=$(echo "$input" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null || true)

if [ -z "$file_path" ]; then
  exit 0
fi

# Only fire on matching path patterns
if ! echo "$file_path" | grep -qE '(prds/[^/]+\.md|specs/[^/]+\.md|docs/prds/[^/]+\.md|docs/specs/[^/]+\.md)$'; then
  exit 0
fi

# File must exist and be readable
if [ ! -f "$file_path" ]; then
  exit 0
fi

line_num=0
found_issue=false

while IFS= read -r line; do
  line_num=$((line_num + 1))
  # Check lines starting with "As a" or "As an" (case-sensitive, strip leading whitespace)
  stripped=$(echo "$line" | sed 's/^[[:space:]]*//')
  if echo "$stripped" | grep -qE '^As an? '; then
    has_i_want=false
    has_so_that=false
    echo "$line" | grep -q "I want" && has_i_want=true
    echo "$line" | grep -q "so that" && has_so_that=true
    if [ "$has_i_want" = false ] || [ "$has_so_that" = false ]; then
      missing=""
      [ "$has_i_want" = false ] && missing="'I want'"
      if [ "$has_so_that" = false ]; then
        [ -n "$missing" ] && missing="$missing and 'so that'" || missing="'so that'"
      fi
      echo "[invest-validator] WARNING: Line $line_num in $file_path — user story missing $missing:" >&2
      echo "  $line" >&2
      found_issue=true
    fi
  fi
done < "$file_path"

# Always exit 0 — advisory only
exit 0
