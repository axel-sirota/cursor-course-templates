# NestJS Phase Checklist

## Phase 0 — Skeleton

**Module Structure**
- [ ] All feature modules generated with `nest g module`, `nest g controller`, `nest g service`
- [ ] Each module has correct `controllers`, `providers`, `imports`, `exports` arrays in `@Module()`
- [ ] Feature modules imported in `AppModule`
- [ ] `TypeOrmModule.forRoot(...)` configured in `AppModule` with `autoLoadEntities: true`

**Application Bootstrap**
- [ ] `main.ts` has global `ValidationPipe` with `whitelist: true, forbidNonWhitelisted: true, transform: true`
- [ ] `main.ts` has global `ClassSerializerInterceptor` with `app.get(Reflector)`
- [ ] Swagger setup in `main.ts` (accessible at `/api`)
- [ ] `PORT` environment variable respected

**Routes**
- [ ] All routes registered (can return `501 Not Implemented` at this stage)
- [ ] Route parameters use appropriate pipes (`ParseUUIDPipe`, `ParseIntPipe`)
- [ ] Auth-protected routes decorated with `@UseGuards(JwtAuthGuard)`

**Type Safety**
- [ ] `tsc --noEmit` passes with zero errors
- [ ] No `any` types in controllers, services, or repositories
- [ ] All DTOs defined (even if empty — no fields required yet)
- [ ] All entity classes defined with correct TypeORM decorators

---

## Phase 1 — Core Implementation

**Test-Driven**
- [ ] Failing unit test written before each service method
- [ ] Failing e2e test written before each controller route
- [ ] All tests passing before moving to next method

**Request Validation**
- [ ] All POST/PUT/PATCH DTOs have complete `class-validator` decorators
- [ ] `@ApiProperty()` with `description` and `example` on every DTO field
- [ ] `ValidationPipe` rejects invalid payloads (manually tested or e2e covered)

**Business Logic**
- [ ] All business logic in services — zero conditional logic in controllers
- [ ] Services throw typed NestJS exceptions (`NotFoundException`, `ConflictException`, etc.)
- [ ] No raw `Error` objects thrown from services

**Auth & Security**
- [ ] `JwtAuthGuard` applied to all protected routes
- [ ] `@Exclude()` on all sensitive entity fields (passwords, tokens, secrets)
- [ ] Password stored as hash — never plaintext

**Data Layer**
- [ ] TypeORM entities have complete column definitions with types and constraints
- [ ] Repository methods typed with explicit return types
- [ ] No raw SQL queries unless documented with explanation

---

## Phase 2 — Hardening

**Testing**
- [ ] Service unit test coverage ≥ 90%
- [ ] Controller unit tests cover all happy paths and error cases
- [ ] E2e tests cover all routes (happy path + validation error + auth failure)

**Error Handling**
- [ ] All domain errors surface as appropriate HTTP status codes
- [ ] Error responses have consistent shape `{ message: string, statusCode: number }`
- [ ] No stack traces leaked in production responses (`NODE_ENV=production`)

**Performance**
- [ ] Database queries use appropriate indexes (check with `EXPLAIN ANALYZE`)
- [ ] N+1 queries eliminated (use `relations` or query builder with `leftJoinAndSelect`)
- [ ] Response pagination on list endpoints (no unbounded `findAll()`)

---

## Handoff Criteria

- [ ] `npm run lint` — zero errors
- [ ] `tsc --noEmit` — zero type errors
- [ ] `npm test` — all unit tests green
- [ ] `npm run test:e2e` — all e2e tests green
- [ ] Swagger docs accessible at `/api` with all routes documented
- [ ] `@Exclude()` on all sensitive entity fields — verified via e2e test asserting fields absent in response
- [ ] Docker image builds successfully: `docker build -t app .`
- [ ] `docker-compose up` starts app + database with no manual steps
- [ ] README documents: local setup, env vars required, how to run tests
