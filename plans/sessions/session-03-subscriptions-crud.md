# Session 03 — Subscriptions CRUD

**Phase:** 2 — Subscriptions
**Estimated effort:** ~60 min
**Depends on:** session-02.

## Goal
Subscribers can register a webhook URL, GET their record, and DELETE (deactivate).

## Decision to record in spec
**Subscribe-from-now** — new subscriptions initialize `lastDeliveredMessageId = MAX(messages.id WHERE topic_id=...)` so they don't receive backlog. Alternative (replay-from-zero) deferred to a future `replay=true` query param.

## TDD steps
1. **Red — repository test.** Confirm `findByActiveTrue` and `findByTopicIdAndActiveTrue` behave correctly with mixed active/inactive rows.
2. **Red — service test.** `SubscriptionServiceTest`:
   - `create("orders", req)` initializes cursor to current max message id for that topic.
   - Duplicate `(topic, name)` → conflict (409).
   - `get(id)` returns DTO; missing id → `EntityNotFoundException` (404).
   - `deactivate(id)` flips `active` to false; subsequent `get` reflects it.
3. **Green — implement service.**
4. **Red — controller test.** `@WebMvcTest`:
   - `POST /topics/orders/subscriptions` 201 happy path.
   - 400 on missing/invalid `webhookUrl` (must start with http/https).
   - 404 on unknown topic.
   - `GET /subscriptions/{id}` 200, `DELETE /subscriptions/{id}` 204.
5. **Green — verify.**

## Files touched
- `src/main/java/com/example/broker/subscriptions/SubscriptionService.java`.
- `src/test/java/com/example/broker/subscriptions/*` (new).

## Done when
- `mvn verify` green.
- End-to-end: publish 5 messages → create subscription → `GET /subscriptions/{id}` shows `lastDeliveredMessageId = 5`.
