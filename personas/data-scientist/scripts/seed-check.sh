#!/usr/bin/env bash
# seed-check.sh — Advisory check: warn if no random seed is set in .py or .ipynb files.
# Triggered by afterFileEdit hook. Reads file_path from stdin (JSON) or $FILE_PATH env var.
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

# Only fire on .py and .ipynb files
case "$FILE" in
  *.py|*.ipynb) ;;
  *) exit 0 ;;
esac

# Only fire on files inside notebooks/ directory
case "$FILE" in
  */notebooks/*) ;;
  *notebooks/*) ;;
  notebooks/*) ;;
  *) exit 0 ;;
esac

# Exit if file does not exist
if [ ! -f "$FILE" ]; then
  exit 0
fi

SEED_PATTERN='random\.seed\|np\.random\.seed\|torch\.manual_seed\|tf\.random\.set_seed'

if [[ "$FILE" == *.py ]]; then
  # Check Python source file
  if ! grep -q "$SEED_PATTERN" "$FILE"; then
    echo "WARNING [seed-check]: No random seed found in $FILE" >&2
    echo "  Set a seed before any random operation:" >&2
    echo "    random.seed(42)" >&2
    echo "    np.random.seed(42)" >&2
    echo "    torch.manual_seed(42)" >&2
    echo "    tf.random.set_seed(42)" >&2
  fi
elif [[ "$FILE" == *.ipynb ]]; then
  # Check Jupyter notebook — extract cell source via jq and grep
  if ! command -v jq &>/dev/null; then
    echo "WARNING [seed-check]: jq not found — cannot check seed in $FILE" >&2
    exit 0
  fi
  CELL_SOURCES="$(jq -r '.cells[].source | if type == "array" then join("") else . end' "$FILE" 2>/dev/null || true)"
  if [ -z "$CELL_SOURCES" ]; then
    exit 0
  fi
  if ! echo "$CELL_SOURCES" | grep -q "$SEED_PATTERN"; then
    echo "WARNING [seed-check]: No random seed found in notebook $FILE" >&2
    echo "  Add a seed cell before any random operation:" >&2
    echo "    import random, numpy as np" >&2
    echo "    random.seed(42); np.random.seed(42)" >&2
  fi
fi

exit 0
