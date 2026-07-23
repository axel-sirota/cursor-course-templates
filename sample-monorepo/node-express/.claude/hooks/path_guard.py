#!/usr/bin/env python3
"""PreToolUse hook that keeps an agent inside its own service directory.

Blocks Edit/Write/NotebookEdit calls whose file_path falls outside the
allowed service prefix (argv[1]). Exit code 2 blocks the tool call and
shows stderr to the agent; exit 0 allows it.

Normal invocation (Claude Code pipes the hook event JSON on stdin):

    echo '{"tool_name": "Edit", "tool_input": {"file_path": "services/gateway/x.py"}}' \
        | python3 .claude/hooks/path_guard.py services/payments
    # exit 2, stderr: BLOCKED path_guard: ...

Self-test invocation (no stdin JSON needed — handy in CI and demos):

    python3 .claude/hooks/path_guard.py services/payments --self-test services/payments/src/x.py
    # exit 0 (allowed)
    python3 .claude/hooks/path_guard.py services/payments --self-test services/gateway/x.py
    # exit 2 (blocked)

Allowed paths, for prefix services/<name>:
  - anything under services/<name>/
  - anything under tests/services/<name>/ or fixtures/services/<name>/
  - the same, at any depth: matching is on the path SEGMENTS, so an
    absolute path inside a worktree copy of the repo still matches on
    its services/<name>/ segment rather than on the repo root.
"""
import json
import os
import posixpath
import sys

GUARDED_TOOLS = {"Edit", "Write", "NotebookEdit"}


def _segments(path: str) -> list:
    """Normalize a path and split it into clean segments."""
    clean = posixpath.normpath(path.replace("\\", "/"))
    return [part for part in clean.split("/") if part not in ("", ".")]


def _contains_subsequence(haystack: list, needle: list) -> bool:
    """True if needle appears as a contiguous run inside haystack."""
    if not needle:
        return False
    span = len(needle)
    for start in range(len(haystack) - span + 1):
        if haystack[start:start + span] == needle:
            return True
    return False


def is_allowed(file_path: str, allowed_prefix: str) -> bool:
    """Decide whether file_path is inside the allowed service scope."""
    if not os.path.isabs(file_path):
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
        if project_dir:
            file_path = os.path.join(project_dir, file_path)

    path_parts = _segments(file_path)
    prefix_parts = _segments(allowed_prefix)

    candidates = (
        prefix_parts,                  # services/<name>/...
        ["tests"] + prefix_parts,      # tests/services/<name>/...
        ["fixtures"] + prefix_parts,   # fixtures/services/<name>/...
    )
    return any(_contains_subsequence(path_parts, c) for c in candidates)


def decide(file_path: str, allowed_prefix: str) -> int:
    """Return the hook exit code for a guarded tool call on file_path."""
    if is_allowed(file_path, allowed_prefix):
        return 0
    print(
        f"BLOCKED path_guard: {file_path} is outside your service scope ({allowed_prefix})",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: path_guard.py <allowed-prefix> [--self-test <file_path>]", file=sys.stderr)
        return 1
    allowed_prefix = sys.argv[1]

    if len(sys.argv) >= 4 and sys.argv[2] == "--self-test":
        # Behave exactly as if a PreToolUse Edit event arrived for this path.
        return decide(sys.argv[3], allowed_prefix)

    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"path_guard: could not parse hook JSON: {exc}", file=sys.stderr)
        return 1

    tool_name = event.get("tool_name", "")
    if tool_name not in GUARDED_TOOLS:
        return 0

    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return 0

    return decide(file_path, allowed_prefix)


if __name__ == "__main__":
    sys.exit(main())
