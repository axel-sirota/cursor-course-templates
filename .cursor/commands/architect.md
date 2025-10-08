# Architect Phase Command

Create a comprehensive API design and session planning for implementing: $ARGUMENTS

## Prerequisites

Before starting architect phase, read all essential files:

### Core Vibe Files
- @vibe/vibe_phase_workflow.md - Phase-based development patterns
- @vibe/vibe_fastapi_boilerplate.md - Project structure and patterns
- @vibe/vibe_database.md - Database models and repository patterns
- @vibe/vibe_development_lifecycle.md - Git workflow and deployment
- @vibe/vibe_agent_module.md - Agent module patterns

### Development Rules
- @.cursor/rules/100-architect-phase.mdc - API design rules
- @.cursor/rules/200-skeleton-phase.mdc - Skeleton implementation rules
- @.cursor/rules/300-endpoint-phase.mdc - Endpoint implementation rules
- @.cursor/rules/400-testing-first.mdc - Test-driven development rules
- @.cursor/rules/500-implementation.mdc - Implementation patterns
- @.cursor/rules/600-phase-transition.mdc - Session transition rules

### Templates
- @templates/openapi-template.yaml - OpenAPI specification template
- @templates/phase_plan_template.md - Session planning template
- @templates/docker-compose-template.yaml - Infrastructure template

## Deliverables

Create comprehensive planning structure:

### 1. OpenAPI Specification
- @openapi.yaml - Complete API specification
- Use @templates/openapi-template.yaml as foundation
- Define all endpoints, schemas, and examples

### 2. Plan Folder Structure
```
plan/
├── project-overview.md
├── api-design/
│   ├── overview.md
│   ├── entities.md
│   └── endpoints.md
├── phases/
│   ├── phase-0-skeleton.md
│   ├── phase-1-*.md
│   └── phase-N-*.md
├── sessions/
│   ├── session-1-phase-0.md
│   ├── session-2-phase-1.md
│   └── session-N-*.md
└── transition-prompts.md
```

### 3. Session Planning Requirements

Each session should be:
- **Focused**: One endpoint per session
- **Time-bounded**: <1 hour of work per session
- **Test-driven**: Start with E2E tests
- **Self-contained**: Clear objectives and deliverables

### 4. Session Plan Template

Use @templates/phase_plan_template.md structure:
```markdown
# Session N: Phase M ([METHOD] [ENDPOINT])

## Objective
Implement [specific endpoint] with real database integration and passing tests.

## Prerequisites
- Previous session completed
- E2E tests written and failing
- Database migration planned

## Session Deliverables
- [ ] Database migration applied
- [ ] Domain models implemented
- [ ] Repository methods created
- [ ] Service layer implemented
- [ ] API endpoint updated
- [ ] E2E tests passing
- [ ] Phase summary generated

## Session Execution Steps
1. Write E2E tests (TDD)
2. Create database migration
3. Implement domain models
4. Create repository
5. Implement service layer
6. Update API endpoint
7. Verify tests pass
8. Generate phase summary

## Success Criteria
- All E2E tests passing
- Endpoint returns real data
- Code formatted and typed
- Documentation updated

## Transition Prompt
"Session N complete. Ready for Session N+1: [Next phase description]"
```

## Phase Breakdown Strategy

Break down implementation into small, focused sessions:

1. **Session 1: Phase 0 (Skeleton)**
   - All endpoints with mock responses
   - Docker Compose setup
   - Environment configuration

2. **Session 2+: Phase M (Individual Endpoints)**
   - One endpoint per session
   - Prioritize by dependencies
   - Start with simple CRUD operations

## Success Criteria

Before completing architect phase:
- [ ] All endpoints documented in OpenAPI
- [ ] Request/response schemas defined
- [ ] Authentication specified
- [ ] Examples provided for all schemas
- [ ] Error responses defined (400, 401, 404, 500)
- [ ] Complete plan/ folder structure created
- [ ] Session plans for all phases generated
- [ ] Transition prompts defined
- [ ] OpenAPI spec validates

## Anti-Patterns to Avoid

Do NOT:
- Skip OpenAPI design and jump to coding
- Design endpoints without considering data models
- Forget error response schemas
- Use inconsistent naming
- Automatically proceed to Session 1 without user confirmation
- Combine multiple phases in a single session
- Skip session planning documentation
