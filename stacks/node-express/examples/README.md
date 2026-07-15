# Reference Solution: Blog API

**TEACHER ONLY** - Complete working example for reference

## What This Is
A complete Express + TypeScript + Prisma blog application implementing the session-based workflow. Use this to:
- Understand the complete structure
- Reference during demos
- Debug student issues
- Prepare for sessions

## Features Implemented
- User registration and login (JWT-based, Prisma-backed)
- Create, read, update, delete blog posts (author-only mutations)
- List posts with pagination
- Add comments to posts
- List comments for a post

## Quick Start
```bash
cd examples/blog-api
cp .env.example .env
docker compose up -d
npm install
npx prisma migrate dev --name init
npm run dev
```

Visit: http://localhost:3000/health

## Structure
Follows the exact `vibe_express_boilerplate.md` structure:
- `src/config/` - Env validation, logger, Prisma client
- `src/middleware/` - Auth, error handling, request logging
- `src/routes/` - Express routers
- `src/controllers/` - Request parsing -> service call -> response
- `src/services/` - Business logic (posts, comments, auth)
- `src/repositories/` - Prisma-backed data access
- `tests/` - E2E and scenario tests (Jest + Supertest)

## Phases Implemented
- Phase 0: Skeleton with mocks
- Phase 1: POST /api/posts (with database)
- Phase 2: GET /api/posts/:postId
- Phase 3: POST /api/posts/:postId/comments
- Phase 4: GET /api/posts/:postId/comments
- Phase 5: PUT /api/posts/:postId (author-only update)
- Phase 6: GET /api/posts (paginated list)
- Phase 7: DELETE /api/posts/:postId (author-only delete)

## Testing
```bash
npm test
```

All tests pass with real PostgreSQL database integration (truncated between tests).
