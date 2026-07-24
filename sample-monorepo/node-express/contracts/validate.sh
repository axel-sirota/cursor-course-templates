#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "usage: validate.sh <service-dir>" >&2
    exit 2
fi

CONTRACTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the validator and keep its report. On success, pass the report through.
# On failure, send the report to STDERR and exit 2: Stop/SubagentStop hooks only
# BLOCK an agent's stop on exit code 2, and only stderr is fed back to the agent
# as feedback — exit 1 would merely warn and let the agent finish.
if output="$(python3 "${CONTRACTS_DIR}/validate.py" "$1")"; then
    printf '%s\n' "$output"
    exit 0
fi

printf '%s\n' "$output" >&2
exit 2
