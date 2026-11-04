#!/usr/bin/env bash
# Language-neutral grader for the engineer Blog API exercises.
#
# Usage:
#   exercises/engineer/run-acceptance.sh <phase> [--cumulative] [--grpc] [-- extra hurl args]
#
#   <phase>        00 | 01 | 02 | 03 | 04 | 05 (or 0..5, or a folder name like 02-posts), or "all"
#   --cumulative   also run every earlier phase (regression check)
#   --grpc         go-grpc stack: run contract/grpc/grpc_smoke.sh with grpcurl instead of the HTTP suite
#
# Environment:
#   BASE_URL   where your API listens (default http://localhost:8000)
#   GRPC_ADDR  where your gRPC server listens (default localhost:50051, --grpc only)
#
# Needs: bash and hurl 7+ (https://hurl.dev). grpcurl only for --grpc. No Python.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHASES=(00-skeleton 01-auth 02-posts 03-comments 04-tags 05-polish)

usage() {
  echo "Usage: $0 <00|01|02|03|04|05|all> [--cumulative] [--grpc] [-- extra hurl args]" >&2
  exit 2
}

[ $# -ge 1 ] || usage
target="$1"; shift
cumulative=0; grpc=0; extra=()
while [ $# -gt 0 ]; do
  case "$1" in
    --cumulative) cumulative=1 ;;
    --grpc) grpc=1 ;;
    --) shift; extra=("$@"); break ;;
    *) usage ;;
  esac
  shift
done

# Resolve the phase argument to an index into PHASES.
idx=-1
if [ "$target" = "all" ]; then
  idx=$(( ${#PHASES[@]} - 1 )); cumulative=1
else
  for i in "${!PHASES[@]}"; do
    p="${PHASES[$i]}"
    num="${p%%-*}"
    if [ "$target" = "$p" ] || [ "$target" = "$num" ] || [ "$target" = "$((10#$num))" ]; then
      idx=$i
    fi
  done
fi
if [ "$idx" -lt 0 ]; then
  echo "Unknown phase '$target'. Pick one of: ${PHASES[*]} or all" >&2
  exit 2
fi

if [ "$grpc" -eq 1 ]; then
  if ! command -v grpcurl >/dev/null 2>&1; then
    echo "grpcurl is not installed. Install it with one of:" >&2
    echo "  macOS:   brew install grpcurl" >&2
    echo "  Go:      go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest" >&2
    echo "  Linux / Windows binaries: https://github.com/fullstorydev/grpcurl/releases" >&2
    exit 3
  fi
  exec bash "$HERE/contract/grpc/grpc_smoke.sh" "${PHASES[$idx]%%-*}"
fi

if ! command -v hurl >/dev/null 2>&1; then
  echo "hurl is not installed. Install it with one of:" >&2
  echo "  macOS:   brew install hurl" >&2
  echo "  Windows: winget install hurl   (or scoop install hurl, or choco install hurl)" >&2
  echo "  Linux:   see https://hurl.dev/docs/installation.html (deb, rpm, tarball, cargo install hurl)" >&2
  exit 3
fi
major="$(hurl --version | head -n 1 | awk '{print $2}' | cut -d. -f1)"
if [ "${major:-0}" -lt 7 ] 2>/dev/null; then
  echo "hurl $major.x found; these suites need hurl 7 or newer. Upgrade it first." >&2
  exit 3
fi

BASE_URL="${BASE_URL:-http://localhost:8000}"
BASE_URL="${BASE_URL%/}"
# Lowercase letters and digits only: run_id ends up in usernames and tag names.
run_id="r$(date +%s | tail -c 7)$RANDOM"

files=()
start=$idx
[ "$cumulative" -eq 1 ] && start=0
for (( i=start; i<=idx; i++ )); do
  for f in "$HERE/${PHASES[$i]}"/acceptance/*.hurl; do
    files+=("$f")
  done
done

echo "Grading ${PHASES[$idx]}$([ "$cumulative" -eq 1 ] && echo " (with earlier phases)") against $BASE_URL (run_id=$run_id)"
set +e
hurl --test --variable "base_url=$BASE_URL" --variable "run_id=$run_id" ${extra[@]+"${extra[@]}"} "${files[@]}"
status=$?
set -e
if [ "$status" -ne 0 ]; then
  echo
  echo "FAILED. Each failing line above ends with a comment naming the contract rule (for example # P-12)."
  echo "Look the rule up in exercises/engineer/<phase>/README.md and contract/openapi.yaml."
  echo "Connection refused? Start your server first, or set BASE_URL."
fi
exit "$status"
