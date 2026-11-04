# Phase 05 instructor notes

## Key design decisions

| Decision | Why |
|---|---|
| `sort` as a closed enum | Never interpolate a sort column from the query string into SQL. Map each allowed value to a fixed `ORDER BY` clause. |
| Substring search with `ILIKE` | Enough for the contract. Leading-wildcard `ILIKE` cannot use a btree index; `pg_trgm` GIN can. Full-text search changes the semantics (stemming), so it is a stretch, not the default. |
| 400 for malformed JSON, 422 for rule breaks | The client needs to know whether it sent garbage or sent valid JSON that broke a rule. Many frameworks blur this; the global error handler fixes it once. |
| 405 with `Allow` | Tells a client it used the wrong verb rather than the wrong path. Most frameworks return 404 for an unmatched method by default. |
| Echo the allowed origin, never `*` | `*` with credentials is rejected by browsers anyway, and a reflected arbitrary origin is a vulnerability. X-18 checks the reflection bug. |
| Request id on errors too | The 500 at 3 a.m. is exactly the response that needs it. |

## Common mistakes

| Symptom | Cause |
|---|---|
| X-01 misses the upper-case title | `LIKE` instead of `ILIKE`, or lowercasing only one side. |
| X-02 order wrong for mixed case | Sorting by raw title with a case-sensitive collation. Sort by `lower(title)`. |
| X-07 returns 200 | Unknown sort silently falls back to the default. |
| SQL injection via `sort` | String-built `ORDER BY`. Show it in `/code-review`. |
| X-10 returns HTML | Framework default 404 page (Spring Whitelabel, Express `Cannot GET`). Spring: `spring.mvc.throw-exception-if-no-handler-found=true` plus a handler, or a catch-all `NoResourceFoundException` handler on Boot 3.2+. Express: a final 404 middleware. Gin: `r.NoRoute`. |
| X-11 returns 422 | FastAPI reports JSON decode errors as `RequestValidationError`. Detect `json_invalid` and return 400. |
| X-13 returns 404 | Gin needs `r.HandleMethodNotAllowed = true` and `r.NoMethod`. Express needs an explicit `.all()` per route. FastAPI and Spring return 405 by default, but with their own body shape. |
| X-16 fails | CORS middleware registered after the auth middleware, so the preflight gets 401. |
| X-18 fails | `origin: true` (Express `cors`), `allowedOriginPatterns("*")` (Spring) or `AllowAllOrigins` (Gin). |
| Container passes locally, fails in CI | App binds to `127.0.0.1` inside the container. Bind `0.0.0.0`. |

## Review prompts

- "Show me the code that turns `sort` into SQL."
- "What does a client see if the database is down?"
- "Which user does the container run as?"
