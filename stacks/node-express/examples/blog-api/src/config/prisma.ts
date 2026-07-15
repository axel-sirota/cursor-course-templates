import { PrismaClient } from '@prisma/client';
import { isDevelopment } from './env';

/**
 * Singleton PrismaClient shared across the app to avoid exhausting the
 * database connection pool with a new client per request.
 */
export const prisma = new PrismaClient({
  log: isDevelopment ? ['warn', 'error'] : ['warn', 'error'],
});
