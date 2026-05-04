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

## Entry Point & Structure
- **Entry point**: `src/main.ts` — bootstraps NestJS app with `NestFactory.create()`, enables `ValidationPipe` globally, starts listening
- **App module**: `src/app.module.ts` — root module, imports all feature modules
- **Config**: `@nestjs/config` with `ConfigModule.forRoot({ isGlobal: true })` — reads from `.env` via `ConfigService`
- **Test command**: `npm test` (Jest unit) or `npm run test:e2e` (supertest)

## Active Phase
- Current: Phase 0 (Skeleton)
