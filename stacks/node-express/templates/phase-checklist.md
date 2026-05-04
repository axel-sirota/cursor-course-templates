# Node.js Express Phase Checklist

## Phase 0 — Skeleton

- [ ] All routes registered (return `501 Not Implemented`)
- [ ] Zod schemas defined for all request bodies
- [ ] `tsc --noEmit` passes with zero errors
- [ ] `npm run lint` passes with zero errors
- [ ] Global error middleware in place as last `app.use`

## Phase 1+ — Implementation

- [ ] Failing Jest test written before each service method implementation
- [ ] Failing Supertest test written before each controller method implementation
- [ ] No `console.log` in any file (use `pino` logger)
- [ ] All async functions propagate errors to global error handler (`next(err)`) or are covered by error boundaries
- [ ] No `any` types (use `unknown` with explicit narrowing)

## Handoff

- [ ] `npm test` — all unit tests green
- [ ] `tsc --noEmit` — zero TypeScript errors
- [ ] `npm run lint` — zero ESLint warnings or errors
- [ ] Integration test covers the happy path for each route
- [ ] Integration test covers at least one invalid-input `400` case per validated route
