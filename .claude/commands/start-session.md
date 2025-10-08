# Start Session Command

Begin execution of a specific session following the session-based development approach.

## Prerequisites

Before starting a session, read:
- @plan/sessions/session-N-phase-M.md - Session plan and objectives
- @plan/sessions/session-N-1-summary.md - Previous session summary (if not Session 1)
- @.cursor/rules/200-skeleton-phase.mdc - For Session 1
- @.cursor/rules/300-endpoint-phase.mdc - For Session 2+
- @.cursor/rules/400-testing-first.mdc - Testing requirements
- @.cursor/rules/500-implementation.mdc - Implementation patterns

## Session Execution Process

### 1. Session Initialization
- Review session plan objectives
- Confirm prerequisites are met
- Check dependencies from previous sessions
- Verify environment is ready

### 2. Follow Session-Specific Rules

**For Session 1 (Phase 0 - Skeleton):**
- Follow @.cursor/rules/200-skeleton-phase.mdc
- Create project structure
- Implement all mock endpoints
- Set up Docker Compose
- Create test structure

**For Session N (Phase M - Implementation):**
- Follow @.cursor/rules/300-endpoint-phase.mdc
- Write E2E tests first (TDD)
- Implement database migration
- Create domain models and repository
- Implement service layer
- Update API endpoint
- Verify tests pass

### 3. Session Completion
- Complete all session deliverables
- Generate session summary in @plan/sessions/session-N-summary.md
- Provide transition prompt for next session
- Do NOT automatically proceed to next session

## Session Commands

### Start Session 1 (Skeleton)
```bash
# Start Session 1: Phase 0 (Skeleton Implementation)
```

### Start Session N (Implementation)
```bash
# Start Session N: Phase M ([METHOD] [ENDPOINT])
```

## Success Criteria

Session is complete when:
- [ ] All session objectives met
- [ ] All deliverables completed
- [ ] Tests passing
- [ ] Code formatted and typed
- [ ] Session summary generated
- [ ] Transition prompt provided

## Anti-Patterns

Do NOT:
- Skip session plan review
- Implement multiple endpoints in one session
- Skip E2E test writing
- Automatically start next session
- Skip session documentation
