#!/usr/bin/env bash
# gRPC smoke grader for the go-grpc variant of the Blog API.
#
# Usage: contract/grpc/grpc_smoke.sh <phase 00..05>
#   Runs the checks for every phase up to and including <phase>.
# Env:   GRPC_ADDR (default localhost:50051)
# Needs: bash, grpcurl (brew install grpcurl, or go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest)
#
# Your server must register grpc.health.v1.Health and server reflection.
set -uo pipefail

ADDR="${GRPC_ADDR:-localhost:50051}"
PHASE="${1:-05}"
PHASE=$((10#$PHASE))
SVC="blog.v1.BlogService"
RUN="r$(date +%s | tail -c 7)$RANDOM"
pass=0; fail=0

command -v grpcurl >/dev/null 2>&1 || { echo "grpcurl not found. brew install grpcurl" >&2; exit 3; }

ok()  { pass=$((pass + 1)); echo "  ok    $1"; }
bad() { fail=$((fail + 1)); echo "  FAIL  $1"; echo "        $2" | head -c 400; echo; }

# call <method> <json> [token]  -> prints combined output, never exits
call() {
  local method="$1" data="$2" token="${3:-}"
  if [ -n "$token" ]; then
    grpcurl -plaintext -H "authorization: Bearer $token" -d "$data" "$ADDR" "$SVC/$method" 2>&1
  else
    grpcurl -plaintext -d "$data" "$ADDR" "$SVC/$method" 2>&1
  fi
}

# field <name> <text> -> first string value of "name": "value" in grpcurl JSON output
field() {
  printf '%s' "$2" | grep -o "\"$1\": *\"[^\"]*\"" | head -n 1 | cut -d'"' -f4
}

# expect_code <rule> <grpc code name> <output>
expect_code() {
  if printf '%s' "$3" | grep -q "Code: $2"; then ok "$1"; else bad "$1 (expected status $2)" "$3"; fi
}

# expect_ok <rule> <output> -> the call succeeded
expect_ok() {
  if printf '%s' "$2" | grep -q "^ERROR"; then bad "$1 (expected OK)" "$2"; else ok "$1"; fi
}

expect_contains() {
  if printf '%s' "$3" | grep -q -- "$2"; then ok "$1"; else bad "$1 (expected output to contain $2)" "$3"; fi
}

echo "gRPC smoke against $ADDR, phases 00..$(printf '%02d' "$PHASE") (run=$RUN)"

# ------------------------------------------------------------------ phase 00
echo "Phase 00: service surface"
out=$(grpcurl -plaintext -connect-timeout 3 "$ADDR" grpc.health.v1.Health/Check 2>&1)
if printf '%s' "$out" | grep -qiE "context deadline exceeded|connection refused|Failed to dial"; then
  echo "Cannot reach a gRPC server at $ADDR. Start your server or set GRPC_ADDR." >&2
  echo "$out" >&2
  exit 1
fi
expect_contains "G-S01 grpc.health.v1.Health/Check returns SERVING" "SERVING" "$out"
out=$(grpcurl -plaintext "$ADDR" list 2>&1)
expect_contains "G-S02 reflection lists $SVC" "$SVC" "$out"
for m in Register Login GetMe CreatePost ListPosts GetPost UpdatePost DeletePost \
         CreateComment ListComments DeleteComment ListTags ListPostsByTag; do
  out=$(grpcurl -plaintext "$ADDR" describe "$SVC.$m" 2>&1)
  expect_contains "G-S03 $SVC exposes $m" "rpc $m" "$out"
done

# ------------------------------------------------------------------ phase 01
if [ "$PHASE" -ge 1 ]; then
  echo "Phase 01: auth"
  out=$(call Register "{\"username\":\"g_$RUN\",\"email\":\"g_$RUN@example.com\",\"password\":\"correct-horse-g1\"}")
  expect_ok "G-A01 Register returns OK" "$out"
  uid=$(field id "$out")
  if printf '%s' "$out" | grep -qi "password"; then bad "G-A02 Register never returns password material" "$out"; else ok "G-A02 Register never returns password material"; fi
  out=$(call Register "{\"username\":\"G_$RUN\",\"email\":\"x_$RUN@example.com\",\"password\":\"correct-horse-g1\"}")
  expect_code "G-A03 duplicate username (any case) is ALREADY_EXISTS" "AlreadyExists" "$out"
  out=$(call Register "{\"username\":\"no spaces\",\"email\":\"bad\",\"password\":\"short\"}")
  expect_code "G-A05 invalid registration is INVALID_ARGUMENT" "InvalidArgument" "$out"
  out=$(call Login "{\"username\":\"g_$RUN\",\"password\":\"correct-horse-g1\"}")
  expect_ok "G-A10 Login returns OK" "$out"
  token=$(field accessToken "$out")
  expect_contains "G-A10 Login tokenType is Bearer" "\"tokenType\": \"Bearer\"" "$out"
  out=$(call Login "{\"username\":\"g_$RUN\",\"password\":\"wrong-password\"}")
  expect_code "G-A11 wrong password is UNAUTHENTICATED" "Unauthenticated" "$out"
  out=$(call Login "{\"username\":\"ghost_$RUN\",\"password\":\"correct-horse-g1\"}")
  expect_code "G-A12 unknown user is UNAUTHENTICATED (same as wrong password)" "Unauthenticated" "$out"
  out=$(call GetMe "{}" "$token")
  expect_contains "G-A20 GetMe returns the token owner" "$uid" "$out"
  out=$(call GetMe "{}")
  expect_code "G-A21 GetMe without metadata is UNAUTHENTICATED" "Unauthenticated" "$out"
  out=$(call GetMe "{}" "${token}x")
  expect_code "G-A23 GetMe with a tampered token is UNAUTHENTICATED" "Unauthenticated" "$out"

  out=$(call Register "{\"username\":\"h_$RUN\",\"email\":\"h_$RUN@example.com\",\"password\":\"correct-horse-g2\"}")
  out=$(call Login "{\"username\":\"h_$RUN\",\"password\":\"correct-horse-g2\"}")
  other=$(field accessToken "$out")
fi

# ------------------------------------------------------------------ phase 02
if [ "$PHASE" -ge 2 ]; then
  echo "Phase 02: posts"
  out=$(call CreatePost "{\"title\":\"No token\",\"content\":\"x\"}")
  expect_code "G-P01 CreatePost without a token is UNAUTHENTICATED" "Unauthenticated" "$out"
  out=$(call CreatePost "{\"title\":\"gRPC post $RUN\",\"content\":\"hello\"}" "$token")
  expect_ok "G-P02 CreatePost returns OK" "$out"
  pid=$(field id "$out")
  expect_contains "G-P03 authorId is the token owner" "$uid" "$out"
  out=$(call CreatePost "{\"title\":\"   \",\"content\":\"x\"}" "$token")
  expect_code "G-P06 blank title is INVALID_ARGUMENT" "InvalidArgument" "$out"
  out=$(call GetPost "{\"id\":\"$pid\"}")
  expect_contains "G-P04 GetPost returns the post" "$pid" "$out"
  out=$(call GetPost "{\"id\":\"not-a-real-id\"}")
  expect_code "G-P10 unknown id is NOT_FOUND" "NotFound" "$out"
  out=$(call UpdatePost "{\"id\":\"$pid\",\"title\":\"Hijack\",\"content\":\"x\"}" "$other")
  expect_code "G-P12 UpdatePost by a non-author is PERMISSION_DENIED" "PermissionDenied" "$out"
  out=$(call UpdatePost "{\"id\":\"$pid\",\"title\":\"Edited $RUN\",\"content\":\"edited\"}" "$token")
  expect_contains "G-P16 UpdatePost by the author persists the title" "Edited $RUN" "$out"
  out=$(call ListPosts "{\"authorId\":\"$uid\",\"page\":{\"pageSize\":1}}")
  expect_contains "G-P20 ListPosts filters by author and reports meta" "\"pageSize\": 1" "$out"
  out=$(call ListPosts "{\"page\":{\"pageSize\":101}}")
  expect_code "G-P24 pageSize over 100 is INVALID_ARGUMENT" "InvalidArgument" "$out"
fi

# ------------------------------------------------------------------ phase 03
if [ "$PHASE" -ge 3 ]; then
  echo "Phase 03: comments"
  out=$(call CreateComment "{\"postId\":\"$pid\",\"content\":\"first\"}" "$other")
  expect_ok "G-C04 CreateComment returns OK" "$out"
  cid=$(field id "$out")
  out=$(call CreateComment "{\"postId\":\"not-a-real-id\",\"content\":\"x\"}" "$other")
  expect_code "G-C02 comment on an unknown post is NOT_FOUND" "NotFound" "$out"
  out=$(call ListComments "{\"postId\":\"$pid\"}")
  expect_contains "G-C05 ListComments includes the comment" "$cid" "$out"
  out=$(call DeleteComment "{\"id\":\"$cid\"}" "$token")
  expect_code "G-C11 DeleteComment by the post author (not comment author) is PERMISSION_DENIED" "PermissionDenied" "$out"
  out=$(call DeleteComment "{\"id\":\"$cid\"}" "$other")
  expect_ok "G-C12 DeleteComment by the comment author returns OK" "$out"
fi

# ------------------------------------------------------------------ phase 04
if [ "$PHASE" -ge 4 ]; then
  echo "Phase 04: tags"
  out=$(call CreatePost "{\"title\":\"Tagged $RUN\",\"content\":\"x\",\"tags\":[\" Go-$RUN \",\"go-$RUN\",\"rpc-$RUN\"]}" "$token")
  expect_contains "G-T01 tags are trimmed and lowercased" "\"go-$RUN\"" "$out"
  out=$(call ListTags "{}")
  expect_contains "G-T10 ListTags lists the new tag" "\"go-$RUN\"" "$out"
  out=$(call ListPostsByTag "{\"tagName\":\"GO-$RUN\"}")
  expect_contains "G-T13 ListPostsByTag is case-insensitive" "Tagged $RUN" "$out"
  out=$(call CreatePost "{\"title\":\"Bad\",\"content\":\"x\",\"tags\":[\"no spaces!\"]}" "$token")
  expect_code "G-T03 invalid tag is INVALID_ARGUMENT" "InvalidArgument" "$out"
fi

# ------------------------------------------------------------------ phase 05
if [ "$PHASE" -ge 5 ]; then
  echo "Phase 05: search and sort"
  out=$(call ListPosts "{\"q\":\"tagged $RUN\"}")
  expect_contains "G-X01 q matches title case-insensitively" "Tagged $RUN" "$out"
  out=$(call ListPosts "{\"authorId\":\"$uid\",\"sort\":\"POST_SORT_TITLE_ASC\"}")
  expect_contains "G-X02 sort by title is accepted" "\"items\"" "$out"
fi

# Clean up the post from phase 02 (also checks delete).
if [ "$PHASE" -ge 2 ]; then
  out=$(call DeletePost "{\"id\":\"$pid\"}" "$token")
  expect_ok "G-P19 DeletePost by the author returns OK" "$out"
  out=$(call GetPost "{\"id\":\"$pid\"}")
  expect_code "G-P19 deleted post is NOT_FOUND" "NotFound" "$out"
fi

echo
echo "gRPC smoke: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
