# Development Lifecycle Vibe: Node.js NestJS

> This document builds on `stacks/shared/` general lifecycle practices and adds NestJS-specific workflow.

## NestJS CLI Workflow

**Always generate with `nest g`**. Never hand-write module, controller, or service boilerplate from scratch.

```bash
# Generate a complete feature module scaffold
nest g module orders
nest g controller orders --no-spec   # or with spec: nest g controller orders
nest g service orders

# Generate a guard
nest g guard shared/guards/jwt-auth

# Generate an interceptor
nest g interceptor shared/interceptors/logging

# Generate a filter
nest g filter shared/filters/http-exception
```

Why: `nest g` creates the correct decorator boilerplate AND auto-updates the parent module's `providers`, `controllers`, and `imports` arrays. Missing this step leads to "provider not found" DI errors that are hard to debug.

## TypeORM Migration Discipline

**Never use `synchronize: true` in production.** It auto-runs DDL against your live database. Use it only for local development with `NODE_ENV=development`.

Migration workflow:

```bash
# 1. Generate migration from entity changes
npx typeorm migration:generate src/migrations/AddOrdersTable -d src/data-source.ts

# 2. Review the generated SQL — always check what TypeORM generated
cat src/migrations/*AddOrdersTable.ts

# 3. Run migration locally
npx typeorm migration:run -d src/data-source.ts

# 4. In CI/CD — migrations run before app deployment
# (Ensure data-source.ts reads DATABASE_URL from env)
```

Migration files are committed to source control. They are the authoritative record of schema changes. Never delete or edit a migration that has been applied to any environment.

## Swagger-First for Enterprise

In enterprise context, the Swagger UI at `/api` is the API contract for frontend teams and external consumers. Treat it as a first-class deliverable.

Practices:
- `@ApiTags('users')` on every controller — groups routes in Swagger UI
- `@ApiResponse()` for each HTTP status a route can return
- `@ApiBearerAuth()` on protected controllers so Swagger UI shows the auth token input
- `@ApiProperty({ description, example })` on every DTO field — non-negotiable

Verify before handoff:
```bash
npm run dev
open http://localhost:3000/api
# Manually verify: all routes visible, auth lock icon shows, can send test requests
```

## Local Development Loop

```bash
# 1. Start database
docker-compose up db -d

# 2. Run migrations
npx typeorm migration:run -d src/data-source.ts

# 3. Start app in watch mode
npm run dev

# 4. Run tests in watch mode (separate terminal)
npm test -- --watch
```

## CI Pipeline

```yaml
# .github/workflows/ci.yml (abbreviated)
steps:
  - run: npm ci
  - run: npm run lint
  - run: npm run typecheck          # tsc --noEmit
  - run: npm test -- --coverage
  - run: docker-compose up db -d    # start test database
  - run: npm run test:e2e
```

All four gates must pass. No exceptions. A PR with failing tests does not get reviewed.

## Feature Branch Lifecycle

```
1. Cut branch: git checkout -b feature/TICKET-123-add-orders-api
2. Generate scaffold: nest g module orders && nest g controller orders && nest g service orders
3. Write failing unit test for first service method
4. Implement until green
5. Write failing e2e test for first route
6. Implement until green
7. Repeat for remaining methods/routes
8. npm run lint && tsc --noEmit && npm test && npm run test:e2e — all green
9. Open PR → code review → merge
```

## Common Debugging Patterns

**"Cannot find provider" / DI not resolving:**
- Check the provider is listed in the module's `providers` array
- Check the module is imported in `AppModule` (or the consuming module)
- If using `@InjectRepository(Entity)`, check `TypeOrmModule.forFeature([Entity])` is in the module's `imports`

**"Circular dependency detected":**
- Do NOT add `forwardRef()` as the first instinct
- Redesign: extract a shared service that both modules depend on
- If you truly need `forwardRef()`, document why with a comment

**"Validation not triggering":**
- Check `app.useGlobalPipes(new ValidationPipe(...))` is in `main.ts` before `app.listen()`
- Check DTO properties have `class-validator` decorators
- Check `transform: true` is set if you need auto-transformation

**"@Exclude() not working":**
- Check `app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector)))` in `main.ts`
- Check the entity/DTO is instantiated as a class instance (not a plain object) — use `plainToInstance()`
