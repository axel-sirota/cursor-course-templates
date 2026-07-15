# ✅ Reference Solution - Setup Complete!

## What's Ready

A complete, working Express + TypeScript blog application using **Prisma** as the ORM (typed queries generated from `schema.prisma`).

### Location
```
examples/blog-api/
```

### Status
✅ package.json with pinned dependency versions
✅ Prisma schema defined (User, Post, Comment + relations)
✅ Docker PostgreSQL configured (port 5433)
✅ Application starts with `npm run dev`
✅ Database tables created via `prisma migrate dev`
✅ All code follows the layered repository/service/controller pattern

## Quick Start

```bash
cd examples/blog-api

# Start Docker services
docker compose up -d

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run migrations
npx prisma migrate dev --name init

# Run the app
npm run dev

# Visit http://localhost:3000/health
```

## Important Notes

### Port Configuration
- **PostgreSQL**: Port **5433** (not 5432)
  - A locally installed PostgreSQL is typically on 5432
  - Docker PostgreSQL is mapped to 5433 to avoid conflict
- **Express**: Port 3000
- **pgAdmin**: Port 5050

### Database Connection
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/blog_db
```

## Architecture

### Prisma (Typed ORM)
```typescript
// Repository layer uses the generated PrismaClient
const row = await this.prisma.post.create({
  data: { title, content, authorId },
});
// row is fully typed by Prisma from schema.prisma — no manual column mapping
return this.toModel(row);
```

### Key Features
- ✅ **Constructor-injected PrismaClient** in every repository (testable, no global singleton reach-through)
- ✅ **Typed query results** generated directly from `schema.prisma`
- ✅ **Zod validation** at the controller boundary, mapped to 400 by the centralized error handler
- ✅ **Migrations** tracked in `prisma/migrations/`
- ✅ **Cascading deletes** declared in the schema (`onDelete: Cascade` on Comment -> Post)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user, returns a JWT
- `POST /api/auth/login` - Login user, returns a JWT

### Posts
- `POST /api/posts` - Create blog post (auth required)
- `GET /api/posts` - List posts (paginated)
- `GET /api/posts/:postId` - Get post by ID
- `PUT /api/posts/:postId` - Update post (author-only)
- `DELETE /api/posts/:postId` - Delete post (author-only)

### Comments
- `POST /api/posts/:postId/comments` - Create comment (auth required)
- `GET /api/posts/:postId/comments` - List comments

### Health
- `GET /health` - Health check (includes a live Prisma `SELECT 1` check)

## Testing

### Run Tests
```bash
cd examples/blog-api
npm test
```

### Test Files
- `tests/routes.test.ts` - Basic E2E tests
- `tests/scenarios.test.ts` - Detailed scenarios with input/output docs ⭐
- `tests/README.md` - Complete test documentation

## Teaching with This Solution

### Show Students
1. **Prisma schema + generated client** in `prisma/schema.prisma` and `src/repositories/*`
2. **Constructor dependency injection** across repository -> service -> controller
3. **Zod validation** at the controller boundary
4. **Layered architecture**: Route -> Controller -> Service -> Repository -> Prisma
5. **Test-driven approach** with clear input/output in `scenarios.test.ts`

### Key Files to Reference
- `src/config/prisma.ts` - Singleton client setup
- `src/repositories/*.repository.ts` - Prisma query examples + typed mappers
- `src/controllers/*.controller.ts` - Request/response conversion
- `tests/scenarios.test.ts` - Test examples with docs

## Stopping Services

```bash
# Stop but keep data
docker compose stop

# Stop and remove all data
docker compose down -v
```

## Troubleshooting

### Can't connect to database
- Check port 5433 (not 5432)
- Ensure Docker is running: `docker compose ps`
- Check logs: `docker compose logs postgres`

### Port already in use
- Change PORT in `.env`
- Or stop the conflicting service: `lsof -ti:3000 | xargs kill -9`

### App won't start
- Check `.env` exists (`cp .env.example .env`)
- Ensure DATABASE_URL uses port 5433
- Verify Docker containers are healthy (`docker compose ps`)
- Run `npx prisma generate` if you see "Prisma Client not generated" errors

## Next Steps

1. ✅ Application is ready to run
2. Test all endpoints via `npm test` or manually with curl/Postman
3. Use as reference during teaching
4. Show students the test scenarios
5. Walk through one complete flow: Route → Controller → Service → Repository → Prisma → Response

## Perfect for Teaching

This solution demonstrates:
- ✅ Professional Express + TypeScript structure
- ✅ Prisma as a typed, migration-driven ORM
- ✅ Zod-validated request/response boundaries
- ✅ Test-driven development with Jest + Supertest
- ✅ Clear layered architecture
- ✅ Complete documentation

**Ready to use as teaching reference!**
