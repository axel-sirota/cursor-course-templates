import { ErrorRequestHandler } from 'express';
import { ZodError } from 'zod';
import { AppError } from '../errors';
import { logger } from '../config/logger';

/**
 * Centralized error-handling middleware. Registered LAST in app.ts, after all routes.
 * Maps known error types to HTTP status codes; logs and returns 500 for
 * anything unrecognized (never leaks internal error details to the client).
 */
export const errorHandler: ErrorRequestHandler = (err, req, res, _next) => {
  if (err instanceof ZodError) {
    res.status(400).json({ detail: err.issues.map((i) => i.message).join(', ') });
    return;
  }

  if (err instanceof AppError) {
    res.status(err.statusCode).json({ detail: err.message });
    return;
  }

  logger.error({ err, correlationId: req.id }, 'Unhandled error');
  res.status(500).json({ detail: 'Internal server error' });
};
