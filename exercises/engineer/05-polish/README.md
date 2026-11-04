# Phase 05: Polish and deploy

**Time:** 90 to 120 minutes. **Grader:** `exercises/engineer/run-acceptance.sh 05` (or `all` for the full regression)

## Scenario

The API works. Before it ships: readers want search and sorting, the frontend team needs CORS, on-call needs request ids in every response, and errors must be predictable JSON with no stack traces. The service runs in a container.

## Inputs

- Contract: `listPosts` parameters `q`, `tag`, `sort`; the conventions block at the top of `openapi.yaml`; the `Error` schema.
- Session file: `workspaces/engineer/plans/sessions/session-6-phase-5.md`.
- Environment: `CORS_ORIGINS` (comma separated, default `http://localhost:3000`).

## Task

1. `GET /api/posts?q=` case-insensitive substring search on title or content.
2. `GET /api/posts?tag=` filter, normalized like stored tags.
3. `sort` one of `-createdAt` (default), `createdAt`, `title`, `-title`. Unknown value: 422 on `sort`.
4. Filters combine with AND, pagination applies after filtering.
5. Error handling: unknown routes are 404 JSON envelopes; malformed JSON is 400 `MALFORMED_JSON`; a known path with an unsupported method is 405 `METHOD_NOT_ALLOWED` with an `Allow` header; no stack traces or exception names in any body.
6. `X-Request-Id`: echo the client value, or generate one, on every response including errors. Log it.
7. CORS from `CORS_ORIGINS`: echo an allowed `Origin`, answer preflights with 200 or 204, never send `*`, send nothing for other origins.
8. Docker: a multi-stage `Dockerfile` and a `docker-compose.yml` with the API and Postgres. The grader must pass against the container.

## Rules checked

| Rule | Requirement |
|---|---|
| X-01 | `q` matches title or content, ignoring case |
| X-02 | `tag` filter with `sort=title` (A to Z) |
| X-03 | `sort=-title` is Z to A |
| X-04 | `sort=createdAt` is oldest first |
| X-05 | Default sort is newest first |
| X-06 | `q`, `tag`, `sort` and `pageSize` combine; pagination after filtering |
| X-07 | Unknown `sort`: 422 naming `sort` |
| X-10 | Unknown route: 404 JSON envelope |
| X-11 | Malformed JSON: 400 `MALFORMED_JSON` |
| X-12 | No `Traceback`, `Exception` or `goroutine` text in error bodies |
| X-13 | PATCH on a post: 405 `METHOD_NOT_ALLOWED` with `Allow` listing `PUT` |
| X-14 | Client `X-Request-Id` is echoed |
| X-15 | Server generates `X-Request-Id` when missing, on success and on errors |
| X-16 | CORS preflight from `http://localhost:3000` succeeds and echoes the origin |
| X-17 | Normal responses to an allowed origin carry `Access-Control-Allow-Origin` |
| X-18 | A disallowed origin gets no `Access-Control-Allow-Origin` |

## Done when

- [ ] `exercises/engineer/run-acceptance.sh all` passes against the local server
- [ ] `docker compose up -d` then `BASE_URL=http://localhost:8000 exercises/engineer/run-acceptance.sh all` passes against the container
- [ ] The image runs as a non-root user and holds no build tools
- [ ] Search uses an index you can explain (`pg_trgm` GIN or a full-text index), or you can explain why it does not need one yet
- [ ] Logs are structured and include the request id

## In-session commands

- `/start-session engineer` on session 6.
- `/engineer-tasks`: search and sort, error handler, request id middleware, CORS, Dockerfile and compose.
- `/engineer-implement`, `/code-review` (security focus on CORS and error bodies), `/next-session`.
- `/dockerize` can draft the Dockerfile and compose file for your stack.

## Stretch

- Run Schemathesis against the container (command in the main README) and fix whatever it finds.
- Add `/ready` that checks the database, separate from `/health`.
- Graceful shutdown: in-flight requests finish on SIGTERM.
