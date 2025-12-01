# Project Context: Node.js Express

## Tech Stack
- **Language**: TypeScript (Strict Mode)
- **Framework**: Express.js
- **Database**: PostgreSQL (Prisma ORM)
- **Testing**: Jest (Unit), Supertest (Integration)
- **Linting**: ESLint, Prettier

## Vibe & Style
- **Coding Style**: camelCase for vars/funcs, PascalCase for classes/interfaces.
- **Architecture**: Layered MVC.
  - `src/controllers/` (HTTP handling)
  - `src/services/` (Business Logic)
  - `src/repositories/` (Data Access / Prisma calls)
  - `src/routes/` (Express Routers)
- **Validation**: Zod (Runtime validation for all inputs).

## Key Rules
- **No Logic in Controllers**: Controllers only parse requests and send responses. Logic is in Services.
- **Async/Await**: Always use `async/await`, never explicit Promises or callbacks.
- **Error Handling**: Use a global Error Middleware. Do not `console.log` errors (use a logger).
- **Dependency Injection**: Use explicit dependency injection or a container (Inversify) is optional but clean separation is mandatory.

## Active Phase
- Current: Phase 0 (Skeleton)

