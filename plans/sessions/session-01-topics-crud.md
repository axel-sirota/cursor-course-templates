# Session 01 — Topics CRUD

**Phase:** 1 — Topics + Publish
**Estimated effort:** ~45 min

## Goal
Replace the `501` stubs in `TopicService.create` / `list` with real persistence.

## Pre-conditions
- Phase 0 skeleton in place (`mvn test` green).
- Docker running (for testcontainers).

## TDD steps
1. **Red — repository test.** `src/test/java/com/example/broker/topics/TopicRepositoryTest.java`: `@DataJpaTest` asserting `findByName` returns the persisted row and `existsByName` is true after save.
2. **Green — confirm repo already satisfies it** (interface is enough; JPA generates impl).
3. **Red — service test.** `TopicServiceTest` with `@DataJpaTest + @Import(TopicService.class)`:
   - `create("orders")` returns a `Response` with non-null id.
   - `create("orders")` again throws `DataIntegrityViolationException` (or a domain `TopicAlreadyExistsException` — your choice; document it).
   - `list()` returns all topics sorted by name.
4. **Green — implement `TopicService.create` and `list`.**
5. **Red — controller test.** `@WebMvcTest(TopicController.class)` mocking `TopicService`:
   - `POST /topics {"name":"orders"}` → 201 + body.
   - `POST /topics {"name":""}` → 400 with validation details.
   - `POST /topics {"name":"BAD NAME"}` → 400 (pattern violation).
6. **Green — already wired**; verify.

## Files touched
- `src/main/java/com/example/broker/topics/TopicService.java` (remove `UnsupportedOperationException`).
- `src/test/java/com/example/broker/topics/{TopicRepositoryTest,TopicServiceTest,TopicControllerTest}.java` (new).
- Maybe `shared/` — add `TopicAlreadyExistsException` + handler entry.

## Done when
- `mvn test` green.
- `curl -X POST localhost:8080/topics -d '{"name":"orders"}' -H 'Content-Type: application/json'` → 201.
- Duplicate POST → 409.
