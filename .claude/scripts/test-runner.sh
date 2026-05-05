#!/usr/bin/env bash
# test-runner.sh — stop hook
# Triggered by stop event. No file_path needed. Non-blocking (exit 0 always).

set -euo pipefail

# Determine project root — start from cwd
PROJECT_ROOT="$(pwd)"

RAN=0

# Python: pyproject.toml or setup.py
if [ -f "$PROJECT_ROOT/pyproject.toml" ] || [ -f "$PROJECT_ROOT/setup.py" ]; then
  echo "[test-runner] Detected Python project — running pytest" >&2
  if command -v pytest >/dev/null 2>&1; then
    pytest -x --tb=short || echo "[test-runner] WARNING: pytest reported failures — review output above" >&2
  else
    echo "[test-runner] pytest not available — skipping Python tests" >&2
  fi
  RAN=1
fi

# Node: package.json with "test" script
if [ -f "$PROJECT_ROOT/package.json" ]; then
  HAS_TEST=$(python3 -c "import json; d=json.load(open('$PROJECT_ROOT/package.json')); print('yes' if 'test' in d.get('scripts',{}) else 'no')" 2>/dev/null || echo "no")
  if [ "$HAS_TEST" = "yes" ]; then
    echo "[test-runner] Detected Node project — running npm test" >&2
    if command -v npm >/dev/null 2>&1; then
      npm test --silent || echo "[test-runner] WARNING: npm test reported failures — review output above" >&2
    else
      echo "[test-runner] npm not available — skipping Node tests" >&2
    fi
    RAN=1
  fi
fi

# Go: go.mod
if [ -f "$PROJECT_ROOT/go.mod" ]; then
  echo "[test-runner] Detected Go project — running go test" >&2
  if command -v go >/dev/null 2>&1; then
    go test ./... || echo "[test-runner] WARNING: go test reported failures — review output above" >&2
  else
    echo "[test-runner] go not available — skipping Go tests" >&2
  fi
  RAN=1
fi

if [ "$RAN" -eq 0 ]; then
  echo "[test-runner] No supported test runner detected — skipping" >&2
fi

exit 0
