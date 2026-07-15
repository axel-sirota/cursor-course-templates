# Blog API Reference Solution

**TEACHER ONLY** - Complete working Express + TypeScript application using Prisma

## Architecture

### Key Technologies
- **Express**: Web framework
- **PostgreSQL**: Production database (Docker)
- **Prisma**: Typed database client and migrations
- **Zod**: Request/response validation
- **Jest + Supertest**: E2E testing

### Why Prisma Instead of Raw SQL

The Python/FastAPI reference solution in this repo deliberately uses raw SQL (`psycopg2`) to teach students what an ORM abstracts away. In the Node ecosystem, **Prisma is the idiomatic choice** — it's the dominant TypeScript ORM, generates fully-typed query results from `schema.prisma`, and its migration workflow (`prisma migrate dev`) is the standard teaching path for this stack. Using raw `pg` queries here would fight the ecosystem rather than teach it. Where the FastAPI solution shows "how to write parameterized SQL safely," this solution shows "how to model relations and let a typed client generate safe queries for you" — both are valid teaching goals, just for different stacks.

### Structure
```
blog-api/
├── src/
│   ├── app.ts                  # Express app assembly (no listen())
│   ├── server.ts                # Entry point (listen())
│   ├── config/
│   │   ├── env.ts               # Zod-validated environment config
│   │   ├── logger.ts            # pino structured logger
│   │   └── prisma.ts            # Singleton PrismaClient
│   ├── middleware/
│   │   ├── requestLogger.ts     # Correlation-ID request logging
│   │   ├── errorHandler.ts      # Centralized error -> HTTP status mapping
│   │   ├── auth.ts              # JWT verification middleware
│   │   └── asyncHandler.ts      # Forwards async route rejections to next()
│   ├── schemas/                 # Zod request/response/domain schemas
│   ├── routes/                  # Express routers
│   ├── controllers/              # Parse request -> call service -> send response
│   ├── services/                 # Business logic
│   ├── repositories/             # Prisma-backed data access
│   └── errors/                   # Typed AppError subclasses
├── prisma/
│   └── schema.prisma             # User, Post, Comment models + relations
├── tests/
│   ├── setup.ts                  # Shared fixtures / DB truncation between tests
│   ├── routes.test.ts            # Basic E2E smoke tests
│   ├── scenarios.test.ts         # Detailed test scenarios
│   └── README.md                 # Test documentation
├── docker-compose.yml             # PostgreSQL + pgAdmin
├── package.json                   # Node dependencies
└── jest.config.ts
```

## Quick Start

### 1. Start Docker Services
```bash
cd examples/blog-api
docker compose up -d
```

This starts:
- PostgreSQL on port **5433** (offset from the default 5432 to avoid clashing with a locally running Postgres)
- pgAdmin on port 5050 (http://localhost:5050)

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults should work with the docker-compose port offset)
```

### 4. Run Database Migrations
```bash
npx prisma migrate dev --name init
npx prisma generate
```

### 5. Run Application
```bash
npm run dev
```

Visit:
- **Health Check**: http://localhost:3000/health

### 6. Run Tests
```bash
npm test
```

## Prisma Architecture

### Connection Management
```typescript
// src/config/prisma.ts
export const prisma = new PrismaClient({
  log: isDevelopment ? ['warn', 'error'] : ['warn', 'error'],
});
```
A single `PrismaClient` instance is shared app-wide (imported by every repository via constructor injection) to avoid exhausting the database connection pool.

### Repository Layer Pattern
```typescript
// src/repositories/post.repository.ts
export class PostRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async create(data: { title: string; content: string; authorId: string }): Promise<Post> {
    const row = await this.prisma.post.create({ data });
    return this.toModel(row);
  }
  // toModel() maps the Prisma row shape to the Zod-inferred domain type
}
```

### API Layer
```typescript
// src/controllers/posts.controller.ts
export async function createPost(req: Request, res: Response): Promise<void> {
  const parsed = CreatePostRequestSchema.parse(req.body);
  const post = await postService.createPost(parsed.title, parsed.content, req.user!.userId);
  res.status(201).json(post);
}
```

## Database Schema

### Users
```prisma
model User {
  id           String    @id @default(uuid())
  email        String    @unique
  passwordHash String
  fullName     String
  createdAt    DateTime  @default(now())
  posts        Post[]
  comments     Comment[]
}
```

### Posts
```prisma
model Post {
  id        String    @id @default(uuid())
  title     String
  content   String
  authorId  String
  author    User      @relation(fields: [authorId], references: [id])
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
  comments  Comment[]
}
```

### Comments
```prisma
model Comment {
  id        String   @id @default(uuid())
  postId    String
  post      Post     @relation(fields: [postId], references: [id], onDelete: Cascade)
  content   String
  authorId  String
  author    User     @relation(fields: [authorId], references: [id])
  createdAt DateTime @default(now())
}
```

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

## Testing Strategy

### E2E Tests
All tests use the real PostgreSQL database from `docker-compose.yml`:
- `tests/setup.ts` truncates every table before each test for isolation
- Tests import the Express `app` directly via Supertest (no real port bound)
- `createTestUser()` registers a fresh user with a random email per test

### Test Files
1. **routes.test.ts** - Basic smoke tests
2. **scenarios.test.ts** - Detailed scenarios with input/output docs
3. **tests/README.md** - Complete testing guide

## Key Patterns to Show Students

### 1. Zod Validation at the Controller Boundary
```typescript
const parsed = CreatePostRequestSchema.parse(req.body);
```
**Zod's `.parse()` throws a `ZodError` on invalid input — the centralized `errorHandler` middleware catches it and returns 400 automatically.**

### 2. Typed Prisma Results, No Manual Row Mapping in Controllers
```typescript
const row = await this.prisma.post.create({ data });  // row is fully typed
return this.toModel(row);                              // repository owns the DB->domain mapping
```

### 3. Layered Architecture
- **Route Layer**: HTTP method/path wiring, middleware attachment
- **Controller Layer**: Request parsing (Zod) + response shaping
- **Service Layer**: Business logic, authorization checks, error throwing
- **Repository Layer**: Prisma queries, DB row -> domain model mapping

### 4. asyncHandler Wrapper for Express 4
```typescript
router.post('/posts', requireAuth, asyncHandler(createPost));
```
Express 4 doesn't automatically forward rejected promises from `async` route handlers to error middleware — `asyncHandler` closes that gap (Express 5 fixes this natively).

### 5. Dependency Injection via Constructors
```typescript
export class PostService {
  constructor(private readonly postRepo: PostRepository) {}
}
```
Every service/repository takes its dependencies as constructor arguments, never importing a global singleton directly. This is what makes `templates/chatbot-tests.md`-style unit tests possible (inject a mock instead of a real Prisma-backed repository).

## Common Issues & Solutions

### Database Connection Errors
```bash
# Check if PostgreSQL is running
docker compose ps

# View PostgreSQL logs
docker compose logs postgres

# Restart services
docker compose restart
```

### Port Already in Use
```bash
# Change PORT in .env file
PORT=3001

# Or stop conflicting service
lsof -ti:3000 | xargs kill -9
```

### Tests Failing
```bash
# Ensure database is running
docker compose ps

# Run with verbose output
npx jest --verbose

# Run a single test file
npx jest tests/routes.test.ts
```

### Prisma Client Out of Sync
```bash
npx prisma generate
```
Run this after any change to `prisma/schema.prisma`.

## pgAdmin Access

1. Visit http://localhost:5050
2. Login:
   - Email: admin@blog.com
   - Password: admin
3. Add Server:
   - Host: `postgres` (the docker-compose service name; use `host.docker.internal` if connecting from outside the compose network)
   - Port: 5432 (the container-internal port, not the host-mapped 5433)
   - Database: blog_db
   - Username: postgres
   - Password: postgres

## Teaching Tips

### Session 1 Demo
1. Show `docker-compose.yml` (PostgreSQL setup, port offset rationale)
2. Show `prisma/schema.prisma` (relations, `@@index`, `@default(uuid())`)
3. Show one complete flow: Route → Controller → Service → Repository → Prisma
4. Run one test showing input/output (`npx jest tests/scenarios.test.ts -t "creates a post"`)
5. Use pgAdmin (or `npx prisma studio`) to show actual database records

### Key Points to Emphasize
- ✅ Prisma generates fully-typed query results — no manual row-to-object mapping bugs
- ✅ Zod validates at the boundary; the error-handling middleware converts failures to HTTP responses
- ✅ Service layer contains business logic and authorization checks
- ✅ Controllers just parse + call + respond — no business logic
- ✅ Constructor-injected dependencies make every layer independently unit-testable

### Common Student Mistakes
- ❌ Calling `prisma.post.findMany()` directly from a controller (skip the repository layer)
- ❌ Forgetting `asyncHandler()` around an async route handler (unhandled rejection instead of a clean 500)
- ❌ Returning raw Prisma rows from a repository instead of mapping through `toModel()`
- ❌ Mixing business logic (e.g. authorization checks) into the controller instead of the service

## Next Steps

After understanding this reference:
1. Walk through one endpoint completely
2. Have students trace: Request → Route → Controller → Service → Repository → Prisma → Response
3. Show how tests validate the flow
4. Let students build a similar endpoint (e.g. post tags, or a `PATCH` for comments) independently

## Stopping Services

```bash
# Stop but keep data
docker compose stop

# Stop and remove data
docker compose down -v
```
