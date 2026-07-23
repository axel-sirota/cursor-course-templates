#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "usage: validate.sh <service-dir>" >&2
    exit 2
fi

CONTRACTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${CONTRACTS_DIR}/validate.py" "$1"
