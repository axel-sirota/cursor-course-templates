#!/usr/bin/env python3
"""PostToolUse hook that appends one JSON line per tool call to
logs/tool_usage.jsonl under CLAUDE_PROJECT_DIR.

Wired in .claude/settings.json (PostToolUse, matcher "*"):

    python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/agent_activity.py

Each line records: ts (UTC ISO-8601), session_id, agent (from
CLAUDE_AGENT_NAME, "main" when unset), tool_name, the file_path or
command it touched (truncated to 120 chars), and success. Watch several
agents work in parallel with:

    tail -f logs/tool_usage.jsonl

This hook never fails the tool call: any internal error prints a
warning to stderr and exits 0.
"""
import json
import os
import sys
from datetime import datetime, timezone

TARGET_MAX = 120  # keep each log line short enough for a readable tail


def build_entry(event: dict) -> dict:
    tool_input = event.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("command") or ""
    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": event.get("session_id", "unknown"),
        "agent": os.environ.get("CLAUDE_AGENT_NAME", "main"),
        "tool_name": event.get("tool_name", "unknown"),
        "target": target[:TARGET_MAX],
        "success": (event.get("tool_response") or {}).get("success", True),
    }


def main() -> int:
    try:
        event = json.load(sys.stdin)
        entry = build_entry(event)
        log_file = os.path.join(
            os.environ.get("CLAUDE_PROJECT_DIR", "."), "logs", "tool_usage.jsonl"
        )
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
    except Exception as exc:  # noqa: BLE001 — a logging hook must never block the tool call
        print(f"agent_activity: warning, could not log tool call: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
