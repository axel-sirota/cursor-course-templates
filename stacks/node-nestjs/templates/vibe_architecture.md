# Architecture Vibe: Node.js NestJS

## Why NestJS over Express

Express is a routing layer. NestJS is an application framework. Choose deliberately:

| Choose NestJS when... | Choose Express when... |
|---|---|
| Team size > 3 | Solo project or 2-person team |
| API has > 20 routes | Small API, < 10 routes |
| Need auth guards / RBAC | Simple API-key auth or no auth |
| Want Swagger auto-generated | No external API consumers |
| Planning microservices | Single monolith, no service evolution planned |
| Team has Java/Spring background | Team strongly prefers functional style |

NestJS provides opinions that Express leaves to you: DI container, module system, guards/interceptors lifecycle, Swagger generation, built-in pipes for validation. These opinions pay for themselves on projects that outlive their initial sprint.

## Module Design

One module = one domain concept. This is the single most important NestJS decision.

```
AppModule
  ├── ConfigModule (global infrastructure)
  ├── TypeOrmModule (global infrastructure)
  ├── AuthModule            ← auth domain
  ├── UsersModule           ← users domain
  ├── OrdersModule          ← orders domain
  └── NotificationsModule   ← notifications domain
```

Modules export services — never individual classes. When `OrdersModule` needs user data, it imports `UsersModule` and injects `UsersService`. It never reaches into `UsersRepository` directly.

This boundary enforcement is what prevents the codebase from becoming a tangle of cross-module imports after 6 months of feature development.

## The NestJS Request Lifecycle

Understanding this prevents the classic "where do I put this logic?" confusion:

```
HTTP Request
    ↓
Middleware              (e.g., cors, helmet, body-parser — runs before NestJS sees the request)
    ↓
Guards                  (AuthGuard, RolesGuard — CAN abort with 401/403)
    ↓
Interceptors (before)   (LoggingInterceptor records start time; TransformInterceptor wraps body)
    ↓
Pipes                   (ValidationPipe validates DTO; ParseUUIDPipe transforms :id param)
    ↓
Controller Handler      (one line: calls service, returns result)
    ↓
Service                 (business logic lives here — all of it)
    ↓
Repository / DB         (data access — typed queries, no raw SQL unless necessary)
    ↑
Interceptors (after)    (LoggingInterceptor records duration; ClassSerializerInterceptor applies @Exclude())
    ↑
HTTP Response
```

Decision rule: if your logic touches auth/authorization → Guard. Cross-cutting before/after → Interceptor. Input shape/coercion → Pipe. Business rule → Service. Data access → Repository.

## TypeORM vs Prisma in NestJS

Both are first-class citizens. Choose based on team profile:

**TypeORM** (default for enterprise):
- `@Entity()`, `@Column()`, `@OneToMany()` decorators — natural for Java developers
- Integrates via `@nestjs/typeorm`, `TypeOrmModule.forFeature([Entity])`
- `getRepository(Entity)` for queries; query builder for complex joins
- Migration system: `typeorm migration:generate` → review → `typeorm migration:run`
- Weakness: TypeScript types are less precise than Prisma; relation loading can surprise you

**Prisma** (greenfield preference):
- Schema-first (`schema.prisma`) — single source of truth
- Better TypeScript type inference — generated client has exact types
- No decorators on models — cleaner separation of ORM from domain
- `PrismaService` wraps `PrismaClient` and is injected like any other NestJS provider
- Migration system: `prisma migrate dev` → `prisma migrate deploy`
- Weakness: less mature NestJS ecosystem; Prisma Studio is good but different mental model

Rule: **TypeORM for teams with Java/Spring background or existing TypeORM projects. Prisma for greenfield with strong TypeScript focus.**

## Microservices with NestJS

`@nestjs/microservices` adds transport layers — Kafka, Redis Pub/Sub, RabbitMQ, gRPC, NATS — while keeping the same module/controller/service pattern.

Evolution path:
1. Start as a monolith — all modules in one app
2. Identify bounded contexts that need independent scaling
3. Extract module to a standalone NestJS app, replace direct calls with message patterns
4. Same guards/interceptors/pipes work in both HTTP and microservice contexts

The key: NestJS lets you evolve from monolith to microservices without rewriting application logic. Only the transport layer changes.

## Configuration Management

Use `@nestjs/config` with Joi validation schema. Never access `process.env` directly in services:

```typescript
// app.module.ts
ConfigModule.forRoot({
  isGlobal: true,
  validationSchema: Joi.object({
    DATABASE_URL: Joi.string().required(),
    JWT_SECRET: Joi.string().min(32).required(),
    PORT: Joi.number().default(3000),
    NODE_ENV: Joi.string().valid('development', 'production', 'test').required(),
  }),
})
```

Services inject `ConfigService` and call `config.get<string>('DATABASE_URL')`. Validation at startup fails fast rather than crashing at runtime.
