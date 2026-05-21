# Phase 2 — Subscriptions

**Goal:** Subscribers can register a webhook URL against a topic and inspect their cursor.

## Tasks
1. `@DataJpaTest` for `SubscriptionRepository.findByActiveTrue` and `findByTopicIdAndActiveTrue`.
2. `SubscriptionService.create` — resolve topic by name; enforce unique `(topic_id, name)`; initialize `lastDeliveredMessageId = current max(messages.id for topic)` so new subscribers don't get full backlog (decision: subscribe-from-now). Document the alternative (replay-from-zero) for later configurability.
3. `SubscriptionService.get` / `deactivate`.
4. `@WebMvcTest(SubscriptionController.class)` — 201/200/204 paths, 400 on bad URL, 404 on unknown topic/sub.
5. Integration test: create topic → create subscription → GET subscription shows cursor = 0 (or current max).

## Done when
- `mvn verify` green.
- `curl -X POST /topics/orders/subscriptions -d '{"name":"billing","webhookUrl":"http://localhost:9000/hook"}'` returns 201.
- `GET /subscriptions/{id}` shows cursor + active=true.
- `DELETE /subscriptions/{id}` → 204; subsequent GET shows active=false.
