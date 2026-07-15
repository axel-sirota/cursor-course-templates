# Phase N Checklist: [HTTP Method] [Endpoint Path]

## Phase Information
- Phase Number: N
- Endpoint: [Method] [Path]
- Goal: [One sentence description]
- Dependencies: [List previous phases]
- Estimated Time: [X] minutes
- Start Time: [YYYY-MM-DD HH:MM]

## Pre-Phase Setup
- [ ] Previous phase summary reviewed
- [ ] Shared libraries identified
- [ ] Dependencies understood
- [ ] Phase requirements clear

## Step 1: Controller Test (5-10 min)
- [ ] Test file created: `src/test/java/.../web/[Feature]ControllerTest.java`
- [ ] Test written using skeleton mock response structure
- [ ] Test includes success case
- [ ] Test includes error cases
- [ ] Test includes authentication check
- [ ] Test run and confirmed FAILING
- [ ] Test failure makes sense (no real implementation yet)

## Step 2: Flyway Migration (5-10 min)
- [ ] Migration file created: `src/main/resources/db/migration/V{n}__create_[table].sql`
- [ ] Schema matches `@Entity` requirements
- [ ] Primary key defined (`UUID`, generated at application layer)
- [ ] Foreign keys added (if applicable)
- [ ] Timestamps added (`created_at`, `updated_at`)
- [ ] Indexes added for common queries
- [ ] `NOT NULL` constraints where appropriate
- [ ] Migration applied locally (`./mvnw spring-boot:run` triggers Flyway)
- [ ] Schema verified (check `flyway_schema_history` table)

## Step 3: Domain Model — `@Entity` (5-10 min)
- [ ] `@Entity` class created with `@Table(name = "...")`
- [ ] `@Id` with `@GeneratedValue(strategy = GenerationType.UUID)`
- [ ] Columns annotated with `@Column(nullable = ..., length = ...)`
- [ ] `@CreationTimestamp` / `@UpdateTimestamp` on audit fields
- [ ] Relationships mapped (`@ManyToOne`, `@OneToMany`) if applicable
- [ ] Lombok `@Getter`/`@Setter`/`@NoArgsConstructor` applied
- [ ] Never exposes itself directly to the web layer

## Step 4: Repository (10-15 min)
- [ ] `[Entity]Repository extends JpaRepository<[Entity], UUID>` created
- [ ] Derived query methods added (`findByX`, `findByXOrderByY`) if needed
- [ ] Custom `@Query` added if a derived method can't express the query
- [ ] `save()` / `findById()` / `findAll()` / `deleteById()` confirmed available for free
- [ ] Pagination support added (`Page<X> findAll(Pageable)`) if the endpoint lists resources

## Step 5: Service Layer (5-10 min)
- [ ] `@Service` class created with `@RequiredArgsConstructor`
- [ ] Repository injected via constructor (never field `@Autowired`)
- [ ] Business logic method implemented
- [ ] `@Transactional` applied at the correct boundary
- [ ] Error handling added (typed exceptions, not bare `Exception`)
- [ ] `@Slf4j` logging added
- [ ] Javadoc on all public methods
- [ ] Input validation implemented (beyond `jakarta.validation` on the DTO)

## Step 6: API Endpoint (5-10 min)
- [ ] Mock implementation removed
- [ ] Service injected via constructor
- [ ] Request DTO validated with `@Valid`
- [ ] Service method called; exceptions bubble to `@RestControllerAdvice`
- [ ] Entity converted to response DTO (`PostResponse.from(entity)` pattern)
- [ ] HTTP status codes correct (`ResponseEntity.ok()`, `.status(HttpStatus.CREATED)`, etc.)
- [ ] Error responses properly formatted (`ProblemDetail`)
- [ ] `@AuthenticationPrincipal` / security dependency added if protected
- [ ] Javadoc added to the controller method

## Step 7: Test Validation (5 min)
- [ ] Controller test run
- [ ] Test now PASSING
- [ ] Test validates actual persistence (via repository or Testcontainers)
- [ ] Test validates proper timestamps
- [ ] Test validates proper UUID generation
- [ ] All test scenarios passing

## Step 8: Code Quality (5 min)
- [ ] Checkstyle passed: `./mvnw checkstyle:check`
- [ ] Code formatted: `./mvnw spotless:apply`
- [ ] Compilation clean: `./mvnw compile`
- [ ] All tests passing: `./mvnw test`
- [ ] No linting errors
- [ ] Code reviewed for best practices

## Step 9: Phase Transition (5-10 min)
- [ ] Phase summary generated: `plan/sessions/session-N-summary.md`
- [ ] Implementation details documented
- [ ] Shared libraries documented
- [ ] Known limitations noted
- [ ] Next phase recommendations provided
- [ ] Files changed list complete
- [ ] Time actual vs estimate noted

## Final Checklist
- [ ] All tests passing
- [ ] All unit tests passing (if applicable)
- [ ] Code formatted and Checkstyle-clean
- [ ] No hardcoded values
- [ ] Secrets properly managed
- [ ] Error handling comprehensive
- [ ] Logging appropriate
- [ ] Documentation complete
- [ ] Ready for next phase

## Time Tracking
- Estimated Time: [X] minutes
- Actual Time: [Y] minutes
- Variance: [+/-Z] minutes
- Notes on variance: [Why it took longer/shorter]

## Notes and Learnings
[Document any issues encountered, solutions found, or learnings for future phases]
