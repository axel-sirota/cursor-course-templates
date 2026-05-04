# Session 4 — Fix `node-express` (STUB → COMPLETE)

**Phase:** 1
**Parallel with:** Sessions 1, 2, 3, 5–6
**Depends on:** nothing

## Current state
```
stacks/node-express/
├── context.md
├── rules/
│   ├── node-standards.mdc      ← no numeric prefix
│   └── 500-docker-node.mdc
├── templates/
│   ├── Dockerfile
│   ├── node-starter.md
│   ├── tsconfig.json
│   └── src/
│       ├── app.ts              ← no error middleware
│       └── server.ts           ← uses console.log (violates own rule)
└── vibe/
    └── vibe_docker.md
```
No `examples/`.

---

## Files to Create / Update

```
stacks/node-express/
├── context.md                          ← UPDATE (Architecture Shape, NestJS note, ORM alternatives)
├── rules/
│   ├── 000-node-workflow.mdc           ← NEW
│   ├── 100-node-architecture.mdc       ← NEW (includes Express vs NestJS decision)
│   ├── 200-node-testing.mdc            ← NEW
│   ├── 300-node-style.mdc              ← NEW
│   ├── 400-node-standards.mdc          ← RENAME from node-standards.mdc
│   └── 500-docker-node.mdc             ← keep as-is
├── templates/
│   ├── node-starter.md                 ← UPDATE (add package.json, Zod middleware, error handler)
│   ├── phase-checklist.md              ← NEW
│   ├── tsconfig.json                   ← UPDATE (add resolveJsonModule, paths)
│   ├── package.json                    ← NEW
│   └── src/
│       ├── app.ts                      ← UPDATE (add global error middleware)
│       └── server.ts                   ← UPDATE (replace console.log with pino)
├── vibe/
│   ├── vibe_architecture.md            ← NEW
│   └── vibe_development_lifecycle.md   ← NEW
└── examples/
    └── users-resource/
        ├── users.router.ts
        ├── users.controller.ts
        ├── users.service.ts
        ├── users.repository.ts
        ├── users.schema.ts
        └── users.controller.test.ts
```

---

## File Specifications

### `context.md` additions

Add section:
```markdown
## Architecture Shape
REST API — Express layered architecture. Router → Controller → Service → Repository.
Enterprise teams with large codebases should evaluate NestJS (see `node-nestjs` stack) for
built-in DI, decorators, and module system. Express is right for small-medium APIs or teams
that prefer minimal framework overhead.
```

Update ORM note: mention Prisma (default), TypeORM (class-decorator style), Drizzle (SQL-first, type-safe).

### `rules/000-node-workflow.mdc`

Frontmatter: `description: Node.js TypeScript development workflow`, `alwaysApply: true`

Rules:
- **TDD loop**: Jest test (failing) → implement → green → refactor.
- **Type safety gate**: `tsc --noEmit` must pass before commit. Zero `any` types except at explicit boundaries.
- **CI gate**: `npm run lint` → `tsc --noEmit` → `npm test` → `npm run test:integration`. All must pass.
- **No `console.log`**: use `pino` or `winston` logger. `console.log` is forbidden in production code.
- **Async/await everywhere**: no raw Promises, no callbacks. Every async function returns `Promise<T>`.

### `rules/100-node-architecture.mdc`

Frontmatter: `description: Express layered architecture and design patterns`, `alwaysApply: true`

Rules:
- **Layer separation**: router registers routes; controller parses request, calls service, sends response; service owns business logic; repository owns data access. No cross-layer logic.
- **No logic in controllers**: controllers call one service method and send the result. If a controller has an `if` statement beyond request validation, it belongs in the service.
- **Zod at the boundary**: validate all request bodies, params, and query strings with Zod schemas. Parse with `schema.parse()` in a validation middleware, never inside controllers.
- **Global error middleware**: the last `app.use(...)` is always the error handler: `(err: Error, req: Request, res: Response, next: NextFunction)`. Never `try/catch` in individual routes.
- **Dependency injection**: pass dependencies as constructor arguments (explicit DI). Avoid module-level singletons for anything that needs to be testable.
- **When to choose NestJS instead**: project has 20+ routes, needs guards/interceptors pattern, team wants class-decorator DI, or the API will grow significantly. NestJS is not over-engineering for enterprise; Express is not under-engineering for small APIs.

### `rules/200-node-testing.mdc`

Frontmatter: `description: Jest and Supertest testing patterns`, `alwaysApply: true`

Rules:
- **Unit tests with Jest**: test service and repository logic with plain Jest. Mock dependencies with `jest.fn()` or `jest.mock()`.
- **Integration tests with Supertest**: test HTTP layer with `supertest(app)`. No mocking of HTTP internals.
- **Test database**: integration tests use a real Postgres via Testcontainers or a dedicated test database. Never mock Prisma in integration tests.
- **Test file naming**: `{name}.test.ts` for unit tests, `{name}.integration.test.ts` for integration.
- **Jest config**: `testEnvironment: 'node'`. Separate `testMatch` patterns for unit vs integration so `npm test` runs only unit tests.
- **Zod error testing**: test that invalid request bodies return `400` with structured error messages.

### `rules/300-node-style.mdc`

Frontmatter: `description: TypeScript style and naming conventions`, `alwaysApply: true`

Rules:
- **camelCase** for variables and functions. **PascalCase** for classes, interfaces, types, enums.
- **No `any`**: use `unknown` + type narrowing instead. `any` is only acceptable at JSON parse boundaries and must be immediately narrowed.
- **Import order**: external packages → internal absolute paths → relative paths. Blank line between groups. Enforced by ESLint `import/order`.
- **Explicit return types**: all exported functions have explicit return type annotations.
- **`const` over `let`**: default to `const`. Use `let` only when reassignment is genuinely needed.
- **Interface vs type**: use `interface` for object shapes that may be extended; `type` for unions, intersections, and utility types.

### `templates/src/server.ts` (UPDATE — CRITICAL FIX)

Replace `console.log` with pino:
```typescript
import pino from 'pino';
const logger = pino();

const PORT = process.env.PORT ?? 3000;
app.listen(PORT, () => {
  logger.info({ port: PORT }, 'Server started');
});
```

### `templates/src/app.ts` (UPDATE)

Add global error middleware as last `app.use`:
```typescript
import { ErrorRequestHandler } from 'express';

const errorHandler: ErrorRequestHandler = (err, req, res, next) => {
  const status = err.status ?? 500;
  res.status(status).json({
    error: err.message ?? 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  });
};

app.use(errorHandler);
```

### `templates/package.json` (NEW)

```json
{
  "scripts": {
    "build": "tsc",
    "dev": "ts-node-dev --respawn src/server.ts",
    "start": "node dist/server.js",
    "test": "jest --testPathPattern='.*\\.test\\.ts$'",
    "test:integration": "jest --testPathPattern='.*\\.integration\\.test\\.ts$'",
    "lint": "eslint src --ext .ts",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "express": "^4.21.0",
    "pino": "^9.0.0",
    "zod": "^3.23.0",
    "@prisma/client": "^5.0.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/express": "^5.0.0",
    "jest": "^29.0.0",
    "ts-jest": "^29.0.0",
    "supertest": "^7.0.0",
    "@types/supertest": "^6.0.0",
    "eslint": "^9.0.0",
    "prisma": "^5.0.0",
    "ts-node-dev": "^2.0.0"
  }
}
```

### `templates/tsconfig.json` (UPDATE)

Add missing options:
```json
{
  "compilerOptions": {
    "strict": true,
    "resolveJsonModule": true,
    "declaration": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] All routes registered (return `501`)
- [ ] Zod schemas defined for all request bodies
- [ ] `tsc --noEmit` passes
- [ ] `npm run lint` passes
- [ ] Global error middleware in place

**Phase 1+ — Implementation:**
- [ ] Failing Jest test written before service logic
- [ ] Failing Supertest test written before controller logic
- [ ] No `console.log` in any file
- [ ] All async functions have `try/catch` or propagate to global error handler
- [ ] No `any` types (use `unknown` + narrowing)

**Handoff:**
- [ ] `npm test` all green
- [ ] `tsc --noEmit` zero errors
- [ ] `npm run lint` zero warnings
- [ ] Integration test covers happy path for each route

### `vibe/vibe_architecture.md`

Sections:
- **Express vs NestJS decision**: Express is a minimal router + middleware layer — you own all structure. NestJS is opinionated DI + module system — it owns structure for you. Choose Express when: team is small, API is small-medium, or framework overhead is undesirable. Choose NestJS when: enterprise team, need guards/interceptors, prefer class-decorator DI, or the codebase will grow large.
- **ORM decision**: Prisma (type-safe schema-first, great DX, recommended default) vs TypeORM (class-decorator entities, mature, familiar to Java devs) vs Drizzle (SQL-first, zero runtime overhead, type-safe). Prisma for greenfield. TypeORM when team knows it or migrating from Java Spring. Drizzle when raw SQL control matters.
- **Zod philosophy**: validate at the boundary, trust internally. Once a request passes Zod, trust the types. Don't re-validate inside services.
- **Error handling model**: throw typed errors in services; global middleware catches and formats. Never expose stack traces in production.
- **When Node/Express over Go/Java**: event-loop I/O model wins for high-concurrency I/O-bound work. Worse for CPU-bound work. Node is the right call for Salesforce-style API gateways and Travelers-style insurance form APIs where I/O dominates.

### `vibe/vibe_development_lifecycle.md`

- npm scripts discipline: `dev` for local, `test` for unit, `test:integration` for integration, `typecheck` standalone
- Feature branch + CI: PR blocks if `lint`, `typecheck`, or `test` fail
- Prisma migration discipline: `prisma migrate dev` in development, `prisma migrate deploy` in CI
- Commit conventions: `feat:`, `fix:`, `refactor:`, `test:`

### `examples/users-resource/`

Six TypeScript files:
- `users.schema.ts` — Zod schemas: `CreateUserSchema`, `UserParamsSchema`
- `users.repository.ts` — `UsersRepository` class; takes Prisma client; CRUD methods with typed returns
- `users.service.ts` — `UsersService` class; takes `UsersRepository`; business logic + error throwing
- `users.controller.ts` — `UsersController` class; takes `UsersService`; 3 methods (create, getById, list) with `next(err)` propagation
- `users.router.ts` — Express router; instantiates controller; wires Zod validation middleware + handlers
- `users.controller.test.ts` — Jest unit tests for controller; mocks service with `jest.fn()`

---

## Acceptance Criteria

- [ ] `ls stacks/node-express/rules/` shows 6 files (000–500)
- [ ] `ls stacks/node-express/templates/` shows `package.json`, `phase-checklist.md`, `tsconfig.json`, `node-starter.md`, `Dockerfile`, `src/`
- [ ] `templates/src/server.ts` contains `pino` (zero `console.log`)
- [ ] `templates/src/app.ts` contains `ErrorRequestHandler` global error middleware
- [ ] `ls stacks/node-express/vibe/` shows 2 docs
- [ ] `ls stacks/node-express/examples/users-resource/` shows 6 `.ts` files
- [ ] `vibe_architecture.md` contains "Express vs NestJS decision" section
- [ ] `rules/100-node-architecture.mdc` contains "When to choose NestJS instead"
