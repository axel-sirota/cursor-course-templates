# Blog API Development Phases

**Human-Readable Project Roadmap**

This document provides a high-level overview of the complete development lifecycle for the Blog API project. Each phase builds incrementally on the previous one, following TDD and layered architecture principles.

---

## Overview

**Project**: RESTful Blog API  
**Stack**: Python 3.11+ | FastAPI | PostgreSQL | SQLAlchemy 2.0 | Alembic  
**Architecture**: Modular Monolith with Repository + Service layers  
**Testing**: Pytest with E2E API tests (TDD approach)  
**Total Phases**: 6 (Phase 0 through Phase 5)  
**Total Sessions**: 6 (one session per phase)

---

## Phase 0: Skeleton (Walking Skeleton)

**Status**: ✅ Complete  
**Session**: 1  
**Duration**: 45-60 minutes

### Purpose
Create a fully functional API skeleton where all endpoints return mock data. This validates the API design, establishes project structure, and enables immediate testing without any backend implementation.

### Deliverables
- ✅ Complete project structure (app/, tests/, plan/)
- ✅ 13 API endpoints with mock implementations
- ✅ Pydantic v2 request/response schemas
- ✅ Docker Compose with PostgreSQL
- ✅ 19 E2E tests (all passing with mock data)
- ✅ OpenAPI documentation at `/docs`
- ✅ Configuration files (requirements.txt, .env.example, pyproject.toml)

### Key Features
- Mock authentication (any Bearer token accepted)
- Consistent mock data patterns
- Full OpenAPI schema validation
- CORS configured
- Health check endpoint

### What's NOT Included
- No database operations
- No real authentication
- No data persistence
- No business logic validation
- No error handling for missing resources

### Success Criteria
- ✅ All 13 endpoints respond correctly
- ✅ OpenAPI docs are complete
- ✅ All tests pass (19/19)
- ✅ Can start server and test manually
- ✅ Docker Compose brings up PostgreSQL

---

## Phase 1: Authentication

**Status**: ⏭️ Next  
**Session**: 2  
**Duration**: 60-90 minutes

### Purpose
Implement real user authentication with database persistence, secure password storage, and JWT token-based authorization. This establishes the foundation for all protected endpoints.

### Deliverables
- [ ] SQLAlchemy User model with async support
- [ ] Alembic migrations (init + create users table)
- [ ] Password hashing with bcrypt
- [ ] JWT token generation and verification
- [ ] UserRepository (data access layer)
- [ ] AuthService (business logic layer)
- [ ] Real auth dependency (replaces mock)
- [ ] E2E tests for complete auth flow

### Key Features
- User registration with duplicate email/username detection
- Secure password hashing (bcrypt)
- JWT tokens with 7-day expiry
- Token payload: { sub: user_id, username, exp }
- Database persistence of users
- Protected endpoint decorator working

### Technical Specs
**Database Schema:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

**JWT Token Format:**
```json
{
  "sub": "user-uuid",
  "username": "johndoe",
  "exp": 1234567890
}
```

### Endpoints Affected
- `POST /api/auth/register` - Now creates real users in DB
- `POST /api/auth/login` - Now verifies credentials and issues real JWT
- `GET /api/auth/me` - Now retrieves real user from DB

### Success Criteria
- [ ] Can register new user
- [ ] Duplicate email/username returns 400
- [ ] Can login with correct credentials
- [ ] Wrong password returns 401
- [ ] JWT token is valid for 7 days
- [ ] Protected endpoints verify token
- [ ] Invalid token returns 401
- [ ] User data persists in database
- [ ] Alembic migrations run successfully
- [ ] All auth tests pass

### Anti-Patterns to Avoid
- ❌ Storing plaintext passwords
- ❌ Using synchronous database operations
- ❌ Hardcoding JWT secret in code
- ❌ Skipping password strength validation
- ❌ Not handling duplicate user errors

---

## Phase 2: Posts CRUD

**Status**: 📋 Planned  
**Session**: 3  
**Duration**: 90-120 minutes

### Purpose
Implement full CRUD operations for blog posts with database persistence, authorization checks (author-only updates/deletes), and pagination.

### Deliverables
- [ ] SQLAlchemy Post model with relationships
- [ ] Alembic migration (create posts table)
- [ ] PostRepository (data access layer)
- [ ] PostService (business logic layer)
- [ ] Authorization checks (author-only operations)
- [ ] Pagination for list endpoint
- [ ] E2E tests for all CRUD operations

### Key Features
- Create posts (authenticated users only)
- List posts with pagination (public)
- Get single post (public)
- Update post (author only)
- Delete post (author only)
- Foreign key relationship: Post → User (author)
- Automatic timestamps (created_at, updated_at)
- Published/draft status

### Technical Specs
**Database Schema:**
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_created ON posts(created_at DESC);
```

**Repository Methods:**
- `create_post(title, content, author_id, published) → Post`
- `get_post_by_id(post_id) → Post | None`
- `list_posts(skip, limit) → List[Post]`
- `update_post(post_id, **updates) → Post`
- `delete_post(post_id) → bool`

**Authorization Logic:**
```python
# Only author can update/delete
if post.author_id != current_user.user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

### Endpoints Affected
- `POST /api/posts` - Creates real post in DB
- `GET /api/posts` - Queries DB with pagination
- `GET /api/posts/{post_id}` - Queries DB, returns 404 if not found
- `PUT /api/posts/{post_id}` - Updates DB, checks authorization
- `DELETE /api/posts/{post_id}` - Deletes from DB, checks authorization

### Success Criteria
- [ ] Can create post as authenticated user
- [ ] Post persists in database
- [ ] Can list posts with pagination (?page=1&pageSize=20)
- [ ] Can get single post by ID
- [ ] Returns 404 for non-existent post
- [ ] Can update own post
- [ ] Cannot update other user's post (403)
- [ ] Can delete own post
- [ ] Cannot delete other user's post (403)
- [ ] Timestamps update correctly
- [ ] All CRUD tests pass

### Anti-Patterns to Avoid
- ❌ Allowing any user to update/delete any post
- ❌ Not handling 404 for missing posts
- ❌ Not paginating large result sets
- ❌ Exposing author's password hash in response
- ❌ Using synchronous SQLAlchemy operations

---

## Phase 3: Comments

**Status**: 📋 Planned  
**Session**: 4  
**Duration**: 60-75 minutes

### Purpose
Implement comment functionality allowing users to comment on blog posts. Includes nested resource handling (comments under posts) and authorization for comment deletion.

### Deliverables
- [ ] SQLAlchemy Comment model with relationships
- [ ] Alembic migration (create comments table)
- [ ] CommentRepository (data access layer)
- [ ] CommentService (business logic layer)
- [ ] Authorization for comment deletion
- [ ] Join queries to include author username
- [ ] E2E tests for comment operations

### Key Features
- Add comment to post (authenticated)
- List comments for post (public)
- Delete own comment (author only)
- Foreign keys: Comment → Post, Comment → User
- Verify post exists before adding comment
- Include author username in response

### Technical Specs
**Database Schema:**
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_comments_post ON comments(post_id);
CREATE INDEX idx_comments_author ON comments(author_id);
```

**Repository Methods:**
- `create_comment(post_id, author_id, content) → Comment`
- `list_comments_by_post(post_id) → List[Comment]`
- `get_comment_by_id(comment_id) → Comment | None`
- `delete_comment(comment_id) → bool`

**Service Logic:**
```python
# Verify post exists before adding comment
post = await post_repo.get_post_by_id(post_id)
if not post:
    raise HTTPException(status_code=404, detail="Post not found")
```

### Endpoints Affected
- `POST /api/posts/{post_id}/comments` - Creates comment in DB
- `GET /api/posts/{post_id}/comments` - Queries DB with joins
- `DELETE /api/comments/{comment_id}` - Deletes from DB, checks authorization

### Success Criteria
- [ ] Can add comment to existing post
- [ ] Returns 404 when commenting on non-existent post
- [ ] Comments include author username
- [ ] Can list all comments for post
- [ ] Can delete own comment
- [ ] Cannot delete other user's comment (403)
- [ ] Comments cascade delete when post deleted
- [ ] All comment tests pass

### Anti-Patterns to Avoid
- ❌ Allowing comments on non-existent posts without validation
- ❌ Not including author information in response
- ❌ Allowing any user to delete any comment
- ❌ N+1 query problem (join users table)
- ❌ Not handling post deletion cascade

---

## Phase 4: Tags

**Status**: 📋 Planned  
**Session**: 5  
**Duration**: 75-90 minutes

### Purpose
Implement tag functionality with many-to-many relationships. Posts can have multiple tags, and tags can be associated with multiple posts. Includes tag normalization and aggregate queries.

### Deliverables
- [ ] SQLAlchemy Tag and PostTag models
- [ ] Alembic migration (create tags and post_tags tables)
- [ ] TagRepository (data access layer)
- [ ] Updated PostService to handle tags
- [ ] Tag normalization (lowercase, trim)
- [ ] Aggregate queries (post count per tag)
- [ ] E2E tests for tag operations

### Key Features
- Create posts with tags
- Update post tags
- List all tags with post counts
- Filter posts by tag
- Tag name normalization
- Get-or-create tag pattern
- Many-to-many relationship handling

### Technical Specs
**Database Schema:**
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE post_tags (
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);
CREATE INDEX idx_post_tags_post ON post_tags(post_id);
CREATE INDEX idx_post_tags_tag ON post_tags(tag_id);
```

**Tag Normalization:**
```python
def normalize_tag(name: str) -> str:
    return name.strip().lower()
```

**Repository Methods:**
- `get_or_create_tag(name) → Tag`
- `list_all_tags() → List[Tag]`
- `get_posts_by_tag(tag_name) → List[Post]`
- `add_tags_to_post(post_id, tag_names) → None`
- `get_tags_for_post(post_id) → List[Tag]`

### Endpoints Affected
- `POST /api/posts` - Now accepts tags array
- `PUT /api/posts/{post_id}` - Now accepts tags array
- `GET /api/posts/{post_id}` - Includes tags in response
- `GET /api/posts` - Includes tags in list response
- `GET /api/tags` - Lists all tags with counts
- `GET /api/tags/{tag_name}/posts` - Filters posts by tag

### Success Criteria
- [ ] Can create post with tags
- [ ] Tags are normalized (lowercase, trimmed)
- [ ] Can update post tags
- [ ] Can list all tags with post counts
- [ ] Can filter posts by tag
- [ ] Duplicate tags are prevented
- [ ] Tags included in post responses
- [ ] Many-to-many relationship working
- [ ] All tag tests pass

### Anti-Patterns to Avoid
- ❌ Case-sensitive tag matching
- ❌ Creating duplicate tags with different cases
- ❌ N+1 queries when loading post tags
- ❌ Not handling empty tag lists
- ❌ Allowing special characters in tag names

---

## Phase 5: Polish & Deploy

**Status**: 📋 Planned  
**Session**: 6  
**Duration**: 120-150 minutes

### Purpose
Add production-ready features including advanced filtering, sorting, search, comprehensive error handling, rate limiting, and production Docker setup. Prepare API for deployment.

### Deliverables
- [ ] Advanced filtering (by author, published status, date range)
- [ ] Sorting (by date, title, multiple fields)
- [ ] Full-text search on posts
- [ ] Comprehensive error handling middleware
- [ ] Request validation (length limits, format validation)
- [ ] Rate limiting middleware
- [ ] Production Dockerfile (multi-stage)
- [ ] docker-compose.prod.yml
- [ ] Database optimization (indexes, query analysis)
- [ ] Structured JSON logging
- [ ] Integration tests (full user journeys)

### Key Features

**Filtering & Search:**
- Filter posts by: author, published status, tag, date range
- Sort posts by: created_at, updated_at, title (asc/desc)
- Full-text search on title and content
- Combined filters (author + tag + published)

**Error Handling:**
- Consistent error response format
- Catch-all exception handler
- SQLAlchemy error handling
- Detailed error logging
- 400, 401, 403, 404, 422, 429, 500 responses

**Validation:**
- Title: 1-200 characters
- Content: 1-10,000 characters
- Email format validation
- Password strength requirements
- Tag name validation (alphanumeric + hyphens)

**Production Setup:**
- Multi-stage Dockerfile (builder + runtime)
- Non-root user in container
- Health check endpoint
- Environment-based configuration
- Resource limits in docker-compose
- Connection pooling optimization
- Database indexes for common queries

**Monitoring & Logging:**
- Structured JSON logs
- Request ID tracking
- Log all errors with stack traces
- Performance metrics (request duration)
- Health check endpoint with DB connectivity

### Technical Specs

**Query Parameters:**
```
GET /api/posts?
  page=1
  &pageSize=20
  &authorId=uuid
  &published=true
  &tag=python
  &sort=createdAt
  &order=desc
  &q=search term
```

**Error Response Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title must be between 1 and 200 characters",
    "details": [...],
    "timestamp": "2026-05-05T14:00:00Z",
    "requestId": "abc-123"
  }
}
```

**Dockerfile Pattern:**
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
RUN useradd -m appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY app/ /app/
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Success Criteria
- [ ] Filtering works for all parameters
- [ ] Sorting works (asc/desc, multiple fields)
- [ ] Search returns relevant results
- [ ] Error handling catches all exceptions
- [ ] Validation prevents invalid data
- [ ] Rate limiting blocks excessive requests
- [ ] Production Docker image builds successfully
- [ ] Multi-stage build reduces image size
- [ ] Structured logs in JSON format
- [ ] Integration tests pass (full workflows)
- [ ] Database queries are optimized
- [ ] Health check includes DB connectivity
- [ ] API ready for deployment

### Anti-Patterns to Avoid
- ❌ Exposing stack traces to clients
- ❌ Missing indexes on filtered columns
- ❌ No request timeout handling
- ❌ Running as root in Docker
- ❌ Hardcoded configuration in code
- ❌ No logging for production debugging
- ❌ Single-stage Docker builds
- ❌ No rate limiting (DDoS vulnerability)

---

## Development Workflow Summary

### Phase Progression
```
Phase 0 (Skeleton) → Session 1
    ↓
Phase 1 (Auth) → Session 2
    ↓
Phase 2 (Posts) → Session 3
    ↓
Phase 3 (Comments) → Session 4
    ↓
Phase 4 (Tags) → Session 5
    ↓
Phase 5 (Polish) → Session 6
    ↓
Production Ready ✅
```

### Testing Strategy
Each phase follows TDD:
1. Write E2E tests for new endpoints
2. Run tests (should fail - red)
3. Implement feature
4. Run tests (should pass - green)
5. Refactor code
6. Run tests again (should still pass)

### Database Migration Strategy
Each phase that adds database tables:
1. Create SQLAlchemy model
2. Generate Alembic migration: `alembic revision -m "description"`
3. Review generated migration
4. Apply migration: `alembic upgrade head`
5. Verify schema in database

### Layered Architecture
```
API Routes (HTTP)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Database (PostgreSQL)
```

### Session Completion Criteria
Each session must:
- ✅ Complete all implementation tasks
- ✅ Pass all E2E tests
- ✅ Update session summary document
- ✅ Verify manually via /docs
- ✅ Commit changes with descriptive message
- ✅ Update PHASES.md with status

---

## Quick Reference

| Phase | Session | Focus | Duration | Database Tables |
|-------|---------|-------|----------|-----------------|
| 0 | 1 | Skeleton | 45-60 min | None (mock only) |
| 1 | 2 | Auth | 60-90 min | users |
| 2 | 3 | Posts CRUD | 90-120 min | posts |
| 3 | 4 | Comments | 60-75 min | comments |
| 4 | 5 | Tags | 75-90 min | tags, post_tags |
| 5 | 6 | Polish | 120-150 min | (optimizations only) |

**Total Estimated Time**: 7-9 hours  
**Total Endpoints**: 13  
**Total Database Tables**: 5  
**Total Tests**: 40+ (estimated)

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-05  
**Status**: Phase 0 Complete, Ready for Phase 1
