# Session-Based Development Runbook

## Project Setup

### 1. Create Project and Virtual Environment
```bash
mkdir project-name
cd project-name

# Create virtual environment in project root
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Copy Materials
```
Copy to project root:
- .cursor/rules/
- .claude/commands/
- vibe/
- templates/
```

### 3. Initialize Git
```bash
git init
git add .
git commit -m "Initial setup with session-based rules"
```

### 4. Open Cursor
```bash
cursor .
```

### 5. Verify Commands Available
In Cursor, you should see these commands available:
- `@architect` - API design and session planning
- `@start-session` - Begin session execution
- `@next-session` - Generate session transitions
- `@read` - Read project context
- `@research-export` - Export research when stuck

## Architect Phase

### Design OpenAPI Specification

**Use Command:**
```
@architect [feature name] with these endpoints:
- [List endpoints]
```

**What the Command Does:**
- Reads all essential vibe files and rules
- Creates comprehensive plan/ folder structure
- Generates openapi.yaml with all endpoints
- Creates session plans for each phase
- Generates transition prompts

**Expected Output:**
- openapi.yaml created/updated
- plan/ folder with complete session planning
- Individual session plans for each phase
- Transition prompts between sessions
- Stops and waits for next command

### Validate OpenAPI
```bash
# Use online validator: https://editor.swagger.io/
# Or install validator and run locally
```

### Review Before Proceeding
- Review openapi.yaml
- Review plan/ folder structure
- Check session plans in plan/sessions/
- Make adjustments if needed
- When satisfied, proceed to Session 1

## Session 1: Phase 0 (Skeleton)

### Start Session 1

**Use Command:**
```
@start-session 1
```

**What the Command Does:**
- Reads plan/sessions/session-1-phase-0.md
- Follows session plan objectives
- Creates complete project structure
- Implements all mock endpoints
- Sets up Docker Compose
- Creates environment configuration

**Expected Output:**
- Complete project structure
- All endpoints returning mock data
- Docker Compose configured
- Environment configuration ready
- Session 1 summary generated
- Stops with transition prompt for Session 2

### Setup Environment
```bash
cp .env.example .env
# Edit .env with your values
```

### Start Services
```bash
docker-compose up -d
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Verify Skeleton
```bash
python main.py
# Visit http://localhost:8000/docs
# Test all endpoints return mock data
# Verify health check works
```

### Session 1 Complete

**Review Session Summary:**
```bash
cat plan/sessions/session-1-summary.md
# Review what was implemented
# Check shared libraries created
# Verify transition prompt for Session 2
```

**Expected Output:**
- plan/sessions/session-1-summary.md created
- Transition prompt: "Session 1 complete. Ready for Session 2"
- Stops and waits for Session 2 command

## Session 2+: Endpoint Implementation

### Starting a Session

**Use Command:**
```
@start-session N
```

**What the Command Does:**
- Reads plan/sessions/session-N-phase-M.md
- Follows session plan objectives
- Implements one endpoint per session
- Uses TDD approach (test first)
- Generates session summary
- Provides transition prompt for next session

**Before starting, review:**
```bash
cat plan/sessions/session-[N-1]-summary.md
# Review shared libraries available
# Review dependencies
# Confirm next session from plan/sessions/
```

### Session Execution Process

**The @start-session command handles all steps automatically:**

1. **E2E Test First (TDD)**
   - Reads session plan objectives
   - Writes E2E test using mock structure
   - Test initially FAILS (proves it tests something)

2. **Database Migration**
   - Creates migration based on session requirements
   - Uses proper UUID and timestamp patterns
   - Applies migration to local database

3. **Domain Models**
   - Creates layered models (Base, Full, Create, Update)
   - Follows vibe_database.md patterns
   - Includes proper type hints and validation

4. **Repository Layer**
   - Implements type-safe mappers
   - Creates CRUD methods for current endpoint
   - Includes error handling and logging

5. **Service Layer**
   - Implements business logic
   - Includes validation and error handling
   - Provides clean interface for API layer

6. **API Endpoint**
   - Replaces mock implementation
   - Converts between API and domain models
   - Handles authentication and error responses

7. **Test Verification**
   - Runs E2E tests (should now PASS)
   - Verifies real data in database
   - Checks code quality (formatting, types)

8. **Session Summary**
   - Documents what was implemented
   - Lists shared libraries created
   - Provides transition prompt for next session

**Manual Verification (if needed):**
```bash
# Run specific test
pytest tests/api/test_[module].py::test_[endpoint] -v

# Check database
psql $DATABASE_URL -c "SELECT * FROM [table];"

# Verify endpoint works
curl -X POST http://localhost:8000/api/[endpoint]
```

### Session Completion

**Review Session Summary:**
```bash
cat plan/sessions/session-N-summary.md
# Review what was implemented
# Check shared libraries created
# Verify transition prompt for next session
```

**Expected Output:**
- plan/sessions/session-N-summary.md created
- Transition prompt: "Session N complete. Ready for Session N+1"
- Stops and waits for next session command

**Commit Changes:**
```bash
git add .
git commit -m "Session N: Phase M ([METHOD] [PATH]) - [Description]"
```

## Session Transition

### Generate Next Session Prompt

**Use Command:**
```
@next-session
```

**What the Command Does:**
- Reads current session summary
- Generates transition prompt for next session
- References next session plan
- Provides clear handoff documentation

**Expected Output:**
- Clear transition prompt with session completion summary
- Next session objectives and prerequisites
- Shared libraries available
- Transition prompt for next session

## When Stuck: Research Export

**Use Command:**
```
@research-export [describe specific problem]
```

**What the Command Does:**
- Documents the problem clearly
- Lists all attempted solutions
- Includes relevant code snippets and error messages
- Generates structured research export
- Creates research-export.md for external research

**Expected Output:**
- research-export.md created with comprehensive problem documentation
- Structured format for external research
- Stops for external research

**Next Steps:**
1. Review research-export.md
2. Use with Claude Desktop or other research tools
3. Document solution when found
4. Update session summary with findings

## Session-Based Workflow Summary

### Quick Start
1. **@architect** - Design API and create session plans
2. **@start-session 1** - Create skeleton with all mock endpoints
3. **@start-session N** - Implement one endpoint per session
4. **@next-session** - Generate transition prompts
5. **@research-export** - When stuck, export for external research

### Session Commands
```bash
# Design and plan
@architect [feature] with endpoints: [list]

# Start specific session
@start-session N

# Generate transition
@next-session

# Read project context (quick)
@read

# Read full context (comprehensive)
@context

# Export research when stuck
@research-export [problem description]
```

## Common Commands

### Database
```bash
# Reset database
cd database/develop
supabase db reset

# Create migration
supabase migration new [description]

# View database
psql $DATABASE_URL
```

### Docker
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# Logs
docker-compose logs -f [service]

# Clean restart
docker-compose down -v
docker-compose up -d
```

### Testing
```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/api/test_[module].py::test_[name] -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Watch mode (if pytest-watch installed)
ptw tests/
```

### Code Quality
```bash
# Format
black app/ tests/

# Type check
mypy app/modules/[module]/

# Full quality check
black app/ tests/ && mypy app/modules/ && pytest tests/
```

### Application
```bash
# Run development server
python main.py

# Run with reload
uvicorn app.main:app --reload --port 8000

# Run in Docker
docker-compose --profile app up
```

## Session Commands Reference

### Available Commands
```
@architect - API design and session planning
@start-session - Begin session execution  
@next-session - Generate session transitions
@read - Read essential project context (quick)
@context - Read full project context (comprehensive)
@research-export - Export research when stuck
@claude-desktop - Generate research prompts
@terraform - Infrastructure management
```

### Session-Based Context
```
Session 1: @plan/sessions/session-1-phase-0.md
Session N: @plan/sessions/session-N-phase-M.md
Transitions: @plan/transition-prompts.md
Summaries: @plan/sessions/session-N-summary.md
```

### Progressive Context Chain
```
Architect → @plan/ folder structure
Session 1 → @openapi.yaml + @templates/
Session N → @app/modules/[module]/ + @plan/sessions/
Transitions → @plan/sessions/session-N-summary.md
```

## Cursor Mode Selection

### Chat Mode
- Use session commands (@architect, @start-session, etc.)
- Ask questions about implementation
- Generate summaries and transitions
- Export research

### Composer Mode
- Commands automatically use Composer when needed
- Multi-file operations handled by commands
- Scaffolding done by session commands

### Edit Mode
- Commands automatically use Edit mode for replacements
- Session commands handle mock → real implementation
- Focus on single endpoint changes

## Quick Session Checklist

### Before Starting Session
- [ ] Previous session summary reviewed
- [ ] Session plan available in plan/sessions/
- [ ] Shared libraries identified
- [ ] Dependencies understood

### During Session (Automated by Commands)
- [ ] E2E test written and FAILING
- [ ] Migration created and applied
- [ ] Models created (layered)
- [ ] Repository implemented
- [ ] Service implemented
- [ ] Mock replaced
- [ ] Tests PASSING

### Before Completing Session
- [ ] All tests passing
- [ ] Code formatted
- [ ] Type checking passing
- [ ] Session summary generated
- [ ] Changes committed

## File Structure Reference

```
project/
├── .cursor/rules/
├── .claude/commands/
├── vibe/
├── templates/
├── plan/
│   ├── project-overview.md
│   ├── api-design/
│   ├── phases/
│   └── sessions/
│       ├── session-1-phase-0.md
│       ├── session-2-phase-1.md
│       └── session-N-summary.md
├── app/
│   ├── core/
│   ├── api/
│   ├── modules/
│   │   └── [module]/
│   │       ├── models/
│   │       ├── repository/
│   │       └── services/
│   └── main.py
├── tests/
│   ├── api/
│   └── modules/
├── database/develop/supabase/migrations/
├── openapi.yaml
├── docker-compose.yml
├── .env
└── requirements.txt
```

## Environment Variables Template

```bash
# Server
PORT=8000
HOST=0.0.0.0
DEBUG=True

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname


# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Supabase (if using)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_ANON_KEY=
```

## Git Workflow

```bash
# Start feature
git checkout -b feature/[name]

# After each session
git add .
git commit -m "Session [N]: Phase [M] ([METHOD] [PATH]) - [Description]"

# Complete feature
git checkout main
git merge feature/[name]
git branch -d feature/[name]
```

## Troubleshooting Quick Fixes

### Docker won't start
```bash
docker-compose down -v
docker-compose up -d
```

### Tests fail unexpectedly
```bash
cd database/develop
supabase db reset
cd ../..
pytest tests/
```

### Import errors
```bash
# Add __init__.py to all packages
find app -type d -exec touch {}/__init__.py \;
```

### Cursor rules not applying
```bash
# Restart Cursor
# Verify .cursor/rules/ exists
# Check file glob patterns match
```

## Production Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Secrets not in code
- [ ] Database migrations ready
- [ ] Docker images built
- [ ] Health check working
- [ ] Logging configured
- [ ] Error handling comprehensive
