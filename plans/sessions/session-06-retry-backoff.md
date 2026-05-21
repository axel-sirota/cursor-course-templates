# Session 06 — Retry with Exponential Backoff

**Phase:** 4 — Retry + DLQ
**Estimated effort:** ~75 min
**Depends on:** session-05.

## Goal
Failed deliveries retry on the schedule `[1s, 5s, 30s, 2m, 10m]`. After attempt 5 still failing, the message is moved to `dead_letter` and the cursor advances past it (skip-and-DLQ semantics — documented trade-off vs. head-of-line blocking).

## Tasks
1. Externalize backoff schedule from `application.yml` (`broker.retry.backoff-seconds` already present).
2. **Unit test** `RetryPolicyTest`: given attempt_no N → expected delay matches schedule; attempt_no >= max → "exhausted".
3. **Red — integration test** with MockWebServer returning 500 forever:
   - Publish 1 message → over time, 5 delivery_attempts created with increasing next_attempt_at gaps.
   - After 5th failure → `dead_letter` row inserted; subscription cursor advanced past this message.
   - Publish a 2nd message → it delivers successfully on the first attempt (cursor advanced past the DLQ'd one).
4. **Green — implement `DeliveryService.retryFailed`:**
   - Query `delivery_attempts WHERE status=PENDING AND next_attempt_at <= now()` (limit batch).
   - For each: POST; on success → mark SUCCESS, advance cursor only if this message_id is `cursor + 1` (otherwise leave cursor for ordered advance to catch up).
   - On failure: if `attempt_no < max` → bump and reschedule; else INSERT `DeadLetter`, mark attempt FAILED, advance cursor.
5. Add a second `@Scheduled(fixedDelayString = "${broker.retry.poll-interval-ms:5000}")` to `DispatcherScheduler` calling `retryFailed`.

## Files touched
- `src/main/java/com/example/broker/dispatch/{RetryPolicy,DeliveryService,DispatcherScheduler}.java`.
- `src/main/java/com/example/broker/deadletter/DeadLetterRepository.java` (already there).
- `src/test/java/com/example/broker/dispatch/{RetryPolicyTest,RetryIntegrationTest}.java` (new).

## Done when
- `mvn verify` green.
- Integration test demonstrates 5-attempt retry + DLQ promotion + cursor-skip in <30 real seconds (tune backoff in test profile, e.g. `[10ms, 20ms, 40ms, 80ms, 160ms]`).
