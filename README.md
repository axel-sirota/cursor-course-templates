# Blog API Starter - Phase-Based Development with Cursor

## Overview

This repository provides a complete set of materials for building production-ready FastAPI applications using phase-based development and AI-assisted coding with Cursor IDE.

## What's Included

### .cursor/rules/
Cursor IDE rules that guide AI-assisted development:
- 000-core-workflow.mdc - Core development principles
- 100-architect-phase.mdc - API design with OpenAPI
- 200-skeleton-phase.mdc - Skeleton implementation
- 300-endpoint-phase.mdc - Endpoint implementation
- 400-testing-first.mdc - Test-driven development
- 500-implementation.mdc - Processor replacement
- 600-phase-transition.mdc - Phase documentation

### vibe/
Reference guides for patterns and best practices:
- vibe_phase_workflow.md - Phase-based development guide
- vibe_fastapi_boilerplate.md - FastAPI project structure
- vibe_database.md - Database patterns with Supabase
- vibe_development_lifecycle.md - Git workflow and deployment
- vibe_agent_module.md - Advanced agent patterns (Session 2)

### templates/
Starting templates for common tasks:
- openapi-template.yaml - OpenAPI 3.0 specification template
- phase-checklist.md - Per-phase task checklist
- research-export-template.md - Problem documentation template
- docker-compose.template.yml - Docker services configuration

### exercises/
Session exercises and instructions:
- session1.md - Complete exercise for Session 1

## Quick Start

### Prerequisites

Ensure you have installed:
- Cursor IDE (latest version)
- Docker Desktop
- Python 3.11 or higher
- Git

### Setup

1. Clone or download this repository
2. Open the project in Cursor: `cursor .`
3. Follow exercises/session1.md instructions

### Understanding the Workflow

This project follows a phase-based development approach:

**Phase 0: Skeleton**
- Design OpenAPI specification
- Create all endpoints with mock responses
- Set up infrastructure (Docker, database)

**Phase 1+: Implementation**
- One endpoint per phase
- E2E test first (must fail)
- Implement real functionality
- Tests pass
- Generate phase summary

## Using Cursor Rules

### How Rules Work

Cursor rules in `.cursor/rules/` automatically guide AI responses based on:
- File patterns (globs)
- Always-apply rules
- Context from vibe guides

### When to Use Each Rule

**000-core-workflow.mdc:**
- Always applies
- Provides fundamental workflow principles

**100-architect-phase.mdc:**
- When creating/editing OpenAPI specs
- When planning new features

**200-skeleton-phase.mdc:**
- When creating Phase 0 skeleton
- When setting up new projects

**300-endpoint-phase.mdc:**
- When implementing Phase 1+ endpoints
- When following TDD cycle

**400-testing-first.mdc:**
- When writing tests
- When in tests/ directory

**500-implementation.mdc:**
- When replacing mock implementations
- When writing business logic

**600-phase-transition.mdc:**
- When completing a phase
- When generating summaries

### Cursor Modes

**Chat Mode:**
- Ask questions
- Plan implementations
- Get explanations
- Generate documentation

**Composer Mode (Agent):**
- Create new features
- Generate boilerplate
- Multi-file operations
- Automated scaffolding

**Edit Mode:**
- Modify existing code
- Refactor implementations
- Fix specific issues
- Targeted changes

## Phase-Based Development Process

### Starting a New Feature

1. Open OpenAPI specification
2. Use Chat mode: "Design API for [feature]"
3. Review and validate OpenAPI spec
4. Generate phase plan

### Creating Skeleton (Phase 0)

1. Use Composer mode: "Create Phase 0 skeleton from OpenAPI"
2. Verify all endpoints return mock data
3. Set up Docker services
4. Test skeleton: `python main.py` and visit `/docs`

### Implementing Endpoints (Phase 1+)

For each endpoint:

1. E2E Test First (Chat mode)
   ```
   "Write E2E test for [endpoint] using skeleton mock data"
   ```

2. Run test - verify it fails
   ```bash
   pytest tests/api/test_[feature].py -v
   ```

3. Database Migration (Composer mode)
   ```
   "Create [table] migration following vibe_database.md"
   ```

4. Models (Composer mode)
   ```
   "Create layered models for [entity]"
   ```

5. Repository (Composer mode)
   ```
   "Create [Entity]Repository with type-safe mappers"
   ```

6. Service (Composer mode)
   ```
   "Create [Entity]Service with business logic"
   ```

7. Replace Mock (Edit mode on endpoint)
   ```
   "Replace mock with real [Entity]Service"
   ```

8. Verify tests pass
   ```bash
   pytest tests/api/test_[feature].py -v
   ```

9. Phase Transition (Chat mode)
   ```
   "Phase [N] complete - generate summary"
   ```

### When You Get Stuck

1. Use Chat mode: "Export research on [problem]"
2. Review generated research-export.md
3. Get external help (Claude Desktop, documentation)
4. Document solution in phase summary

## Directory Structure

After Phase 0, your project will look like:

```
blog-api/
├── .cursor/
│   └── rules/              # Cursor AI rules
├── vibe/                   # Reference guides
├── templates/              # Starting templates
├── phases/                 # Phase summaries (generated)
├── app/
│   ├── core/              # Database, config, middleware
│   ├── api/               # API endpoints
│   │   ├── health.py
│   │   ├── auth.py
│   │   └── posts.py
│   ├── modules/           # Business modules
│   │   └── posts/
│   │       ├── models/
│   │       ├── repository/
│   │       └── services/
│   └── main.py
├── tests/
│   ├── api/               # E2E tests
│   └── modules/           # Unit tests
├── database/
│   └── develop/
│       └── supabase/
│           └── migrations/
├── templates/             # HTML templates
├── docker-compose.yml
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- PORT - API server port (default: 8000)
- DATABASE_URL - PostgreSQL connection string
- JWT_SECRET_KEY - Secret for JWT tokens
- ALLOWED_ORIGINS - CORS allowed origins

## Running the Application

### Start Docker Services

```bash
docker-compose up -d
```

Services:
- PostgreSQL: localhost:5432
- pgAdmin: localhost:5050 (if using tools profile)

### Start API Server

```bash
python main.py
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/api/test_posts.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black app/ tests/

# Type check
mypy app/modules/

# Run all quality checks
black app/ tests/ && mypy app/modules/ && pytest tests/
```

## Common Commands

### Database

```bash
# Reset database (apply all migrations)
cd database/develop
supabase db reset

# Create new migration
supabase migration new [description]
```

### Docker

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

### Testing

```bash
# Run specific test
pytest tests/api/test_posts.py::test_create_post -v

# Run with output
pytest tests/ -v -s

# Run integration tests only
pytest tests/ -v -m integration
```

## Best Practices

### Test-Driven Development
1. Write E2E test first
2. Test must fail initially
3. Implement minimum to pass test
4. Refactor while keeping tests green

### Code Quality
- Use type hints on all functions
- Write docstrings for public APIs
- Format with Black
- Maximum line length: 88 characters
- Follow Python Google Style Guide

### Phase Management
- One endpoint per phase
- Generate summary after each phase
- Document shared libraries
- Note known limitations

### Git Workflow
- Commit after each phase
- Use descriptive commit messages
- Reference vibe_development_lifecycle.md

## Troubleshooting

### Docker Issues

**Services won't start:**
```bash
docker-compose down -v
docker-compose up -d
```

**Database connection refused:**
- Check Docker Desktop is running
- Verify DATABASE_URL in .env
- Check port 5432 is not in use

### Test Issues

**Import errors:**
- Ensure `__init__.py` exists in all packages
- Check Python path: `export PYTHONPATH=.`

**Tests fail unexpectedly:**
- Check database is running
- Verify migrations applied
- Clear test database if needed

### Cursor Issues

**Rules not applying:**
- Check file matches glob patterns
- Restart Cursor if needed
- Verify `.cursor/rules/` directory exists

**AI responses incorrect:**
- Reference vibe guides explicitly
- Provide more context
- Use specific rule names

## Learning Resources

### Official Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- PostgreSQL: https://www.postgresql.org/docs/
- Pytest: https://docs.pytest.org/
- Cursor: https://cursor.sh/docs

### Internal Guides
- Read all vibe/ guides before starting
- Review .cursor/rules/ to understand AI behavior
- Check templates/ for starting points
- Follow exercises/session1.md step-by-step

## Getting Help

### During Development
1. Check phase summaries for examples
2. Review vibe guides for patterns
3. Use Chat mode to ask questions
4. Export research for complex problems

### Common Questions

**How do I start a new phase?**
Use Chat mode: "Start Phase [N]: [Endpoint]"

**How do I know what to implement next?**
Check phases/phase-[N-1]-summary.md recommendations

**How do I handle errors?**
Follow patterns in 500-implementation.mdc

**How do I test my code?**
Reference 400-testing-first.mdc patterns

## Next Steps

1. Complete exercises/session1.md
2. Review your phase summaries
3. Identify patterns that worked well
4. Prepare for Session 2:
   - Advanced agent patterns
   - MCP server integration
   - Team workflows
   - CI/CD pipelines

## Contributing

To improve these materials:
1. Document issues you encounter
2. Suggest improvements to rules
3. Share successful patterns
4. Update vibe guides based on experience

## License

These materials are provided for educational purposes. Adapt and use as needed for your projects.

## Support

For questions or issues:
- Review documentation in vibe/
- Check exercises/session1.md
- Consult with instructor
- Reference official documentation
