# Session 8 — New Stack: `node-nestjs`

**Phase:** 3 — Group A (engineer persona)
**Parallel with:** Sessions 7, 9–12
**Depends on:** Sessions 1–6 complete
**Client fit:** Salesforce, Travelers (enterprise Node.js APIs)

## Architecture Shape
REST API (enterprise) — NestJS module/decorator pattern. Built-in DI, guards, interceptors. TypeScript-first.

---

## Files to Create

```
stacks/node-nestjs/
├── context.md
├── rules/
│   ├── 000-nestjs-workflow.mdc
│   ├── 100-nestjs-architecture.mdc
│   ├── 200-nestjs-testing.mdc
│   ├── 300-nestjs-style.mdc
│   └── 500-docker-nestjs.mdc
├── templates/
│   ├── nestjs-starter.md
│   ├── phase-checklist.md
│   └── package.json
├── vibe/
│   ├── vibe_architecture.md
│   └── vibe_development_lifecycle.md   (references stacks/shared/)
└── examples/
    └── users-module/
        ├── users.module.ts
        ├── users.controller.ts
        ├── users.service.ts
        ├── users.repository.ts
        ├── dto/create-user.dto.ts
        ├── entities/user.entity.ts
        └── users.controller.spec.ts
```

---

## File Specifications

### `context.md`

```markdown
# Project Context: Node.js NestJS

## Tech Stack
- Language: TypeScript 5+ (strict mode)
- Framework: NestJS 10+
- ORM: TypeORM (default for enterprise) or Prisma (greenfield)
- Database: PostgreSQL
- Testing: Jest (unit), Supertest (e2e)
- Validation: class-validator + class-transformer
- Auth: @nestjs/passport + passport-jwt
- Linting: ESLint + Prettier

## Architecture Shape
REST API (enterprise) — NestJS module system with DI, guards, interceptors, pipes.
Use for: large enterprise APIs, teams wanting class-decorator DI, microservices with @nestjs/microservices.
Use node-express for: small APIs, minimal framework preference, quick prototypes.

## Vibe & Style
- Coding Style: camelCase functions/variables, PascalCase classes/decorators.
- Architecture: Feature modules. Each feature is a module with controller, service, repository, DTOs, entity.
- Pattern: Module → Controller → Service → Repository. Guards before controllers. Pipes for validation.

## Key Rules
- One module per feature. Never import individual classes across module boundaries — export the module.
- Business logic in services only. Controllers are thin (parse → call service → return).
- DTOs with class-validator for all inputs. Never accept raw `any` from the request.
- Guards for authentication/authorization. Never check JWT in a controller.
- Interceptors for cross-cutting: logging, response transformation, caching.

## Active Phase
- Current: Phase 0 (Skeleton)
```

### `rules/000-nestjs-workflow.mdc`

- **Module-first**: generate module before controller or service. `nest g module users` → `nest g controller users` → `nest g service users`.
- **TDD loop**: write failing Jest unit test → implement service → green. Write failing e2e test → implement controller → green.
- **CI gate**: `npm run lint` → `tsc --noEmit` → `npm test` → `npm run test:e2e`. All pass.
- **No circular imports**: NestJS DI fails silently on circular deps. Use `forwardRef()` only as last resort; redesign if needed.

### `rules/100-nestjs-architecture.mdc`

- **Feature modules**: every domain concept is a module (`UsersModule`, `OrdersModule`). AppModule only imports feature modules and global infrastructure modules.
- **No big AppModule**: if `AppModule` directly imports >5 feature modules it's fine; if it's importing 40 things, introduce domain modules grouping related features.
- **Controllers are thin**: one service call per handler method. No business logic, no `if` statements beyond guard delegation.
- **DTOs for every input**: `CreateUserDto` with `@IsString()`, `@IsEmail()` etc. Use `ValidationPipe` globally. Never trust raw request body.
- **Response DTOs**: transform entities to response DTOs in service layer. Never return raw TypeORM entities — they expose relations and sensitive fields.
- **Guards for auth**: `@UseGuards(JwtAuthGuard)` on controllers or specific routes. Never decode JWT inside controllers.
- **Interceptors for cross-cutting**: `ClassSerializerInterceptor` for `@Exclude()` fields. Custom interceptors for logging, tracing.
- **Pipes for transformation**: `ParseIntPipe`, `ParseUUIDPipe` on route params. Never cast manually.
- **Exception filters**: use `@Catch()` exception filter for domain errors. `HttpException` for HTTP errors.

### `rules/200-nestjs-testing.mdc`

- **Unit tests with `Test.createTestingModule`**: for services and controllers. Mock dependencies with `jest.fn()` providers.
- **E2e tests with Supertest**: `@nestjs/testing` + `INestApplication`. Real HTTP calls against the full NestJS app.
- **Test database**: e2e tests use a real Postgres via Testcontainers or a dedicated test schema.
- **Controller unit tests**: use `Test.createTestingModule({ controllers: [UsersController], providers: [{ provide: UsersService, useValue: mockService }] })`.
- **Service unit tests**: mock repository with `jest.fn()` implementations.
- **Test naming**: `describe('UsersService')` → `describe('createUser')` → `it('should return created user')`.

### `rules/300-nestjs-style.mdc`

- **Decorators**: decorators are the NestJS vocabulary. Use them. Don't fight the framework's opinions.
- **`@Exclude()` on sensitive fields**: password hashes, secrets — annotate with `@Exclude()` from `class-transformer` and use `ClassSerializerInterceptor` globally.
- **`@ApiProperty()` for Swagger**: every DTO field gets `@ApiProperty()` with description and example. Non-optional in enterprise context.
- **Naming conventions**: `{Resource}Module`, `{Resource}Controller`, `{Resource}Service`, `{Resource}Repository`. DTOs: `Create{Resource}Dto`, `Update{Resource}Dto`, `{Resource}ResponseDto`.
- **No `any`**: strict TypeScript. All providers typed. Repository return types explicit.

### `templates/nestjs-starter.md`

Scaffold showing NestJS feature module structure:
```
src/
  app.module.ts              (imports feature modules, global pipes/guards/interceptors)
  main.ts                    (bootstrap, global validation pipe, swagger setup)
  users/
    users.module.ts
    users.controller.ts
    users.service.ts
    users.repository.ts      (TypeORM repository wrapper or Prisma service)
    dto/
      create-user.dto.ts
      update-user.dto.ts
      user-response.dto.ts
    entities/
      user.entity.ts
    guards/
      (resource-specific guards if needed)
  shared/
    guards/
      jwt-auth.guard.ts
    interceptors/
      logging.interceptor.ts
    filters/
      http-exception.filter.ts
    pipes/
      (global pipes registered in main.ts)
```

Include `main.ts` showing:
```typescript
app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true }));
app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector)));
```

### `templates/package.json`

```json
{
  "scripts": {
    "build": "nest build",
    "dev": "nest start --watch",
    "start": "node dist/main",
    "test": "jest",
    "test:e2e": "jest --config jest-e2e.json",
    "lint": "eslint src --ext .ts",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/typeorm": "^10.0.0",
    "typeorm": "^0.3.0",
    "pg": "^8.0.0",
    "class-validator": "^0.14.0",
    "class-transformer": "^0.5.0",
    "@nestjs/passport": "^10.0.0",
    "passport-jwt": "^4.0.0",
    "reflect-metadata": "^0.2.0"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "typescript": "^5.5.0",
    "jest": "^29.0.0",
    "supertest": "^7.0.0",
    "@types/supertest": "^6.0.0"
  }
}
```

### `templates/phase-checklist.md`

**Phase 0 — Skeleton:**
- [ ] All feature modules generated (`nest g module`, `nest g controller`, `nest g service`)
- [ ] Routes registered (return `501`)
- [ ] Global `ValidationPipe` configured in `main.ts`
- [ ] `tsc --noEmit` passes

**Phase 1+ — Implementation:**
- [ ] Failing unit test before service logic
- [ ] Failing e2e test before controller logic
- [ ] All request DTOs have `class-validator` decorators
- [ ] No business logic in controllers
- [ ] Guards in place for auth-protected routes

**Handoff:**
- [ ] `npm test` all green
- [ ] `npm run test:e2e` all green
- [ ] Swagger docs auto-generated and accessible at `/api`
- [ ] `@Exclude()` on all sensitive entity fields

### `vibe/vibe_architecture.md`

- **Why NestJS over Express**: NestJS provides opinions that Express leaves to you — DI container, module system, guards/interceptors lifecycle, Swagger generation. Choose NestJS when: team size >3, API >20 routes, need auth guards/RBAC, want Swagger auto-generated, or planning microservices.
- **Module design**: one module = one domain concept. Modules export services for other modules to inject. Never import individual classes — import the module.
- **The NestJS lifecycle**: Request → Guards → Interceptors (before) → Pipes → Controller → Service → Interceptors (after) → Response. Understanding this prevents "where do I put this logic?" questions.
- **TypeORM vs Prisma in NestJS**: TypeORM integrates natively via `@nestjs/typeorm` and `@Entity()` decorators — natural fit for Java developers. Prisma is schema-first, better type inference, no decorators on entities. Pick TypeORM for Salesforce/enterprise Java-background teams, Prisma for greenfield.
- **Microservices with NestJS**: `@nestjs/microservices` adds Kafka, Redis, RabbitMQ, gRPC transports. Same module/controller pattern; swap HTTP for message patterns. Good for event-driven evolution of an existing NestJS app.

### `vibe/vibe_development_lifecycle.md`

References `stacks/shared/`. Adds NestJS-specific:
- NestJS CLI workflow: always generate with `nest g` to get correct boilerplate
- TypeORM migration discipline: `typeorm migration:generate` → review → `typeorm migration:run` in CI
- Swagger-first for enterprise: generate swagger at startup; API contract visible to consumers

### `examples/users-module/`

Seven files — complete NestJS feature module:
- `users.module.ts` — imports TypeOrmModule, exports UsersService
- `entities/user.entity.ts` — TypeORM `@Entity` with `@Exclude()` on password
- `dto/create-user.dto.ts` — `@IsString`, `@IsEmail`, `@ApiProperty` on all fields
- `users.repository.ts` — wraps TypeORM Repository; typed CRUD methods
- `users.service.ts` — injects repository; business logic; throws `NotFoundException`
- `users.controller.ts` — `@Controller('users')`, `@UseGuards(JwtAuthGuard)`, 3 routes
- `users.controller.spec.ts` — Jest unit test with mock service via `Test.createTestingModule`

---

## Acceptance Criteria

- [ ] `ls stacks/node-nestjs/rules/` shows 5 files
- [ ] `ls stacks/node-nestjs/templates/` shows 3 files
- [ ] `ls stacks/node-nestjs/vibe/` shows 2 docs
- [ ] `ls stacks/node-nestjs/examples/users-module/` shows 7 files
- [ ] `context.md` Architecture Shape = "REST API (enterprise)"
- [ ] `rules/100-nestjs-architecture.mdc` contains "Guards for auth" rule
- [ ] `vibe_architecture.md` contains "Why NestJS over Express" section
- [ ] `templates/nestjs-starter.md` shows module structure with guards/interceptors/pipes
