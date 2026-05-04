#!/usr/bin/env bash
# gap-detector.sh
# Triggered by the stop event — no file_path input.
# Prints an advisory message reminding the PM to validate their PRD.
# Non-blocking: always exits 0.

echo "[gap-detector] Session ended. Run /pm-validate to check PRD completeness before next session." >&2

exit 0
