# Phase 04 instructor notes

## Key design decisions

| Decision | Why |
|---|---|
| Normalize before validating | `" API "` and `"api"` are the same tag. Validate the normalized value so the error message matches what would be stored. |
| Tags only exist while used | The list query joins through `post_tags`, so orphans never show (T-15). No cleanup job needed for correctness. |
| Omitted `tags` on PUT keeps the set | PUT is a full replacement for title and content, but tags were added later; clearing them on every old client's PUT would be data loss. Good conversation about contract evolution and backwards compatibility. The gRPC variant needs an explicit `replace_tags` flag because proto3 cannot tell absent from empty. |
| Unknown tag is an empty page | Browsing a tag is a search, and an empty search result is not an error. Compare with phase 03, where a missing post is a 404. |

## Common mistakes

| Symptom | Cause |
|---|---|
| T-01 count is 3 | Dedup before normalization, or a case-sensitive set. |
| T-01 order wrong | Tags returned in insertion order. Sort on output. |
| T-07 clears tags | DTO default `tags = []` makes "absent" look like "empty". Use `Optional`/nullable (`List<String> tags` null check, `*[]string` in Go, `tags?: string[]` in TypeScript, `tags: list[str] | None = None` in Pydantic). |
| Unique violation under load | Insert-then-select without `ON CONFLICT DO NOTHING` (or JPA `merge` race). |
| T-10 `postCount` too high | Counting `post_tags` rows that point at deleted posts (no cascade on the join table). |
| T-13 fails | Path value not lowercased before lookup. |
| N+1 on post lists | Tags loaded per post. Batch them for the whole page. |

## Review prompts

- "Two people create posts tagged `go` at the same moment. Walk me through the SQL."
- "What does a post list page of 10 cost in queries now?"
