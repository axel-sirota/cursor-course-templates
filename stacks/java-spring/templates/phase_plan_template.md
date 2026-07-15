# Implementation Phase Plan

## Project Overview
- Project Name: [Project Name]
- API Version: 1.0.0
- Total Endpoints: [Number]
- Estimated Total Time: [Hours/Days]

## Phase 0: Skeleton

**Goal:** Create working Spring Boot skeleton with all endpoints returning mock DTOs

**Deliverables:**
- Complete Maven project structure
- All endpoints with mock responses matching OpenAPI
- Docker Compose configuration
- Environment setup (`.env.example`, `application.yml`)
- Development tooling configured (Checkstyle, Spotless, JUnit 5)
- Actuator health check endpoint
- Authentication endpoints (register, login) if applicable

**Success Criteria:**
- All endpoints accessible via `/swagger-ui.html`
- Mock responses match OpenAPI schemas
- Docker services running
- `/actuator/health` passing

**Estimated Time:** 60-90 minutes

**Dependencies:** None

---

## Phase 1: [HTTP Method] [Endpoint Path]

**Goal:** [One sentence description of what this endpoint does]

**Endpoint:** [METHOD] [PATH]

**Priority:** High/Medium/Low

**Deliverables:**
- Flyway migration for [table]
- `@Entity` class: [Entity]
- `[Entity]Repository extends JpaRepository<[Entity], UUID>` (+ custom query methods if needed)
- `[Entity]Service` with business logic and `@Transactional` boundaries
- Real endpoint implementation
- Tests passing (`@WebMvcTest` + Mockito unit tests)
- Phase summary document

**Success Criteria:**
- Controller test passes against real service logic
- Data persists correctly in Postgres
- Proper error handling (400, 401, 404, 500) via `@RestControllerAdvice`
- `./mvnw checkstyle:check` and `./mvnw spotless:apply` clean

**Estimated Time:** 45-60 minutes

**Dependencies:** Phase 0

**Shared Libraries Created:**
- `[Entity]Repository` (available for reading in future phases)
- `[Entity]Service` (can be extended)
- `[Entity]` entity (represents core domain concept)

---

## Phase 2: [HTTP Method] [Endpoint Path]

**Goal:** [One sentence description]

**Endpoint:** [METHOD] [PATH]

**Priority:** High/Medium/Low

**Deliverables:**
- [List if new tables needed, otherwise "Uses existing tables"]
- Additional repository query methods (if needed)
- Service method implementation
- Real endpoint implementation
- Tests passing
- Phase summary document

**Success Criteria:**
- Controller test passes
- Integration with Phase 1 libraries works
- Error handling comprehensive

**Estimated Time:** 30-45 minutes

**Dependencies:** Phase 1 (`[Entity]Repository` available)

**Shared Libraries Created:**
- Extended `[Entity]Repository` with `findById()`/`findByX()`
- [Additional libraries if any]

---

## Phase 3: [HTTP Method] [Endpoint Path]

**Goal:** [One sentence description]

**Endpoint:** [METHOD] [PATH]

**Priority:** High/Medium/Low

**Deliverables:**
- Flyway migration for [new table]
- `[NewEntity]` entity (layered — DTO separate from `@Entity`)
- `[NewEntity]Repository`
- `[NewEntity]Service`
- Real endpoint implementation
- Tests passing
- Phase summary document

**Success Criteria:**
- New entity created successfully
- Foreign key relationships work (`@ManyToOne`/`@OneToMany`)
- Tests pass

**Estimated Time:** 45-60 minutes

**Dependencies:** Phase 1, Phase 2

**Shared Libraries Created:**
- `[NewEntity]Repository`
- `[NewEntity]Service`
- `[NewEntity]` entity

---

## Phase Priority Matrix

### Must Have (Phase 0-3)
Critical functionality required for MVP:
- Phase 0: Skeleton
- Phase 1: [Core creation endpoint]
- Phase 2: [Core read endpoint]
- Phase 3: [Core related entity]

### Should Have (Phase 4-6)
Important but not blocking:
- Phase 4: [Update endpoint]
- Phase 5: [List endpoint with pagination]
- Phase 6: [Delete endpoint]

### Nice to Have (Phase 7+)
Enhancement features:
- Phase 7: [Advanced feature]
- Phase 8: [Analytics/reporting]
- Phase 9: [Additional integrations]

## Implementation Strategy

### Week 1
- Phase 0: Skeleton (Day 1)
- Phase 1-2: Core functionality (Day 2-3)
- Phase 3-4: Extended functionality (Day 4-5)

### Week 2
- Phase 5-6: Complete CRUD (Day 1-2)
- Phase 7+: Enhancements (Day 3-5)

## Risk Assessment

### High Risk Phases
- [Phase N]: [Reason - complexity, external dependencies, etc.]

### Dependencies Between Phases
```
Phase 1 (Create) → Phase 2 (Read) → Phase 3 (Related Entity)
                ↓
              Phase 4 (Update)
                ↓
              Phase 5 (Delete)
```

### Blocking Issues
- Flyway schema changes require careful migration ordering (never edit an already-applied migration file)
- Authentication must work in Phase 0 before implementing protected endpoints
- `@ManyToOne`/foreign key relationships need parent tables to exist first

## Testing Strategy

### Per Phase
- `@WebMvcTest` written before implementation
- Test must fail initially
- Implementation makes test pass
- Mockito unit tests added for complex business logic
- Testcontainers integration test for the full stack (at least once per sub-system)

### Integration Testing
After Phase 3: Test cross-entity operations
After Phase 6: Complete CRUD testing
After Phase 9: Full system integration tests

## Quality Gates

### Before Completing Each Phase
- [ ] All tests passing (`./mvnw test`)
- [ ] Checkstyle passing (`./mvnw checkstyle:check`)
- [ ] Code formatted (`./mvnw spotless:apply`)
- [ ] Compilation clean (`./mvnw compile`)
- [ ] No linting errors
- [ ] Phase summary generated
- [ ] Changes committed

### Before Moving to Production
- [ ] All phases complete
- [ ] Full test suite passing
- [ ] Security review complete
- [ ] Performance testing done
- [ ] Documentation updated

## Rollback Plan

### If Phase Fails
1. Revert to previous phase summary state
2. Review what went wrong
3. Adjust approach or split into smaller phases
4. Restart phase with new strategy

### Database Rollback
Each migration should be reversible:
- Never edit an already-applied Flyway migration — write a new `V{n+1}__` migration to undo/fix it
- Test rollback procedures on a scratch database
- Document migration dependencies

## Notes

### Design Decisions
- [Key architectural decisions made during design]
- [Trade-offs considered]
- [Alternative approaches rejected and why]

### Assumptions
- [Assumptions about user behavior]
- [Assumptions about data volume]
- [Assumptions about performance requirements]

### Future Considerations
- [Features planned for later versions]
- [Scalability considerations]
- [Integration possibilities]
