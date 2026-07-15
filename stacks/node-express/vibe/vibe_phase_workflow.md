# Phase-Based Development Workflow

## Purpose

This guide documents the phase-based development workflow for building production-ready Node.js applications with Express using test-driven development. This workflow prioritizes incremental implementation, comprehensive testing, and knowledge documentation.

## Core Philosophy

### Build in Phases, Not All at Once

Complex features are broken down into phases where each phase implements one endpoint or one distinct piece of functionality. This approach provides:

- Clear progress markers
- Easier debugging (small changes)
- Better testing (focused tests)
- Knowledge capture at each step
- Ability to pause and resume work

### Test-Driven, Not Test-After

Supertest E2E tests are written before implementation using the skeleton's mock data as expected output. This ensures:

- Tests validate actual behavior
- Implementation is driven by requirements
- No untested code reaches completion
- Refactoring is safe and fast

### Document as You Go

Each phase transition generates a summary documenting what was built, what's available for reuse, and what comes next. This prevents:

- Knowledge loss between sessions
- Duplicate work
- Dependency confusion
- Process inefficiency

## The Phase Cycle

### Phase 0: Skeleton

Create complete API skeleton with all endpoints returning mock data.

**Purpose:**
- Establish project structure
- Define API contracts via OpenAPI
- Enable E2E test writing
- Validate API design before implementation

**Activities:**
1. Design OpenAPI specification
2. Plan implementation phases
3. Create project structure (following `vibe_express_boilerplate.md`)
4. Implement all endpoints with mock responses
5. Set up Docker Compose for local development
6. Configure environment variables
7. Set up development tools (eslint, prettier, tsc, jest)
8. Verify all endpoints return expected mock data

**Deliverables:**
- Working API with mock data
- OpenAPI specification
- Phase plan document
- Docker Compose setup
- Environment configuration
- Test structure

**Success Criteria:**
- All endpoints reachable and returning mock data
- Mock responses match OpenAPI schemas
- Health check passing
- Docker services running
- Ready for Phase 1 implementation

### Phase 1+ Implementation Phases

Each subsequent phase implements one endpoint with full functionality.

**Selection Criteria:**
1. Dependencies (create before read)
2. Complexity (simple before complex)
3. User value (high-impact first)

**Phase Activities:**

#### Step 1: E2E Test First (5-10 minutes)
Write a Supertest test using skeleton mock data as expected structure:
```typescript
it('creates a post', async () => {
  // Test MUST fail initially
  const response = await request(app).post('/api/posts').send({ /* ... */ });
  expect(response.status).toBe(201);
  expect(response.body).toHaveProperty('postId');
});
```

Run test and verify it fails (proves test is valid).

#### Step 2: Database Setup (5-10 minutes)
Add or update the Prisma model for required tables:
- Define schema matching domain schemas
- Include proper indexes and constraints
- Apply migration locally (`npx prisma migrate dev`)
- Verify schema (`npx prisma studio`)

Reference `vibe_express_boilerplate.md` for schema patterns.

#### Step 3: Domain Schemas (5-10 minutes)
Create layered Zod schemas following the repository pattern:
- Base schema (business fields only)
- Full schema (includes ID and timestamps)
- Create schema (for creation operations)
- Update schema (`.partial()` for update operations)

#### Step 4: Repository Implementation (10-15 minutes)
Implement CRUD operations with typed mappers:
- Create repository class
- Implement required methods only
- Add a `toModel()` transformation function
- Handle errors appropriately

#### Step 5: Service Layer (5-10 minutes)
Add business logic and orchestration:
- Create service class
- Implement business rules
- Add error handling (throw typed `AppError` subclasses)
- Add logging

#### Step 6: Processor Replacement (5-10 minutes)
Replace mock controller body with real implementation:
- Import service layer
- Parse request body with Zod
- Execute business logic through the service
- Let thrown errors reach the centralized error-handling middleware
- Return the typed JSON response

#### Step 7: Test Validation (5 minutes)
Run E2E tests and verify they pass:
```bash
npx jest tests/routes/posts.test.ts -t "creates a post"
```

Tests should now pass with real implementation.

#### Step 8: Code Quality (5 minutes)
Format and validate code:
```bash
npx eslint src/ tests/ --fix
npx prettier --write src/ tests/
npx tsc --noEmit
npx jest
```

All quality checks must pass.

#### Step 9: Phase Transition (5-10 minutes)
Generate phase summary documenting:
- What was implemented
- Shared libraries created
- Known limitations
- Next phase recommendations

Reference `rules/600-phase-transition.mdc` for summary format.

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
- Begin with E2E test writing

### Completing a Phase
```
"Phase N complete" or "Transition to next phase"
```

AI will:
- Verify all tests passing
- Run code quality checks
- Generate phase summary
- Provide recommendations for next phase

### Exporting for Research
```
"Export research on [problem]" or "Generate research export"
```

AI will:
- Document problem clearly
- List attempted solutions
- Include code snippets
- Generate research-export.md

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
    └── [implementation]
```

### Phase Naming Convention
- Phase 0: Skeleton
- Phase 1+: "[HTTP Method] [Endpoint Path]"
  - Example: "POST /posts"
  - Example: "GET /posts/{id}"
  - Example: "POST /posts/{id}/comments"

## Testing Strategy

### E2E Tests Drive Implementation

Every endpoint follows this pattern:
1. Write E2E test using skeleton mock data
2. Test fails (no implementation yet)
3. Implement endpoint
4. Test passes (implementation complete)

### Test Organization
```
tests/
├── routes/              # E2E tests for all endpoints
│   ├── posts.test.ts
│   └── comments.test.ts
└── services/            # Unit tests for business logic
    └── post.service.test.ts
```

### Test Coverage Requirements
- E2E tests: All success and error paths
- Unit tests: Complex business logic
- Coverage: Minimum 80% for services (see `jest.config.ts` coverageThreshold)
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
3. Export to research-export.md
4. Get help from external resources (Claude Desktop, documentation)
5. Apply solution and document in phase summary

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

### Adding to Existing Feature
1. Review relevant phase summaries
2. Identify shared libraries
3. Start new phase
4. Follow standard phase cycle

### Refactoring
1. Ensure tests passing before refactoring
2. Refactor code
3. Verify tests still passing
4. Update phase summary if needed

## Success Metrics

### Phase Completion
- All E2E tests passing
- Code formatted (prettier) and type-checked (tsc --noEmit), lint-clean (eslint)
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
- Skip E2E test writing
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
- Follow style guidelines (eslint, prettier)
- Use strict TypeScript (tsc --noEmit)
- Document as you go
- Refactor incrementally

### Communication
- Use phase summaries for status updates
- Share learnings in summaries
- Document gotchas for team
- Ask for help when stuck

## Next Steps

After understanding this workflow:
1. Review `vibe_express_boilerplate.md` for project structure
2. Read `.cursor/rules/` for AI assistant guidance
3. Start with OpenAPI design
4. Create Phase 0 skeleton
5. Begin Phase 1 implementation
