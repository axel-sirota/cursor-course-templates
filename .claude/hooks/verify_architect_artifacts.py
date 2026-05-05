#!/usr/bin/env python3
"""
Stop hook: blocks Claude from finishing if /architect ran but session files are missing.
Only activates when plans/ directory exists (meaning /architect has started work).
"""
import json, os, sys

event = json.load(sys.stdin)

# Critical: prevent infinite loop when hook already forced a continuation
if event.get("stop_hook_active", False):
    sys.exit(0)

plans_dir = os.path.join(os.getcwd(), "plans")
sessions_dir = os.path.join(plans_dir, "sessions")

# Only enforce if plans/ exists — otherwise /architect hasn't run yet
if not os.path.isdir(plans_dir):
    sys.exit(0)

missing = []

if not os.path.isdir(sessions_dir):
    missing.append("plans/sessions/ directory")
else:
    session_files = [f for f in os.listdir(sessions_dir) if f.endswith(".md")]
    if not session_files:
        missing.append("plans/sessions/ has no .md session files")
    elif not any("session-1" in f or "phase-0" in f for f in session_files):
        missing.append("plans/sessions/session-1-phase-0.md (Phase 0 session)")

if not os.path.isfile(os.path.join(plans_dir, "interface-contract.md")):
    missing.append("plans/interface-contract.md")

if missing:
    print(json.dumps({
        "decision": "block",
        "reason": (
            "Architect artifacts missing — create these before finishing:\n"
            + "\n".join(f"  • {m}" for m in missing)
        )
    }))

sys.exit(0)
