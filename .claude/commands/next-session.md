# Next Session Transition Generator

Generate a comprehensive transition prompt for the next session of development.

## Prerequisites

Before generating transition prompt, read:
- @plan/sessions/session-N-summary.md - Current session summary
- @plan/sessions/session-N+1-phase-M.md - Next session plan
- @.cursor/rules/600-phase-transition.mdc - Session transition rules
- @vibe/vibe_phase_workflow.md - Development workflow patterns

## Transition Prompt Structure

Generate transition prompt with:

### 1. Session Completion Summary
- Summary of completed work in current session
- List of all modified files with paths
- Tests implemented and passing status
- Shared libraries created

### 2. Next Session Context
- Reference to @plan/sessions/session-N+1-phase-M.md
- Session objectives and deliverables
- Prerequisites and dependencies
- Estimated completion time

### 3. Implementation Guidance
- Specific implementation steps from session plan
- Key technical decisions to make
- Database changes required
- Testing strategy

### 4. Transition Prompt Format
```
Session N Complete: Phase M ([METHOD] [ENDPOINT])

Implemented:
- [Specific endpoint] with real database integration
- Database migration: [migration file]
- Domain models: [model files]
- Repository: [repository file]
- Service layer: [service file]
- API endpoint: [endpoint file]

Tests:
- E2E tests passing: [test file]
- All tests passing: YES/NO

Shared Libraries Created:
- [Repository] - available for future sessions
- [Service] - available for future sessions
- [Models] - available for future sessions

Session Summary:
- Generated plan/sessions/session-N-summary.md
- Documented implementation details
- Listed shared libraries created
- Noted dependencies for next session

Next Session:
- Review plan/sessions/session-N+1-phase-M.md for next phase
- When ready, say "Start Session N+1" to begin next implementation

DO NOT proceed to Session N+1 automatically.
```

## File References

Always include proper @ references to:
- @plan/sessions/session-N-summary.md - Current session documentation
- @plan/sessions/session-N+1-phase-M.md - Next session plan
- @templates/phase_plan_template.md - Session planning template
- @.cursor/rules/ - All relevant development rules
