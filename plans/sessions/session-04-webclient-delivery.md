# Session 04 — WebClient Delivery (single subscription)

**Phase:** 3 — Dispatcher + Webhook Push
**Estimated effort:** ~75 min
**Depends on:** session-03.

## Goal
`DeliveryService.deliverPending(subscription)` POSTs new messages to the subscriber's webhook and advances the cursor on success.

## Tasks
1. Add `WebClientConfig` with timeouts (connect 2s, read 5s, response 5s).
2. **Red — delivery test** using `okhttp3.mockwebserver.MockWebServer`:
   - Enqueue 3 messages.
   - `deliverPending(sub)` → MockWebServer received 3 POSTs in order with `X-Message-Id`, `X-Subscription-Id` headers.
   - Subscription `lastDeliveredMessageId` advanced to id of message #3.
   - 3 `delivery_attempts` rows with status=SUCCESS.
3. **Red — failure test:**
   - MockWebServer returns 500 on message #2.
   - `deliverPending` delivers #1 (cursor → id1), creates PENDING `DeliveryAttempt` for #2 (cursor stays at id1).
4. **Green — implement** `DeliveryService.deliverPending`:
   - Load batch of messages `id > cursor` ordered ascending.
   - For each: POST via `WebClient`, sync `.block(timeout)`.
   - 2xx → INSERT SUCCESS attempt, UPDATE subscription set `last_delivered_message_id = :newId WHERE id = :subId AND last_delivered_message_id = :oldId` (optimistic).
   - Non-2xx / IO error → INSERT PENDING attempt with `next_attempt_at = now + 1s`, BREAK out of loop (preserve order).
5. Verify with `mvn test`.

## Files touched
- `src/main/java/com/example/broker/dispatch/WebClientConfig.java` (new).
- `src/main/java/com/example/broker/dispatch/DeliveryService.java`.
- `src/main/java/com/example/broker/messages/MessageRepository.java` (`findTop100ByTopicIdAndIdGreaterThanOrderByIdAsc` already there).
- `pom.xml` — add `com.squareup.okhttp3:mockwebserver` (test scope).
- `src/test/java/com/example/broker/dispatch/DeliveryServiceTest.java` (new).

## Done when
- Mock webhook server receives in-order POSTs with correct headers.
- Cursor advance is atomic (verified by concurrent test if time permits).
