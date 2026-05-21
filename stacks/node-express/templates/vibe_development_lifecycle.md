# Node.js Express Development Lifecycle

## npm Scripts Discipline

Each script has one job. Never chain unrelated concerns into a single script.

| Script | Purpose |
|--------|---------|
| `npm run dev` | Local development with hot reload (`ts-node-dev --respawn`) |
| `npm test` | Unit tests only (`*.test.ts`) |
| `npm run test:integration` | Integration tests only (`*.integration.test.ts`) |
| `npm run typecheck` | `tsc --noEmit` standalone — type check without emitting JS |
| `npm run lint` | ESLint on `src/` |
| `npm run build` | Compile TypeScript to `dist/` |
| `npm start` | Run compiled JS from `dist/server.js` (production) |

Never run `npm start` in development. Never skip `typecheck` before committing.

## Feature Branch + CI

Every feature lives on a branch. The PR is the review gate.

CI pipeline (in order):
1. `npm run lint` — must pass, zero errors
2. `npm run typecheck` — must pass, zero TypeScript errors
3. `npm test` — unit tests must be green
4. `npm run test:integration` — integration tests must be green

PR is blocked until all four pass. No exceptions.

## Prisma Migration Discipline

| Environment | Command |
|-------------|---------|
| Development | `npx prisma migrate dev --name <migration-name>` — creates and applies migration, generates client |
| CI / Staging / Production | `npx prisma migrate deploy` — applies pending migrations only, does not create new ones |

Never run `migrate dev` in production. Never manually edit migration SQL files after they are applied. Migration files are checked into git.

## Commit Conventions

Follow conventional commits:

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or route |
| `fix:` | Bug fix |
| `refactor:` | Code change with no behaviour change |
| `test:` | Adding or updating tests |
| `chore:` | Build config, dependencies, tooling |
| `docs:` | Documentation only |

Examples:
- `feat: add POST /users endpoint`
- `fix: handle missing userId in getUser service`
- `refactor: extract validation middleware to shared module`
- `test: add integration tests for users router`
