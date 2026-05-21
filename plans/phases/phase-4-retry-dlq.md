# Phase 4 — Retry + Dead Letter + Admin

**Goal:** Failed deliveries retry with backoff [1s, 5s, 30s, 2m, 10m]; after attempt 5 the message moves to `dead_letter`; admin endpoints let you inspect & replay.

## Tasks
1. `DeliveryService.retryFailed()`:
   - Query `delivery_attempts WHERE status=PENDING AND next_attempt_at <= now()`.
   - For each: retry POST. On success → mark SUCCESS, advance cursor (if this attempt's message_id is `lastDeliveredMessageId + 1`).
   - On failure: if `attempt_no < max-attempts` → bump `attempt_no`, set `next_attempt_at = now + backoff[attempt_no]`, status stays PENDING. Else insert `DeadLetter` row, mark attempt FAILED, advance cursor past this message (skip-and-DLQ semantics — document this trade-off).
2. `DispatcherScheduler` — call `retryFailed()` every 5s (separate `@Scheduled`).
3. `DeadLetterService.list` / `replay` — replay inserts a fresh PENDING `DeliveryAttempt` with `next_attempt_at = now`.
4. Tests:
   - Unit: backoff schedule.
   - Integration: MockWebServer returns 500 five times → DLQ row created; subscription cursor advances past the failed message; new message after still delivers.
   - Integration: `POST /admin/dead-letter/{id}/replay` causes re-attempt and (with MockWebServer now returning 200) success.

## Done when
- `mvn verify` green.
- `curl /admin/dead-letter` shows entries after exhausted retries.
- Replay endpoint re-delivers successfully.
