# Phase-Based Development Workflow

## Purpose

This guide documents the phase-based development workflow for building production-ready
Spring Boot applications using test-driven development. This workflow prioritizes incremental
implementation, comprehensive testing, and knowledge documentation.

## Core Philosophy

### Build in Phases, Not All at Once

Complex features are broken down into phases where each phase implements one endpoint or one
distinct piece of functionality. This approach provides:

- Clear progress markers
- Easier debugging (small changes)
- Better testing (focused tests)
- Knowledge capture at each step
- Ability to pause and resume work

### Test-Driven, Not Test-After

`@WebMvcTest`/`@SpringBootTest` tests are written before implementation using the skeleton's
mock DTO as the expected output. This ensures:

- Tests validate actual behavior
- Implementation is driven by requirements
- No untested code reaches completion
- Refactoring is safe and fast

### Document as You Go

Each phase transition generates a summary documenting what was built, what's available for
reuse, and what comes next. This prevents:

- Knowledge loss between sessions
- Duplicate work
- Dependency confusion
- Process inefficiency

## The Phase Cycle

### Phase 0: Skeleton

Create a complete Spring Boot skeleton with all endpoints returning mock DTOs.

**Purpose:**
- Establish project structure
- Define API contracts via OpenAPI
- Enable `@WebMvcTest` writing
- Validate API design before implementation

**Activities:**
1. Design OpenAPI specification
2. Plan implementation phases
3. Create project structure (following `vibe_java_spring_boilerplate.md`)
4. Implement all endpoints as mock `@RestController` methods
5. Set up Docker Compose for local development
6. Configure `application.yml` and `.env.example`
7. Set up development tools (Checkstyle, Spotless, JUnit 5)
8. Verify all endpoints return expected mock DTOs

**Deliverables:**
- Working Spring Boot app with mock data
- OpenAPI specification
- Phase plan document
- Docker Compose setup
- `application.yml` configuration
- Test structure

**Success Criteria:**
- All endpoints accessible via `/swagger-ui.html`
- Mock responses match OpenAPI schemas
- `/actuator/health` passing
- Docker services running
- Ready for Phase 1 implementation

### Phase 1+ Implementation Phases

Each subsequent phase implements one endpoint with full functionality.

**Selection Criteria:**
1. Dependencies (create before read)
2. Complexity (simple before complex)
3. User value (high-impact first)

**Phase Activities:**

#### Step 1: Test First (5-10 minutes)
Write a `@WebMvcTest` using the skeleton mock DTO as the expected structure:
```java
@Test
void createPost_returnsCreatedPost() throws Exception {
    // Test MUST fail initially
    mockMvc.perform(post("/api/posts")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""{"title":"Test","content":"Body"}"""))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.postId").exists());
}
```

Run the test and verify it fails (proves the test is valid).

#### Step 2: Flyway Migration (5-10 minutes)
Create the migration for required tables:
- Define schema matching `@Entity` requirements
- Include proper indexes and constraints
- Applied automatically on next `./mvnw spring-boot:run`
- Verify schema in `flyway_schema_history`

Reference `vibe_database.md` for migration patterns.

#### Step 3: Domain Model (5-10 minutes)
Create the `@Entity` class following JPA conventions:
- `@Id` with `GenerationType.UUID`
- `@Column` annotations with `nullable`/`length`
- `@CreationTimestamp`/`@UpdateTimestamp` for audit fields
- Never exposed directly to the web layer

Reference `vibe_database.md` for entity mapping patterns.

#### Step 4: Repository Implementation (10-15 minutes)
Implement only the query methods needed for this endpoint:
- Extend `JpaRepository<Entity, UUID>`
- Add derived query methods where the method name alone expresses the query
- Add `@Query` only where a derived name can't express it
- `save()`/`findById()`/`findAll()`/`deleteById()` come for free

#### Step 5: Service Layer (5-10 minutes)
Add business logic and orchestration:
- Create `@Service` class with `@RequiredArgsConstructor`
- Implement business rules
- Add `@Transactional` boundaries
- Add `@Slf4j` logging

#### Step 6: Controller Replacement (5-10 minutes)
Replace the mock endpoint with the real implementation:
- Inject the service via constructor
- Validate the request DTO with `@Valid`
- Call the service method
- Map the returned entity to a response DTO (`Response.from(entity)`)
- Let `@RestControllerAdvice` handle error mapping

#### Step 7: Test Validation (5 minutes)
Run the test and verify it passes:
```bash
./mvnw test -Dtest=PostControllerTest#createPost_returnsCreatedPost
```

The test should now pass with the real implementation.

#### Step 8: Code Quality (5 minutes)
Format and validate code:
```bash
./mvnw checkstyle:check
./mvnw spotless:apply
./mvnw compile
./mvnw test
```

All quality checks must pass.

#### Step 9: Phase Transition (5-10 minutes)
Generate a phase summary documenting:
- What was implemented
- Shared libraries created
- Known limitations
- Next phase recommendations

Reference `rules/600-phase-transition.mdc` for the summary format.

**Time Estimate:**
Each implementation phase takes approximately 40-60 minutes.

## Workflow Commands

### Starting a Phase
```
"Start Phase N: [HTTP Method] [Endpoint Path]"
```

AI will:
- Read previous phase summaries
- Identify available shared libraries
- Begin with test writing

### Completing a Phase
```
"Phase N complete" or "Transition to next phase"
```

AI will:
- Verify all tests passing
- Run code quality checks (Checkstyle, Spotless)
- Generate phase summary
- Provide recommendations for next phase

### Exporting for Research
```
"Export research on [problem]" or "Generate research export"
```

AI will:
- Document problem clearly
- List attempted solutions
- Include code snippets and the full Java stack trace
- Generate `research-export.md`

## Phase Organization

### Directory Structure
```
project/
├── phases/
│   ├── phase-0-summary.md
│   ├── phase-1-summary.md
│   ├── phase-2-summary.md
│   └── ...
├── docs/
│   └── api-design/
│       ├── overview.md
│       ├── entities.md
│       └── phase-plan.md
└── src/
    └── main/java/... [implementation]
```

### Phase Naming Convention
- Phase 0: Skeleton
- Phase 1+: "[HTTP Method] [Endpoint Path]"
  - Example: "POST /posts"
  - Example: "GET /posts/{id}"
  - Example: "POST /posts/{id}/comments"

## Testing Strategy

### Tests Drive Implementation

Every endpoint follows this pattern:
1. Write a `@WebMvcTest` using the skeleton mock DTO
2. Test fails (no implementation yet)
3. Implement the endpoint
4. Test passes (implementation complete)

### Test Organization
```
src/test/java/com/example/<app>/
├── web/              # @WebMvcTest controller tests
│   ├── PostControllerTest.java
│   └── CommentControllerTest.java
├── service/          # Mockito unit tests for business logic
│   └── PostServiceTest.java
└── integration/      # @SpringBootTest + Testcontainers
    └── PostIntegrationTest.java
```

### Test Coverage Requirements
- Controller tests: all success and error paths
- Unit tests: complex business logic
- Coverage: minimum 80% for services (via `./mvnw test jacoco:report`)
- All tests must pass before phase completion

## Knowledge Management

### Phase Summaries
Each phase generates a summary containing:
- Implementation details
- Shared libraries available
- Known limitations
- Recommendations for next phase

These summaries enable:
- Resuming work after breaks
- Onboarding new developers
- Understanding system evolution
- Planning future work

### Research Exports
When encountering unknown problems:
1. Document the issue
2. List attempted solutions
3. Export to `research-export.md`
4. Get help from external resources (Claude Desktop, documentation)
5. Apply solution and document in the phase summary

## Integration with Git

### Committing Work
Commit after each phase completion:
```bash
git add .
git commit -m "Phase N: [Endpoint] - [Brief description]"
```

### Branching Strategy
Reference `vibe_development_lifecycle.md` for:
- Feature branch creation
- Phase-based commits
- Pull request process
- Production deployment

## Common Patterns

### Creating a New Feature
1. Design OpenAPI spec (Architect Phase)
2. Create Phase 0 skeleton
3. Plan phases (Phase Plan document)
4. Implement Phase 1
5. Implement Phase 2
6. Continue until feature complete

### Adding to an Existing Feature
1. Review relevant phase summaries
2. Identify shared libraries
3. Start a new phase
4. Follow the standard phase cycle

### Refactoring
1. Ensure tests are passing before refactoring
2. Refactor code
3. Verify tests still passing
4. Update phase summary if needed

## Success Metrics

### Phase Completion
- All tests passing
- Code formatted (Spotless) and Checkstyle-clean
- Phase summary generated
- No known bugs

### Feature Completion
- All planned phases complete
- All endpoints implemented
- Full test coverage
- Documentation complete

## Anti-Patterns to Avoid

Do NOT:
- Implement multiple endpoints in one phase
- Skip writing the test first
- Move to next phase with failing tests
- Skip phase summary generation
- Implement without tests first
- Ignore code quality checks
- Forget to document shared libraries
- Rush through phases to "finish faster"

## Tips for Success

### Time Management
- Each phase is 40-60 minutes
- Take breaks between phases
- Don't rush implementation
- Let tests guide the code

### Quality Focus
- Write good tests first
- Follow style guidelines (Checkstyle, Spotless)
- Use constructor injection everywhere
- Document as you go
- Refactor incrementally

### Communication
- Use phase summaries for status updates
- Share learnings in summaries
- Document gotchas for the team
- Ask for help when stuck

## Next Steps

After understanding this workflow:
1. Review `vibe_java_spring_boilerplate.md` for project structure
2. Review `vibe_database.md` for data layer patterns
3. Read `rules/*.mdc` for AI assistant guidance
4. Start with OpenAPI design
5. Create Phase 0 skeleton
6. Begin Phase 1 implementation
