# Session 07 — Dead-Letter Admin Endpoints

**Phase:** 4 — Retry + DLQ
**Estimated effort:** ~30 min
**Depends on:** session-06.

## Goal
Operator-facing endpoints to inspect and replay dead-letter entries.

## Tasks
1. **Red — service test** `DeadLetterServiceTest` (`@DataJpaTest` + `@Import`):
   - `list()` returns rows in `moved_at DESC` order.
   - `replay(id)` inserts a fresh PENDING `DeliveryAttempt` with `attempt_no=1`, `next_attempt_at=now()`, and does NOT delete the dead-letter row (audit trail).
   - `replay(unknownId)` → `EntityNotFoundException` → 404.
2. **Green — implement `DeadLetterService.list` and `replay`.**
3. **Red — controller test** `@WebMvcTest(DeadLetterController.class)`:
   - `GET /admin/dead-letter` → 200 + list.
   - `POST /admin/dead-letter/{id}/replay` → 202.
   - 404 path.
4. **Integration test:** trigger DLQ promotion (reuse session-06 setup) → call replay endpoint with MockWebServer now returning 200 → assert delivery succeeds.

## Files touched
- `src/main/java/com/example/broker/deadletter/DeadLetterService.java`.
- `src/test/java/com/example/broker/deadletter/*` (new).

## Done when
- `mvn verify` green.
- `curl /admin/dead-letter` returns DLQ entries.
- `curl -X POST /admin/dead-letter/{id}/replay` → 202 and the message is re-delivered.
- Final acceptance: full lifecycle (publish → fail 5x → DLQ → replay → success) demoable via curl.
