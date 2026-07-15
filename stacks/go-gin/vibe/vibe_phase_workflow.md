# Phase-Based Development Workflow (Go + Gin)

## Purpose

This guide documents the phase-based development workflow for building production-ready Go
applications with Gin using test-driven development. This workflow prioritizes incremental
implementation, comprehensive testing, and knowledge documentation.

## Core Philosophy

### Build in Phases, Not All at Once

Complex features are broken down into phases where each phase implements one endpoint or one distinct
piece of functionality. This approach provides:

- Clear progress markers
- Easier debugging (small changes)
- Better testing (focused tests)
- Knowledge capture at each step
- Ability to pause and resume work

### Test-Driven, Not Test-After

E2E tests (via `net/http/httptest`) are written before implementation using the skeleton's mock data as
expected output. This ensures:

- Tests validate actual behavior
- Implementation is driven by requirements
- No untested code reaches completion
- Refactoring is safe and fast

### Document as You Go

Each phase transition generates a summary documenting what was built, what's available for reuse, and
what comes next. This prevents:

- Knowledge loss between sessions
- Duplicate work
- Dependency confusion
- Process inefficiency

## The Phase Cycle

### Phase 0: Skeleton

Create a complete API skeleton with all endpoints returning mock data.

**Purpose:**
- Establish project structure
- Define API contracts via OpenAPI (Gin has no auto-generated `/docs` — the spec is authoritative)
- Enable E2E test writing
- Validate API design before implementation

**Activities:**
1. Design the OpenAPI specification
2. Plan implementation phases
3. Create project structure (following `vibe_gin_boilerplate.md`)
4. Implement all handlers with mock responses
5. Set up Docker Compose for local development
6. Configure environment variables
7. Set up development tools (`golangci-lint`, `gofmt`, `go vet`)
8. Verify all endpoints return expected mock data

**Deliverables:**
- Working API with mock data
- OpenAPI specification
- Phase plan document
- Docker Compose setup
- Environment configuration
- Test scaffolding

**Success Criteria:**
- All endpoints reachable and returning mock data (verified via `curl`)
- Mock responses match OpenAPI schemas
- Health check passing
- Docker services running
- `go build ./...` and `go vet ./...` succeed
- Ready for Phase 1 implementation

### Phase 1+ Implementation Phases

Each subsequent phase implements one endpoint with full functionality.

**Selection Criteria:**
1. Dependencies (create before read)
2. Complexity (simple before complex)
3. User value (high-impact first)

**Phase Activities:**

#### Step 1: E2E Test First (5-10 minutes)
Write a test using the skeleton mock data as the expected structure:
```go
func TestCreatePost(t *testing.T) {
    // Test MUST fail initially
    router := setupRouter(t)
    req := httptest.NewRequest(http.MethodPost, "/api/posts", body)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)
    assert.Equal(t, http.StatusCreated, w.Code)
}
```

Run the test and verify it fails (proves the test is valid).

#### Step 2: Database Setup (5-10 minutes)
Set up the database schema for required tables:
- Define the schema matching the GORM model's struct tags
- Include proper indexes and constraints
- Apply the schema locally (`golang-migrate up` or `AutoMigrate`)
- Verify the schema in the database

Reference `vibe_database.md` for database patterns.

#### Step 3: GORM Model + DTOs (5-10 minutes)
Create the layered types following the repository pattern:
- GORM model (DB layer, `gorm:"..."` tags)
- Request DTO (API layer, `json:"..."` + `binding:"..."` tags)
- Response DTO (API layer, `json:"..."` tags)
- `ToXResponse()` converter function

Reference `vibe_database.md` for the full type-layering rationale.

#### Step 4: Repository Implementation (10-15 minutes)
Implement CRUD operations:
- Create the repository struct with a `*gorm.DB` field
- Implement only the required methods
- Wrap errors with `fmt.Errorf("...: %w", err)`
- Propagate `context.Context` via `db.WithContext(ctx)`

#### Step 5: Service Layer (5-10 minutes)
Add business logic and orchestration:
- Declare the repository interface at point of use (in the service package)
- Create the service struct
- Implement business rules
- Add error handling and structured logging

#### Step 6: Handler Replacement (5-10 minutes)
Replace the mock handler with a real implementation:
- Convert the handler to a dependency-injecting factory function
- Convert the API request DTO to the service's input shape
- Execute business logic through the service
- Convert the service result to an API response DTO
- Add proper HTTP error mapping (`errors.Is`/`errors.As`)

#### Step 7: Test Validation (5 minutes)
Run E2E tests and verify they pass:
```bash
go test ./internal/handler/... -run TestCreatePost -v
```

Tests should now pass with the real implementation.

#### Step 8: Code Quality (5 minutes)
Format and validate code:
```bash
gofmt -l .
go vet ./...
golangci-lint run
go test ./... -race -cover
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

The AI will:
- Read previous phase summaries
- Identify available shared libraries
- Begin with E2E test writing

### Completing a Phase
```
"Phase N complete" or "Transition to next phase"
```

The AI will:
- Verify all tests passing
- Run code quality checks
- Generate a phase summary
- Provide recommendations for the next phase

### Exporting for Research
```
"Export research on [problem]" or "Generate research export"
```

The AI will:
- Document the problem clearly
- List attempted solutions
- Include Go code snippets and `go vet`/compiler output
- Generate `research-export.md`

## Phase Organization

### Directory Structure
```
project/
├── plan/
│   ├── phases/
│   │   ├── phase-0-skeleton.md
│   │   ├── phase-1-*.md
│   │   └── ...
│   └── sessions/
│       ├── session-1-summary.md
│       ├── session-2-summary.md
│       └── ...
├── openapi.yaml
└── cmd/ internal/ pkg/   # implementation
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
1. Write an E2E test using the skeleton mock data (`httptest`)
2. Test fails (no implementation yet)
3. Implement the endpoint
4. Test passes (implementation complete)

### Test Organization
Colocated `_test.go` files (idiomatic Go):
```
internal/
├── handler/
│   ├── posts.go
│   └── posts_test.go       # E2E tests for all handlers
└── service/
    ├── post_service.go
    └── post_service_test.go  # Unit tests for business logic
```

### Test Coverage Requirements
- E2E tests: all success and error paths
- Unit tests: complex business logic (service layer, mocked repository)
- Coverage: minimum 80% for services (`go test ./... -cover`)
- All tests must pass before phase completion

## Knowledge Management

### Phase Summaries
Each phase generates a summary containing:
- Implementation details
- Shared libraries available
- Known limitations
- Recommendations for the next phase

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
4. Get help from external resources (Claude Desktop, Go documentation, `pkg.go.dev`)
5. Apply the solution and document it in the phase summary

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
1. Design the OpenAPI spec (Architect Phase)
2. Create the Phase 0 skeleton
3. Plan phases (Phase Plan document)
4. Implement Phase 1
5. Implement Phase 2
6. Continue until the feature is complete

### Adding to an Existing Feature
1. Review relevant phase summaries
2. Identify shared libraries
3. Start a new phase
4. Follow the standard phase cycle

### Refactoring
1. Ensure tests are passing before refactoring
2. Refactor the code
3. Verify tests still pass (`go test ./...`)
4. Update the phase summary if needed

## Success Metrics

### Phase Completion
- All E2E tests passing
- Code formatted (`gofmt`) and linted (`golangci-lint`)
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
- Move to the next phase with failing tests
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
- Follow style guidelines (`gofmt`, `golangci-lint`)
- Use doc comments on exported identifiers
- Document as you go
- Refactor incrementally

### Communication
- Use phase summaries for status updates
- Share learnings in summaries
- Document gotchas for the team (GORM quirks, Gin binding edge cases)
- Ask for help when stuck

## Next Steps

After understanding this workflow:
1. Review `vibe_gin_boilerplate.md` for project structure
2. Review `vibe_database.md` for data layer patterns
3. Read `rules/*.mdc` for AI assistant guidance
4. Start with OpenAPI design
5. Create the Phase 0 skeleton
6. Begin Phase 1 implementation
