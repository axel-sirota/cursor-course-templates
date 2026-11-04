# Phase 02: Posts CRUD

**Time:** about 120 minutes. **Grader:** `exercises/engineer/run-acceptance.sh 02`

## Scenario

Logged-in users write posts. Anyone can read them. Only the author can change or delete a post. Lists are paginated, newest first.

## Inputs

- Contract: operations `createPost`, `listPosts`, `getPost`, `updatePost`, `deletePost`; schemas `PostInput`, `Post`, `PostPage`, `PageMeta`.
- Session file: `workspaces/engineer/plans/sessions/session-3-phase-2.md`.

## Task

1. Persist posts with a foreign key to the author.
2. Create: `authorId` comes from the token. Ignore any `authorId` in the body.
3. Get: unknown ids return 404 whatever their format.
4. Update (PUT, full replacement of title and content) and delete: author only.
5. List: `page` (default 1), `pageSize` (default 10, max 100), optional `authorId` filter, newest first. Response is the pagination envelope.
6. Apply the status precedence for protected writes: **401 > 404 > 403 > 422**.

## Rules checked

| Rule | Requirement |
|---|---|
| P-01 | Create without a token: 401 |
| P-02 | Create returns 201 with every Post field |
| P-03 | `authorId` is the token owner; a client-sent `authorId` is ignored |
| P-04 | Get is public and returns the stored post |
| P-05 | Empty body: 422 naming `title` and `content` |
| P-06 | Whitespace-only title: 422 |
| P-07 | Title over 200 characters: 422 |
| P-08 | Wrong JSON type (number for title): 422, no coercion |
| P-10 | Unknown id, UUID-shaped or not: 404 `NOT_FOUND` |
| P-11 | PUT without a token: 401 |
| P-12 | PUT by a non-author: 403 `FORBIDDEN` |
| P-13 | Non-author with an invalid body still gets 403 (ownership before validation) |
| P-14 | PUT on a missing post: 404 |
| P-15 | PUT is a full replacement: missing `content` is 422 |
| P-16 | Author PUT returns 200 and persists |
| P-17 | DELETE by a non-author: 403 and the post survives |
| P-18 | DELETE without a token: 401 |
| P-19 | Author DELETE: 204; then GET and a second DELETE return 404 |
| P-20 | List defaults: `page` 1, `pageSize` 10; `authorId` filter; correct `total` and `totalPages` |
| P-21, P-22 | Pages hold the right posts, newest first |
| P-23 | A page past the end is 200 with empty `items` |
| P-24 | `page` < 1, non-numeric `page`, `pageSize` 0 or over 100: 422 naming the parameter |

## Done when

- [ ] `exercises/engineer/run-acceptance.sh 02 --cumulative` passes
- [ ] Service-layer unit tests cover the ownership rule and the pagination maths (`totalPages` for 0, 1, exact and remainder cases)
- [ ] Integration tests hit a real database for list ordering and filters
- [ ] The list query uses `LIMIT`/`OFFSET` (or keyset) in SQL, not in memory
- [ ] There is an index that serves the default sort

## In-session commands

- `/start-session engineer` on session 3.
- `/engineer-tasks`: one task per operation plus one for the ownership guard and one for pagination.
- `/engineer-implement`, then `/code-review` with attention to authorization paths, then `/next-session`.

## Stretch

- Add `ETag` on `GET /api/posts/{id}` and honour `If-None-Match` with 304.
- Optimistic locking: reject a PUT with a stale `If-Match` with 412.
- Measure the list query with `EXPLAIN` before and after the index.
