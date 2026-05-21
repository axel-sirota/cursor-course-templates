# Phase 1 — Topics + Publish

**Goal:** Real persistence for topics and messages. `/topics` and `/topics/{name}/messages` work end-to-end.

## Tasks (TDD: red → green per task)
1. `@DataJpaTest` for `TopicRepository.findByName` / `existsByName`.
2. `TopicService.create` — reject duplicates with `409 Conflict`; persist; return DTO.
3. `TopicService.list` — return all topics sorted by name.
4. `@WebMvcTest(TopicController.class)` — happy path + validation 400.
5. `MessageService.publish(topicName, request)` — resolve topic by name (404 if missing), persist `Message`, return DTO with assigned id + publishedAt.
6. `@WebMvcTest(PublishController.class)` — 202 Accepted, 404 on unknown topic, 400 on bad payload.
7. Integration test: POST topic → POST message → DB row count = 1.

## Done when
- `mvn verify` green.
- `curl -X POST /topics -d '{"name":"orders"}'` returns 201.
- `curl -X POST /topics/orders/messages -d '{"payload":{"x":1}}'` returns 202 with id.
