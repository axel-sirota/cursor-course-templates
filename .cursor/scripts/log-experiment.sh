#!/usr/bin/env bash
# log-experiment.sh — Advisory reminder to log experiment results at session end.
# Triggered by the stop hook. No file_path input needed.
# Non-blocking: exits 0 always, message goes to stderr.

set -euo pipefail

echo "ADVISORY [log-experiment]: Session ended. Run /ds-handoff or invoke experiment-tracker to log results before your next session." >&2

exit 0
