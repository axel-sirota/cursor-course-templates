# Node.js Express Architecture Decisions

## Express vs NestJS Decision

Express is a minimal router + middleware layer — you own all structure. NestJS is an opinionated DI + module system — it owns structure for you.

**Choose Express when:**
- Team is small (1–5 engineers).
- API is small-to-medium (under 20 routes).
- You want minimal framework overhead and full control over architecture.
- Speed of initial setup matters more than long-term scaffolding consistency.

**Choose NestJS when:**
- Enterprise team that needs a shared, enforced structure.
- Need built-in guards, interceptors, and pipes pattern (auth, rate limiting, logging).
- Team prefers class-decorator DI and wants a pattern familiar from Spring/Angular.
- The codebase will grow large and module boundaries matter.

Neither is wrong. Express is not under-engineering for small APIs. NestJS is not over-engineering for enterprise.

## ORM Decision

**Prisma** (recommended default):
- Schema-first. Write `schema.prisma`, get a fully type-safe generated client.
- Best DX in the ecosystem. Migrations are first-class.
- Use for all greenfield projects unless there is a specific reason to choose otherwise.

**TypeORM**:
- Class-decorator entities (similar to JPA/Hibernate).
- Mature and battle-tested.
- Choose when the team is migrating from a Java/Spring codebase or already knows TypeORM well.

**Drizzle**:
- SQL-first. Write SQL-like TypeScript, get type-safe queries.
- Zero runtime overhead.
- Choose when raw SQL control matters or when Prisma's query engine overhead is a concern.

## Zod Philosophy

Validate at the boundary, trust internally.

- All untrusted input (request body, query params, path params, environment variables) is validated with Zod at the entry point.
- Once a value passes a Zod schema, treat the inferred TypeScript type as ground truth throughout the service and repository layers.
- Do not re-validate inside services or repositories. Doing so is redundant and creates inconsistency.

## Error Handling Model

- Services throw typed errors (e.g., `class NotFoundError extends Error { status = 404 }`).
- Controllers do not `try/catch` — they call services and forward errors with `next(err)`.
- The global error middleware in `app.ts` catches all errors, formats them, and sends the response.
- Stack traces are included in `development` mode only. Never expose stack traces in production.

## When Node/Express Over Go or Java

Node's event loop model excels at high-concurrency I/O-bound workloads — many simultaneous connections waiting on database, network, or file I/O. It is the wrong choice for CPU-bound work (image processing, heavy computation).

**Node is the right call for:**
- API gateways that proxy and aggregate downstream services.
- Form-heavy CRUD APIs (insurance, finance, HR) where I/O dominates.
- Real-time features (webhooks, SSE, WebSockets) that need many open connections.
- Teams already strong in JavaScript/TypeScript who don't want a context switch.
