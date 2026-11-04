# Phase 03: Comments

**Time:** 60 to 90 minutes. **Grader:** `exercises/engineer/run-acceptance.sh 03`

## Scenario

Readers discuss posts. Any logged-in user can comment on any post. Comments are listed oldest first, like a conversation. Only the person who wrote a comment can delete it. Deleting a post removes its comments.

## Inputs

- Contract: operations `createComment`, `listComments`, `deleteComment`; schemas `CommentInput`, `Comment`, `CommentPage`.
- Session file: `workspaces/engineer/plans/sessions/session-4-phase-3.md`.

## Task

1. Persist comments with foreign keys to the post and the author.
2. Nested create and list under `/api/posts/{postId}/comments`; a missing post is 404 for both.
3. Flat delete at `/api/comments/{commentId}`, comment author only. The post author is not a moderator in this contract.
4. List uses the same `page` / `pageSize` rules and envelope as posts, oldest first.
5. Deleting a post deletes its comments (database cascade or explicit delete in one transaction).

## Rules checked

| Rule | Requirement |
|---|---|
| C-01 | Comment without a token: 401 |
| C-02 | Comment on an unknown post: 404 `NOT_FOUND` |
| C-03 | Whitespace-only content: 422 naming `content` |
| C-04 | Create returns 201; `postId` is the parent, `authorId` is the token owner (body value ignored) |
| C-05 | List is public, oldest first, correct `total` |
| C-06 | List honours `page` and `pageSize` |
| C-07 | List comments of an unknown post: 404, not an empty list |
| C-10 | Delete without a token: 401 |
| C-11 | Delete by anyone but the comment author, including the post author: 403 |
| C-12 | Comment author deletes: 204; list shrinks; second delete is 404 |
| C-13 | Unknown comment id: 404 |
| C-14 | Deleting a post with comments succeeds (no foreign key error) and its comments are gone |

## Done when

- [ ] `exercises/engineer/run-acceptance.sh 03 --cumulative` passes
- [ ] A migration adds the comments table with `ON DELETE CASCADE` (or the service deletes comments in the same transaction as the post)
- [ ] Unit tests cover the delete permission rule
- [ ] Integration test proves the cascade against a real database

## In-session commands

- `/start-session engineer` on session 4.
- `/engineer-tasks`: migration, create, list, delete, cascade.
- `/engineer-implement`, `/code-review`, `/next-session`.

## Stretch

- Add `commentCount` to Post without an N+1 query (one aggregate query per page).
- Let the post author delete comments on their own posts. Write the contract change first, then the tests, then the code.
- Soft delete comments and show `[deleted]` in the list. Discuss what that does to the graded contract.
