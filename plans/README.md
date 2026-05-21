# Plans

Two layers:

- **`phases/`** — high-level milestones. Each phase is a coherent slice of functionality, scoped across multiple sessions. Used by `/next-phase` and for stakeholder summaries.
- **`sessions/`** — concrete TDD work units (~30–75 min each). Self-contained: pre-conditions, red/green steps, files touched, done-when. Used by `/start-session` and `/next-session`.

## Map

| Phase | Sessions |
|---|---|
| Phase 0 — Skeleton (done by `/architect`) | — |
| Phase 1 — Topics + Publish | session-01-topics-crud, session-02-publish-messages |
| Phase 2 — Subscriptions | session-03-subscriptions-crud |
| Phase 3 — Dispatcher + Webhook Push | session-04-webclient-delivery, session-05-dispatcher-poller |
| Phase 4 — Retry + DLQ | session-06-retry-backoff, session-07-dlq-admin |

Start the next chunk with: `/start-session session-01-topics-crud`.
