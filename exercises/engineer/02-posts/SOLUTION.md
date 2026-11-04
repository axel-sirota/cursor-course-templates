# Phase 02 instructor notes

## Key design decisions

| Decision | Why |
|---|---|
| `authorId` from the token only | Mass assignment is the bug this phase is built to catch (P-03). DTOs for input must not have an `authorId` field at all. |
| Precedence 401 > 404 > 403 > 422 | Deterministic and testable. Checking ownership before validating the body means a stranger learns nothing about validation rules for a post they cannot touch. Some teams prefer 404 instead of 403 to hide existence; the contract picks 403 so the rule is visible in tests. |
| PUT is full replacement | Matches HTTP semantics and keeps the contract small. PATCH is not in the contract and becomes a 405 in phase 05. |
| Offset pagination with `total` | Familiar and easy to grade. Mention the cost: `COUNT(*)` on big tables and drifting pages under writes. Keyset pagination is a good stretch discussion. |
| Unknown id format is 404 | A string that is not a UUID or not a number is still just "not found". Returning 400 or 500 leaks the storage type. |
| Newest first, stable | Order by `created_at DESC, id DESC` so two posts with the same timestamp still have a fixed order. |

## Common mistakes

| Symptom | Cause |
|---|---|
| P-03 fails | Request DTO reused as entity, or `authorId` read from the body. |
| P-08 passes `42` as `"42"` | Jackson coerces scalars by default. Students need `MapperFeature.ALLOW_COERCION_OF_SCALARS` disabled (or `spring.jackson.mapper.allow-coercion-of-scalars=false`). |
| P-10 returns 400 for `not-a-real-id` | Typed path parameter: Spring `Long`/`UUID` conversion, FastAPI `int`/`UUID` annotation, Nest `ParseIntPipe`/`ParseUUIDPipe`, Gin `strconv` error mapped to 400. Map conversion failures to 404. |
| P-10 returns 500 | Postgres `invalid input syntax for type uuid` bubbling up from the query. |
| P-13 returns 422 | Validation runs before the handler (framework binding). The fix is to validate the body in the service after the ownership check, or to accept a loose DTO and validate it explicitly. Good discussion point about where validation belongs. |
| P-21 order flips | Ordering by `id` with random UUIDs, or missing a tie-breaker. |
| P-23 returns 404 | Empty page treated as not found. |
| P-24 `page=abc` returns 400 | Query binding error not mapped to 422. |
| `totalPages` wrong for 0 items | `ceil(0 / n)` is 0. Integer division without ceiling gives 1 for 3 items of size 2. |

## Review prompts

- "Show me where the author check lives. Is it in the controller or the service?"
- "What SQL does the list endpoint run? Paste it."
- "What stops a user from changing someone else's post by guessing an id?"
