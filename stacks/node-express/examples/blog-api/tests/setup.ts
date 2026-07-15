import { randomUUID } from 'crypto';
import request from 'supertest';
import { PrismaClient } from '@prisma/client';
import app from '../src/app';

/**
 * Shared PrismaClient for tests. Points at DATABASE_URL, which should be
 * set to a dedicated test database (e.g. via .env.test) before running the suite.
 */
export const prisma = new PrismaClient();

export interface TestUser {
  email: string;
  password: string;
  token: string;
  userId: string;
}

/**
 * Register a fresh test user and return credentials + auth header.
 * Uses a random UUID in the email to avoid collisions across test runs.
 */
export async function createTestUser(overrides: Partial<{ email: string; password: string; fullName: string }> = {}): Promise<TestUser> {
  const email = overrides.email ?? `test-${randomUUID()}@example.com`;
  const password = overrides.password ?? 'testpass123';
  const fullName = overrides.fullName ?? 'Test User';

  const response = await request(app).post('/api/auth/register').send({ email, password, fullName });

  return {
    email,
    password,
    token: response.body.accessToken,
    userId: response.body.user.userId,
  };
}

/** Convenience helper: returns an Authorization header object for a fresh test user. */
export async function getAuthHeaders(): Promise<{ Authorization: string }> {
  const { token } = await createTestUser();
  return { Authorization: `Bearer ${token}` };
}

export function buildPostPayload(overrides: Partial<{ title: string; content: string }> = {}) {
  return {
    title: 'Test Post',
    content: 'Test content for the post.',
    ...overrides,
  };
}

/**
 * Truncate all tables between tests to keep state isolated.
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
