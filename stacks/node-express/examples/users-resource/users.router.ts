import { Router, Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import { PrismaClient } from '@prisma/client';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';
import { UsersRepository } from './users.repository';
import {
  CreateUserSchema,
  UserParamsSchema,
  ListUsersQuerySchema,
} from './users.schema';

// Validation middleware factory
const validate =
  (schema: ZodSchema, target: 'body' | 'params' | 'query' = 'body') =>
  (req: Request, res: Response, next: NextFunction): void => {
    const result = schema.safeParse(req[target]);
    if (!result.success) {
      res.status(400).json({
        error: 'Validation failed',
        issues: result.error.issues,
      });
      return;
    }
    // Replace the parsed field with coerced/defaults-applied values
    (req as Record<string, unknown>)[target] = result.data;
    next();
  };

// Dependency wiring
const prisma = new PrismaClient();
const usersRepository = new UsersRepository(prisma);
const usersService = new UsersService(usersRepository);
const usersController = new UsersController(usersService);

const router = Router();

router.get(
  '/',
  validate(ListUsersQuerySchema, 'query'),
  (req, res, next) => usersController.list(req, res, next),
);

router.get(
  '/:id',
  validate(UserParamsSchema, 'params'),
  (req, res, next) => usersController.getById(req, res, next),
);

router.post(
  '/',
  validate(CreateUserSchema, 'body'),
  (req, res, next) => usersController.create(req, res, next),
);

export default router;
