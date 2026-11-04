# Phase 03 instructor notes

## Key design decisions

| Decision | Why |
|---|---|
| Nested create and list, flat delete | Matches the original course API. A comment id is globally unique, so delete does not need the post id. Good moment to discuss when nesting helps and when it is noise. |
| 404 for comments of a missing post | An empty list would hide client bugs (wrong post id) and makes "deleted post" look like "post without comments". |
| Oldest first | Comments are read as a conversation. Posts are a feed (newest first). Same envelope, different default order. |
| Only the comment author deletes | Keeps the permission rule to one line. The moderation stretch makes students change the contract first, which is the real lesson. |
| Cascade on post delete | Orphaned comments are a data integrity bug. C-14 checks it from the outside by deleting the orphan and expecting 404. |

## Common mistakes

| Symptom | Cause |
|---|---|
| C-14 first request returns 409 or 500 | Foreign key without `ON DELETE CASCADE`, and the service deletes the post only. |
| C-14 last request returns 204 or 403 | Comments survived the post delete (cascade missing or soft delete on posts only). |
| C-07 returns 200 with empty items | List query filters by post id without checking the post exists. |
| C-11 returns 204 | Permission check uses the post author, or "author of either". |
| C-05 order wrong | Default sort copied from posts (newest first). |
| N+1 when listing | `authorUsername` loaded per comment. Use a join or a batch lookup. JPA students: `@EntityGraph` or a fetch join; Prisma: `include`. |
| JPA `LazyInitializationException` | Entity returned outside the transaction. Map to DTO inside the service. |

## Review prompts

- "Delete a post with comments. What SQL ran?"
- "How many queries does a page of 10 comments cost?"
