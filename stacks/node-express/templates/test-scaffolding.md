# Test Scaffolding Template (Jest + Supertest)

This is the Node/Jest equivalent of a `conftest.py`: a shared `tests/setup.ts` that every layer (skeleton mock endpoints, E2E route tests, unit tests) can import from. Copy this into new projects verbatim and adapt entity-specific fixtures.

## jest.config.ts

```typescript
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],
  collectCoverageFrom: ['src/**/*.ts', '!src/server.ts'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  clearMocks: true,
};

export default config;
```

## tests/setup.ts

```typescript
import { randomUUID } from 'crypto';
import request from 'supertest';
import { PrismaClient } from '@prisma/client';
import app from '../src/app';

/**
 * Shared PrismaClient for tests. Points at DATABASE_URL from .env.test
 * (a dedicated test database, never the dev database).
 */
export const prisma = new PrismaClient();

/**
 * Register a fresh test user and return credentials + auth header.
 * Uses a random UUID in the email to avoid collisions across test runs.
 */
export async function createTestUser(): Promise<{
  email: string;
  password: string;
  token: string;
  userId: string;
}> {
  const email = `test-${randomUUID()}@example.com`;
  const password = 'testpass123';

  const response = await request(app)
    .post('/api/auth/register')
    .send({ email, password, fullName: 'Test User' });

  return {
    email,
    password,
    token: response.body.accessToken,
    userId: response.body.user.userId,
  };
}

/**
 * Convenience helper: returns an Authorization header object for a fresh test user.
 */
export async function getAuthHeaders(): Promise<{ Authorization: string }> {
  const { token } = await createTestUser();
  return { Authorization: `Bearer ${token}` };
}

/**
 * Returns a supertest client bound to the Express app (no server.listen() needed —
 * Supertest binds directly to the app's request handler on an ephemeral port).
 */
export function client() {
  return request(app);
}

/**
 * Truncate all tables between tests to keep state isolated.
 * Prefer this over full `prisma migrate reset` for per-test speed.
 */
export async function resetDatabase(): Promise<void> {
  const tables = await prisma.$queryRaw<Array<{ tablename: string }>>`
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  `;
  for (const { tablename } of tables) {
    if (tablename !== '_prisma_migrations') {
      await prisma.$executeRawUnsafe(`TRUNCATE TABLE "${tablename}" CASCADE;`);
    }
  }
}

beforeEach(async () => {
  await resetDatabase();
});

afterAll(async () => {
  await prisma.$disconnect();
});
```

## Alternative: Transaction Rollback Strategy

If truncating between tests is too slow for a large suite, wrap each test in a Prisma interactive transaction and roll it back instead of committing:

```typescript
// tests/setup.ts (transactional variant)
import { PrismaClient } from '@prisma/client';

let rollback: () => Promise<void>;

beforeEach(async () => {
  await new Promise<void>((resolve) => {
    prisma.$transaction(async (tx) => {
      // Swap the app's prisma instance for `tx` here via dependency injection
      // (requires the app/service layer to accept an injected client).
      rollback = async () => {
        throw new Error('ROLLBACK');
      };
      resolve();
      await new Promise(() => {}); // keep the transaction open until rollback() throws
    }).catch(() => undefined);
  });
});

afterEach(async () => {
  await rollback();
});
```

This pattern requires the repository layer to accept an injected `PrismaClient | Prisma.TransactionClient`, which is a larger refactor — most course projects should start with the simpler truncate-between-tests approach above and only move to transaction rollback if test suite speed becomes a real bottleneck.

## Fixture Factories

Keep entity-specific builders next to the tests that use them, or in a `tests/fixtures/` folder if shared across many files:

```typescript
// tests/fixtures/post.fixture.ts
export function buildPostPayload(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    title: 'Test Post',
    content: 'Test content',
    ...overrides,
  };
}
```

## .env.test

```
NODE_ENV=test
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_db_test
JWT_SECRET=test-secret-not-for-production
```

Point Jest at this file via `dotenv/config` in a global setup script, or export it before running `npx jest`:

```bash
NODE_ENV=test npx dotenv -e .env.test -- jest
```

## npm scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```
