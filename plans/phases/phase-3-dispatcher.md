# Phase 3 — Dispatcher + Webhook Push

**Goal:** Messages flow from publisher → broker → subscriber's webhook URL. Cursor advances on success.

## Tasks
1. Add `WebClient` bean with sane timeouts (connect 2s, read 5s).
2. `DeliveryService.deliverPending(subscription)`:
   - Load up to `batch-size` messages with `id > subscription.lastDeliveredMessageId`.
   - For each: POST to `webhookUrl` with body = `payload`, headers include `X-Message-Id`, `X-Subscription-Id`, plus original `headers`.
   - On 2xx: persist `DeliveryAttempt(status=SUCCESS)` and advance cursor (atomically — use UPDATE ... WHERE last_delivered_message_id = :prev to avoid lost-update from concurrent pollers).
   - On non-2xx / IO error: persist `DeliveryAttempt(status=PENDING, attempt_no=1, next_attempt_at=now+1s)`; STOP advancing cursor for this subscription this tick (preserves ordering).
3. `DispatcherScheduler.pollAndDispatch` — call `deliverPending` per active subscription.
4. Test: spin up a `MockWebServer` (okhttp) inside an integration test; publish 3 messages; assert webhook received all 3 in order; cursor advanced.

## Done when
- Publishing a message results in a POST to the registered webhook URL within ~1s.
- Cursor in `subscriptions` table updates to the latest delivered id.
- `delivery_attempts` row written per attempt with status=SUCCESS.
