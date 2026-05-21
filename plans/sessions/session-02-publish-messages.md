# Session 02 — Publish Messages

**Phase:** 1 — Topics + Publish
**Estimated effort:** ~45 min
**Depends on:** session-01 logically, but **runnable in parallel** — see "Parallel with session-01" below.

## Parallel with session-01

This session does **not** need `TopicService.create` to work. It only needs `TopicRepository.findByName`, which already exists from the Phase 0 skeleton. Seed topics directly via the repository in test setup:

```java
@Autowired TopicRepository topics;
@BeforeEach void seed() { topics.save(new Topic("orders")); }
// then POST /topics/orders/messages
```

Branch off `main` (Phase 0 skeleton) in parallel with session-01. No file conflicts: S1 owns `topics/TopicService.java` + `topics/*Test.java`; S2 owns `messages/MessageService.java` + `messages/*Test.java`. Either order of merge is fine.

## Goal

`POST /topics/{name}/messages` persists a row in `messages` and returns the assigned id.

## TDD steps

1. **Red — service test.** `MessageServiceTest`:
   - `publish("orders", payload)` returns id > 0, publishedAt set.
   - `publish("does-not-exist", payload)` throws `EntityNotFoundException`.
   - Two publishes get strictly increasing ids.
2. **Green — implement `MessageService.publish`:** look up topic by name, persist `Message`, return DTO.
3. **Red — controller test.** `@WebMvcTest(PublishController.class)`:
   - 202 happy path.
   - 404 unknown topic.
   - 400 missing `payload`.
4. **Green — verify.**
5. **Red — full integration test** (`@SpringBootTest` + Testcontainers):
   - Seed topic via `TopicRepository` in `@BeforeEach` → POST 3 messages → query `messages` table → 3 rows in order.

## Files touched

- `src/main/java/com/example/broker/messages/MessageService.java`.
- `src/test/java/com/example/broker/messages/{MessageServiceTest,PublishControllerTest,PublishIntegrationTest}.java` (new).

## Done when

- `mvn verify` green.
- `curl -X POST localhost:8080/topics/orders/messages -d '{"payload":{"orderId":"42"}}' -H 'Content-Type: application/json'` → 202 with id.
