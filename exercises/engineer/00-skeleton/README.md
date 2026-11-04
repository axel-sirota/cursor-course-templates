# Phase 00: Skeleton

**Time:** 60 to 90 minutes. **Grader:** `exercises/engineer/run-acceptance.sh 00`

This file is also the plan you hand to `/architect`. It describes the whole Blog API so the architect can write one session file per phase.

## Scenario

Your team is building the Blog API: users register and log in, write posts, comment on posts and tag them. The contract is fixed and lives in [`../contract/openapi.yaml`](../contract/openapi.yaml) (gRPC teams: [`../contract/grpc/blog.proto`](../contract/grpc/blog.proto)). Every engineer builds the same API. You build it in the stack you picked with `/setup-stack engineer`.

Phase 00 is the walking skeleton: every route exists, answers with the right status code and returns mock data in the right shape. No database, no real auth yet.

## Inputs

| Input | Where |
|---|---|
| HTTP contract | `exercises/engineer/contract/openapi.yaml` |
| gRPC contract (go-grpc only) | `exercises/engineer/contract/grpc/blog.proto` |
| Stack specifics (port, layout, traps) | `exercises/engineer/STACK_NOTES.md` |
| Your workspace | `workspaces/engineer/` |

## Plan for /architect

Run:

```
/architect engineer exercises/engineer/00-skeleton/README.md
```

The architect should produce these sessions. Each session maps to one exercise folder and one grader.

| Session file | Phase | Exercise folder | Scope |
|---|---|---|---|
| `session-1-phase-0.md` | 0 Skeleton | `00-skeleton` | All 14 operations stubbed with mock data, health check, test runner wired |
| `session-2-phase-1.md` | 1 Authentication | `01-auth` | Register, login (JWT), me, password hashing, persistence |
| `session-3-phase-2.md` | 2 Posts CRUD | `02-posts` | Create, list (paginated, authorId filter), get, update and delete (author only) |
| `session-4-phase-3.md` | 3 Comments | `03-comments` | Add, list (paginated), delete (comment author only), cascade on post delete |
| `session-5-phase-4.md` | 4 Tags | `04-tags` | Tags on posts (many-to-many), tag list with counts, posts by tag |
| `session-6-phase-5.md` | 5 Polish and deploy | `05-polish` | Search, sort, tag filter, error handling, request ids, CORS, Docker |

The interface contract (`workspaces/engineer/plans/interface-contract.md`) must point at `exercises/engineer/contract/openapi.yaml` instead of redesigning it. Copy the file into your workspace (see STACK_NOTES for where) and treat it as read-only.

The 14 operations:

| Method | Path | Phase | Auth |
|---|---|---|---|
| GET | `/health` | 00 | public |
| POST | `/api/auth/register` | 01 | public |
| POST | `/api/auth/login` | 01 | public |
| GET | `/api/auth/me` | 01 | bearer |
| POST | `/api/posts` | 02 | bearer |
| GET | `/api/posts` | 02 | public |
| GET | `/api/posts/{postId}` | 02 | public |
| PUT | `/api/posts/{postId}` | 02 | bearer, author only |
| DELETE | `/api/posts/{postId}` | 02 | bearer, author only |
| POST | `/api/posts/{postId}/comments` | 03 | bearer |
| GET | `/api/posts/{postId}/comments` | 03 | public |
| DELETE | `/api/comments/{commentId}` | 03 | bearer, comment author only |
| GET | `/api/tags` | 04 | public |
| GET | `/api/tags/{tagName}/posts` | 04 | public |

## Task

1. Run `/architect` as above, review the plans, approve.
2. Let the architect scaffold the skeleton in `workspaces/engineer/`.
3. Make every stub return the success status and a body that matches the contract schema: `201` for creates, `204` with an empty body for deletes, the pagination envelope (`items`, `page`, `pageSize`, `total`, `totalPages`) for lists, `{"status":"ok"}` for health.
4. Stubs accept any bearer token for now. Login returns any non-empty `accessToken`.
5. Write one unit or HTTP test per stub in your stack's test framework.

## Rules checked

| Rule | What the grader checks |
|---|---|
| S-01 | `GET /health` returns 200 JSON `{"status":"ok"}` |
| S-02 | Register returns 201 with `id`, `username`, `email`, `createdAt` as strings |
| S-03 | Login returns 200 with `accessToken`, `tokenType: "Bearer"`, integer `expiresIn`, embedded `user` |
| S-04 | Me returns 200 and a User |
| S-05 | Create post returns 201 with string fields and a `tags` array |
| S-06 | List posts returns the pagination envelope with integer meta fields |
| S-07, S-08 | Get and update post return 200 and a Post |
| S-09, S-10 | Add comment returns 201; list comments returns the envelope |
| S-11, S-14 | Delete comment and delete post return 204 |
| S-12, S-13 | Tag list returns `{"items":[...]}`; posts by tag returns the envelope |

The phase 00 grader is the regression floor: your finished API must still pass it.

## Done when

- [ ] `workspaces/engineer/plans/` has the overview, six session files and the interface contract
- [ ] The server starts on `BASE_URL` (default `http://localhost:8000`) with one command, written in your workspace README
- [ ] `exercises/engineer/run-acceptance.sh 00` passes
- [ ] Your own test suite runs green with your stack's test command
- [ ] gRPC teams: `exercises/engineer/run-acceptance.sh 00 --grpc` passes

## In-session commands

- `/start-session engineer`, then `/engineer-tasks` to split the skeleton session into tasks (one per route group).
- `/engineer-implement` for each task, red then green.
- `/code-review` on the diff, then `/next-session`.

## Stretch

- Serve the contract file at `GET /openapi.yaml` so tooling can find it.
- Run Schemathesis against your stubs (see the main README). Mock data that breaks the schema shows up at once.
