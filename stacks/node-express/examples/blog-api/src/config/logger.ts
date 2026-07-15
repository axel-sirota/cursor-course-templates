import pino from 'pino';
import { isDevelopment } from './env';

/**
 * Structured logger. Pretty-printed in development, JSON in production.
 */
export const logger = pino({
  level: isDevelopment ? 'debug' : 'info',
  transport: isDevelopment
    ? { target: 'pino-pretty', options: { colorize: true, translateTime: 'HH:MM:ss' } }
    : undefined,
});
