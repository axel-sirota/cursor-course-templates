# Session 1: Phase 0 - Skeleton

## Goal
Build a walking skeleton with mock implementations for all API endpoints. No database, no real authentication — just validate API contracts and structure.

## Prerequisites
- API design reviewed (plan/api-design.md)
- Python 3.11+ installed
- Docker installed

## Implementation Tasks

### 1. Project Structure
Create the FastAPI modular monolith structure:
```
app/
├── core/
│   ├── config.py          # Environment configuration
│   ├── database.py        # Database connection (stub for now)
│   ├── logging.py         # Logging setup
│   ├── middleware.py      # CORS, error handling
│   └── dependencies.py    # FastAPI dependencies (auth, etc.)
├── api/
│   ├── health.py          # Health check endpoint
│   ├── auth.py            # Auth endpoints (mock)
│   ├── posts.py           # Posts endpoints (mock)
│   ├── comments.py        # Comments endpoints (mock)
│   └── tags.py            # Tags endpoints (mock)
├── schemas/
│   ├── auth.py            # Auth request/response models
│   ├── posts.py           # Post request/response models
│   ├── comments.py        # Comment request/response models
│   └── tags.py            # Tag request/response models
└── main.py                # FastAPI application entrypoint
```

### 2. Configuration Files
- `requirements.txt` — Python dependencies
- `.env.example` — Environment variables template
- `docker-compose.yml` — PostgreSQL + app services
- `pyproject.toml` — Pytest configuration

### 3. Mock Endpoints
Implement all 13 endpoints with hardcoded mock data:

**Auth endpoints:**
- POST /api/auth/register → Return mock user with token
- POST /api/auth/login → Return mock token
- GET /api/auth/me → Return mock current user

**Posts endpoints:**
- POST /api/posts → Echo back request with mock ID
- GET /api/posts → Return list of 3 mock posts
- GET /api/posts/{post_id} → Return single mock post
- PUT /api/posts/{post_id} → Echo back update with mock response
- DELETE /api/posts/{post_id} → Return 204 No Content

**Comments endpoints:**
- POST /api/posts/{post_id}/comments → Echo comment with mock ID
- GET /api/posts/{post_id}/comments → Return list of 2 mock comments
- DELETE /api/comments/{comment_id} → Return 204 No Content

**Tags endpoints:**
- GET /api/tags → Return list of mock tags
- GET /api/tags/{tag_name}/posts → Return mock posts for tag

**Health:**
- GET /health → Return { "status": "ok" }

### 4. Pydantic Models
Create all request/response schemas using Pydantic v2:
- Use `model_config = ConfigDict(populate_by_name=True)`
- Use `Field(alias="camelCase")` for JSON field names
- Use snake_case for Python field names

### 5. Mock Authentication
Create a mock auth dependency:
```python
async def require_auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"user_id": "mock-user-123", "username": "mockuser"}
```

### 6. Docker Setup
- PostgreSQL 15 service (for future phases)
- App service (optional, for container testing)
- Volumes for database persistence
- Health checks configured

## Verification Steps

### Manual Testing
1. Start services: `docker-compose up -d`
2. Start app: `python app/main.py` or `uvicorn app.main:app --reload`
3. Visit OpenAPI docs: http://localhost:8000/docs
4. Test health: `curl http://localhost:8000/health`
5. Test auth: `curl -X POST http://localhost:8000/api/auth/login -d '{"email":"test@example.com","password":"pass"}'`
6. Test posts: `curl http://localhost:8000/api/posts`

### Automated Testing
Create basic E2E tests:
- `tests/conftest.py` — Test fixtures
- `tests/api/test_health.py` — Health check test
- `tests/api/test_auth.py` — Auth endpoints test (mock)

Run: `pytest tests/ -v`

## Completion Checklist
- [ ] All 13 endpoints implemented with mock data
- [ ] All Pydantic schemas created with proper aliasing
- [ ] Docker Compose working with PostgreSQL
- [ ] .env.example created with all variables
- [ ] requirements.txt with FastAPI, SQLAlchemy, Alembic, Pytest
- [ ] OpenAPI docs accessible at /docs
- [ ] All mock endpoints return consistent data
- [ ] Health check passing
- [ ] Basic E2E tests passing

## Mock Data Patterns
Use consistent IDs:
- User: `mock-user-123`
- Post: `mock-post-456`
- Comment: `mock-comment-789`
- Tag: `mock-tag-001`

## Next Session
Session 2 will implement Phase 1 (Authentication) with real database and JWT tokens.

## Session Duration
Estimated: 45-60 minutes
