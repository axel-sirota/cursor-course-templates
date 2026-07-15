import { NextFunction, Request, Response } from 'express';

type AsyncRouteHandler = (req: Request, res: Response, next: NextFunction) => Promise<void>;

/**
 * Wraps an async Express route handler so any rejected promise (including a
 * thrown Zod/AppError inside an async function) is forwarded to next(),
 * reaching the centralized errorHandler instead of crashing the process.
 * Express 4 does not do this automatically (Express 5 does).
 */
export function asyncHandler(handler: AsyncRouteHandler) {
  return (req: Request, res: Response, next: NextFunction): void => {
    handler(req, res, next).catch(next);
  };
}
