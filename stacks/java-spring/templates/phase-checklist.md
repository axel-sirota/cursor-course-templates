# Spring Boot Phase Checklist

Use this checklist to verify readiness before moving between phases.

---

## Phase 0 — Skeleton

- [ ] All controllers registered (return `501 Not Implemented`)
- [ ] Service interfaces defined
- [ ] Repository interfaces defined (extend `JpaRepository`)
- [ ] `mvn compile` succeeds
- [ ] `mvn spotless:check` passes

---

## Phase 1+ — Implementation

- [ ] `@WebMvcTest` written and failing before controller logic
- [ ] `@DataJpaTest` written and failing before repository logic
- [ ] `@Valid` on all request DTOs
- [ ] `@ControllerAdvice` handles expected exceptions
- [ ] `@Transactional(readOnly = true)` on all read service methods

---

## Handoff

- [ ] `mvn verify` passes (all tests green)
- [ ] `mvn spotless:check` passes
- [ ] No `@Autowired` field injection remaining
- [ ] `/actuator/health` returns `200 OK`
