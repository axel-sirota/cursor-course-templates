# Reference Solution: Blog API

**TEACHER ONLY** - Complete working example for reference

## What This Is
A complete FastAPI blog application implementing the session-based workflow. Use this to:
- Understand the complete structure
- Reference during demos
- Debug student issues
- Prepare for sessions

## Features Implemented
- User registration and login (in-memory)
- Create blog posts
- Get post by ID
- Add comments to posts
- List comments for a post

## Quick Start
```bash
cd solutions/blog-api
cp .env.example .env
docker-compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Visit: http://localhost:8000/docs

## Structure
Follows exact vibe_fastapi_boilerplate.md structure:
- `app/core/` - Database, config, dependencies
- `app/api/` - API endpoints
- `app/modules/` - Business logic (posts, comments, users)
- `tests/` - E2E and unit tests

## Phases Implemented
- Phase 0: Skeleton with mocks
- Phase 1: POST /api/posts (with database)
- Phase 2: GET /api/posts/{id}
- Phase 3: POST /api/posts/{id}/comments
- Phase 4: GET /api/posts/{id}/comments

## Testing
```bash
pytest tests/ -v
```

All tests pass with real database integration.

