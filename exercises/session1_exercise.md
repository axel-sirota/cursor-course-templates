# Session 1 Exercise: Build a Blog API with Phase-Based Development

## Learning Objectives

By the end of this session, you will:
- Understand phase-based development workflow
- Use Cursor rules to guide AI-assisted development
- Build a production-ready FastAPI application from scratch
- Implement test-driven development with E2E tests
- Work with PostgreSQL database using Docker
- Properly manage secrets and environment variables

## Exercise Overview

You will build a blog API with the following features:
- User authentication (register, login)
- Blog post management (create, read)
- Comment system (create, list)
- Simple HTML dashboard

## Setup (10 minutes)

### Prerequisites
- Cursor IDE installed
- Docker Desktop installed and running
- Python 3.11+ installed
- Git installed

### Initial Setup

1. Create project directory:
```bash
mkdir blog-api
cd blog-api
```

2. Copy materials folder into project:
```bash
# Provided materials include:
# - .cursor/rules/
# - vibe/ guides
# - templates/
```

3. Initialize git repository:
```bash
git init
git add .
git commit -m "Initial setup with Cursor rules"
```

4. Open in Cursor:
```bash
cursor .
```

## Part 1: Demonstration (40 minutes)

Watch and follow along as the instructor demonstrates:

### Phase 0: Design and Skeleton (15 minutes)

**Architect Phase:**
- Design OpenAPI specification for blog API
- Plan implementation phases
- Document endpoint requirements

**Skeleton Implementation:**
- Create project structure following FastAPI boilerplate
- Set up Docker Compose with PostgreSQL
- Implement all endpoints with mock responses
- Create basic HTML templates
- Verify skeleton is working

**Deliverables:**
- OpenAPI specification
- Phase plan document
- Working skeleton with all endpoints
- Docker services running

### Phase 1: POST /posts Implementation (25 minutes)

**Step-by-step demonstration:**

1. E2E Test First (5 minutes)
   - Write test using skeleton mock data
   - Run test and verify it fails
   - Document expected behavior

2. Database Migration (5 minutes)
   - Create posts table migration
   - Define schema with proper types
   - Apply migration locally

3. Models and Repository (10 minutes)
   - Create layered domain models
   - Implement repository with type-safe mappers
   - Create service layer

4. Processor Replacement (5 minutes)
   - Replace mock endpoint with real implementation
   - Convert between API and domain models
   - Add error handling

5. Test Validation
   - Run E2E test and verify it passes
   - Demonstrate test validates real database

6. Phase Transition
   - Generate phase summary
   - Document shared libraries
   - Identify next phase

## Break (10 minutes)

## Part 2: Your Implementation (40 minutes)

Now you will implement the comments feature following the same pattern.

### Your Task: POST /posts/{postId}/comments

Implement comment creation following the exact phase-based workflow demonstrated.

### Step-by-Step Instructions

#### Step 1: E2E Test (10 minutes)

Using Chat mode in Cursor:
```
"Start Phase 2: POST /posts/{postId}/comments
Write E2E test using skeleton mock data"
```

Expected output:
- Test file: tests/api/test_comments.py
- Test initially fails
- Test uses mock comment structure

Verify:
```bash
pytest tests/api/test_comments.py::test_create_comment -v
# Should FAIL
```

#### Step 2: Database Migration (5 minutes)

Using Composer mode:
```
"Create comments table migration
Follow vibe_database.md patterns"
```

Expected output:
- Migration file in database/develop/supabase/migrations/
- Table with: id, post_id, content, author_id, created_at, updated_at
- Foreign key to posts table

Apply migration:
```bash
cd database/develop
supabase db reset
```

#### Step 3: Models (5 minutes)

Using Composer mode:
```
"Create layered models for Comment
Base → Full → Create
Follow vibe_database.md patterns"
```

Expected output:
- app/modules/comments/models/domain_models.py
- CommentBase, Comment, CommentCreate models
- Proper type hints and docstrings

#### Step 4: Repository (10 minutes)

Using Composer mode:
```
"Create CommentRepository with type-safe mappers
Implement create() and get_by_post_id() methods"
```

Expected output:
- app/modules/comments/repository/repository.py
- Type-safe mappers for conversions
- CRUD methods with error handling

#### Step 5: Service Layer (5 minutes)

Using Composer mode:
```
"Create CommentService with business logic
Handle comment creation validation"
```

Expected output:
- app/modules/comments/services/comment_service.py
- create_comment() method
- Validation and error handling

#### Step 6: API Endpoint (10 minutes)

Using Edit mode on the mock endpoint:
```
"Replace mock implementation with real CommentService
Convert API models to domain models"
```

Expected output:
- Updated endpoint in app/api/comments.py
- Service integration
- Proper error handling

#### Step 7: Verify (5 minutes)

Run tests:
```bash
pytest tests/api/test_comments.py::test_create_comment -v
# Should PASS now
```

Run all tests:
```bash
pytest tests/api/ -v
```

Format and check code:
```bash
black app/ tests/
pytest tests/
```

#### Step 8: Phase Transition

Using Chat mode:
```
"Phase 2 complete
Generate phase summary"
```

Expected output:
- phases/phase-2-summary.md
- Documentation of what was built
- Shared libraries for future phases

## Success Criteria

By end of practice session, you should have:

### Working Implementation
- [ ] Comment creation endpoint functional
- [ ] E2E test passing
- [ ] Database migration applied
- [ ] Models following layered architecture
- [ ] Repository with type-safe mappers
- [ ] Service layer with business logic

### Code Quality
- [ ] Code formatted with Black
- [ ] Type hints on all functions
- [ ] Docstrings on public APIs
- [ ] No linting errors
- [ ] All tests passing

### Documentation
- [ ] Phase summary generated
- [ ] Shared libraries documented
- [ ] Known limitations noted

## Homework Assignment

Extend your blog API with a dashboard feature.

### Requirements

Create a simple HTML dashboard that displays:
- Total number of posts
- Number of comments per post (list)

### Implementation Steps

1. Create new endpoint:
```
GET /api/stats
```

2. Response format:
```json
{
  "totalPosts": 10,
  "postsWithComments": [
    {
      "postId": "post-123",
      "title": "My Post",
      "commentCount": 5
    }
  ]
}
```

3. Create HTML template:
```html
<!-- templates/dashboard.html -->
Display stats in a simple, readable format
```

4. Implement following phase-based workflow:
   - Write E2E test first
   - Implement stats aggregation in service
   - Create API endpoint
   - Create HTML template
   - Verify tests pass

### Submission

Commit your work:
```bash
git add .
git commit -m "Add dashboard feature"
git push
```

Submit:
- Link to your repository
- Screenshot of dashboard page
- Screenshot of passing tests

## Tips for Success

### Using Cursor Rules
- Rules automatically apply based on file patterns
- Reference vibe/ guides when planning
- Use Chat mode for questions
- Use Composer mode for creating new features
- Use Edit mode for modifying existing code

### Testing Strategy
- Always write E2E test first
- Test should fail before implementation
- Test should pass after implementation
- Run tests frequently during development

### Common Issues

**Database connection fails:**
```bash
docker-compose down -v
docker-compose up -d
```

**Tests not finding modules:**
```bash
# Ensure __init__.py files exist in all packages
```

**Type errors:**
```bash
# Add proper type hints
# Reference vibe_fastapi_boilerplate.md
```

**Migration issues:**
```bash
cd database/develop
supabase db reset
```

## Resources

### Reference Materials
- vibe/vibe_phase_workflow.md - Phase-based development guide
- vibe/vibe_fastapi_boilerplate.md - Project structure guide
- vibe/vibe_database.md - Database patterns guide
- .cursor/rules/ - AI assistant rules

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- PostgreSQL: https://www.postgresql.org/docs/
- Pytest: https://docs.pytest.org/

### Getting Help
- Check phase summaries for examples
- Review previous phase implementations
- Ask instructor during session
- Reference vibe guides for patterns

## Next Steps

After completing this exercise:
- Review your phase summaries
- Identify patterns that worked well
- Note areas for improvement
- Prepare questions for Session 2

Session 2 will cover:
- Advanced agent module patterns
- MCP server integration
- Team development workflows
- CI/CD pipeline setup
