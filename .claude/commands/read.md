# Read Project Context Command

Read all essential project files to understand current status and context.

## Required Files to Read

### Vibe Development Guides
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

### Project Status Files
- @plan/project-overview.md - Project description and scope
- @plan/api-design/overview.md - API design decisions
- @plan/api-design/entities.md - Entity relationships
- @plan/api-design/endpoints.md - Endpoint specifications
- @plan/phases/ - Individual phase plans
- @plan/sessions/ - Session execution plans
- @plan/transition-prompts.md - Phase transition prompts

### Templates
- @templates/openapi-template.yaml - OpenAPI specification template
- @templates/phase_plan_template.md - Session planning template
- @templates/docker-compose-template.yaml - Infrastructure template
- @templates/phase-checklist.md - Phase completion checklist
- @templates/research-export.md - Research export template

### Current Implementation (if exists)
- @app/ - Application code structure
- @tests/ - Test files and structure
- @openapi.yaml - Current API specification
- @docker-compose.yml - Infrastructure configuration

## Reading Priority

1. **First**: @vibe/ files for development patterns
2. **Second**: @.cursor/rules/ for implementation rules
3. **Third**: @plan/ files for current project status
4. **Fourth**: @templates/ for reference materials
5. **Fifth**: @app/ and @tests/ for current implementation

## Context Understanding

After reading all files, provide summary of:
- Current project phase and session
- Available shared libraries and models
- Next session objectives and prerequisites
- Key technical decisions and patterns
- Known limitations and technical debt
