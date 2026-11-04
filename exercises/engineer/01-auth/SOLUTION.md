# Phase 01 instructor notes

## Key design decisions

| Decision | Why |
|---|---|
| Unique username and email ignoring case | `Alice` and `alice` as two accounts is a phishing gift. Enforce it in the database (unique index on `lower(username)` / `citext`), not only in code, or two concurrent registers both win. |
| One error for unknown user and wrong password | Prevents user enumeration through login. Point out that register still reveals existence through 409; that is a product trade-off the contract accepts. |
| 72-byte password limit | bcrypt ignores bytes after 72. Without the limit two different long passwords can match. Bytes, not characters: emoji count as 4. |
| HS256 pinned | Tokens must be verified with the expected algorithm. Libraries that read `alg` from the header and accept `none` are the classic hole (A-25). |
| `sub` is the user id, not the username | Usernames can change later; ids do not. |
| 401 vs 403 | 401 means "who are you?" (missing or bad token). 403 means "I know you, and no". Phase 02 needs 403; phase 01 must never return 403 for a missing token. |

## Common mistakes

| Symptom | Cause |
|---|---|
| A-02 fails | Entity or ORM model serialized directly. Spring: entity returned from controller. Prisma: `select` missing. Use a response DTO. |
| A-05 fails with 400 | Framework default validation status. Spring `MethodArgumentNotValidException` and Nest `ValidationPipe` default to 400; FastAPI returns 422 but with its own `detail` shape. All need a global handler that maps to the envelope. |
| A-05 fields named `user_name` or `Username` | Field naming drift. Fields are the camelCase JSON names. |
| A-21 returns 403 | Spring Security default entry point for anonymous users. Configure an `AuthenticationEntryPoint` that returns 401 with the envelope. |
| A-22 returns 500 | Token parse exception not caught (Go `jwt.Parse` error ignored, Java `JwtException` unhandled). |
| A-24 passes locally, fails in CI | Secret hardcoded in tests and in the app, or defaulted to an empty string. |
| A-25 passes by accident | Library rejects `none` by default (most do now). Ask the student to show where the algorithm is pinned anyway. |
| A-03 race | Check-then-insert without a unique index. Two parallel registers both succeed. Show it with two `curl &` calls. |

## Review prompts

- "Where does the secret come from, and what happens when it is missing?"
- "Show me the line that rejects an expired token."
- "What does the database row for a user contain?"

## Timing

The error envelope eats the most time, because every stack's validation layer has its own default shape. Encourage students to build the global error handler as task 1 of this session: it pays off in every later phase.
