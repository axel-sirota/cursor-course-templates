# Session 05 — Dispatcher Poller (multi-subscription, end-to-end)

**Phase:** 3 — Dispatcher + Webhook Push
**Estimated effort:** ~30 min
**Depends on:** session-04.

## Goal
`DispatcherScheduler` actually wires per-subscription dispatch on every poll tick, so an end-to-end publish → webhook flow works without manual invocation.

## Tasks
1. Update `DispatcherScheduler.pollAndDispatch`:
   - For each `findByActiveTrue()` subscription → `deliveryService.deliverPending(sub)`.
   - Wrap each subscription's call in its own try/catch + log; one bad subscription must not stall the rest.
2. **Integration test** `DispatcherEndToEndTest` (`@SpringBootTest` + Testcontainers):
   - Spin up `MockWebServer`.
   - Create topic + 2 subscriptions (both pointing at MockWebServer but with different `name`s).
   - Publish 1 message.
   - `await().atMost(3, SECONDS).until(() -> mockServer.getRequestCount() == 2)`.
3. Verify cursor advanced for both subscriptions independently.

## Files touched
- `src/main/java/com/example/broker/dispatch/DispatcherScheduler.java`.
- `src/test/java/com/example/broker/dispatch/DispatcherEndToEndTest.java` (new).
- `pom.xml` — add `org.awaitility:awaitility` (test scope).

## Done when
- Publish a message → both subscribers' webhooks called within ~1 second, automatically.
