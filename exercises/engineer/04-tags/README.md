# Phase 04: Tags

**Time:** about 90 minutes. **Grader:** `exercises/engineer/run-acceptance.sh 04`

## Scenario

Authors tag posts so readers can browse by topic. A post has up to five tags, a tag is shared by many posts (many-to-many). Readers see every tag in use with its post count and can list the posts under a tag.

## Inputs

- Contract: `PostInput.tags`, `Post.tags`, operations `listTags` and `listPostsByTag`, schema `TagSummary`.
- Session file: `workspaces/engineer/plans/sessions/session-5-phase-4.md`.

## Task

1. Add a `tags` table and a `post_tags` join table (unique pair, cascade on post delete).
2. Accept `tags` on create and update. Normalize each tag: trim, lowercase. After normalization it must match `^[a-z0-9][a-z0-9-]{0,29}$`. Duplicates collapse. At most 5.
3. Return `tags` sorted A to Z on every Post.
4. PUT with `tags` replaces the set. PUT without `tags` keeps the current set. `tags: []` clears it.
5. `GET /api/tags`: every tag with at least one post, with `postCount`, sorted by name.
6. `GET /api/tags/{tagName}/posts`: posts with that tag, newest first, paginated. Normalize the path value. Unknown tag is 200 with an empty page.

## Rules checked

| Rule | Requirement |
|---|---|
| T-01 | Tags are trimmed, lowercased, deduplicated, sorted, and persisted |
| T-02 | A post without tags has `tags: []` |
| T-03 | Invalid characters: 422 naming `tags` |
| T-04 | More than 5 distinct tags: 422 |
| T-05 | `tags` not an array of strings: 422 |
| T-06 | PUT with `tags` replaces the set |
| T-07 | PUT without `tags` keeps the set |
| T-08 | PUT with `tags: []` clears the set |
| T-10 | Tag list has each tag once with the right `postCount` |
| T-11 | Posts by tag: right total, newest first |
| T-12 | Posts by tag honours `pageSize` |
| T-13 | Tag lookup in the path ignores case |
| T-14 | Unknown tag: 200, `total` 0, empty `items` |
| T-15 | A tag with zero posts disappears from the tag list |
| T-16 | Deleting a post lowers `postCount` |

## Done when

- [ ] `exercises/engineer/run-acceptance.sh 04 --cumulative` passes
- [ ] Unit tests cover tag normalization (case, spaces, duplicates, limit, bad characters)
- [ ] Creating a post with a new tag and the same tag from two requests at once does not fail on the unique index (upsert)
- [ ] The tag list is one aggregate query, not one count per tag

## In-session commands

- `/start-session engineer` on session 5.
- `/engineer-tasks`: migration, normalizer, create/update wiring, tag list, posts by tag.
- `/engineer-implement`, `/code-review`, `/next-session`.

## Stretch

- `GET /api/tags?prefix=py` for autocomplete.
- Garbage-collect tags with zero posts in a scheduled job instead of hiding them in the query. Which approach is simpler to test?
