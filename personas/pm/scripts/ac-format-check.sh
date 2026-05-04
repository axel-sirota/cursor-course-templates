#!/usr/bin/env bash
# ac-format-check.sh
# Reads a file_path from stdin JSON.
# Fires only on markdown files under prds/ or docs/prds/ or specs/ or docs/specs/.
# Checks that every user story section (containing "As a") is followed by
# at least one Given/When/Then block within 10 lines.
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

# Read the file into an array
mapfile -t lines < "$file_path"
total=${#lines[@]}

for ((i=0; i<total; i++)); do
  line="${lines[$i]}"
  stripped=$(echo "$line" | sed 's/^[[:space:]]*//')

  # Detect a user story line
  if echo "$stripped" | grep -qE '^As an? '; then
    story_line=$((i + 1))
    # Look ahead up to 10 lines for Given/When/Then
    found_gwt=false
    end=$((i + 10))
    [ $end -ge $total ] && end=$((total - 1))
    for ((j=i; j<=end; j++)); do
      ahead="${lines[$j]}"
      if echo "$ahead" | grep -qiE '(\*\*Given\*\*|\*\*When\*\*|\*\*Then\*\*|- Given|- When|- Then|^Given |^When |^Then )'; then
        found_gwt=true
        break
      fi
    done
    if [ "$found_gwt" = false ]; then
      echo "[ac-format-check] WARNING: Line $story_line in $file_path — user story has no Given/When/Then AC within 10 lines:" >&2
      echo "  $line" >&2
    fi
  fi
done

# Always exit 0 — advisory only
exit 0
