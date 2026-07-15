import { Router } from 'express';
import { prisma } from '../config/prisma';
import { isDevelopment } from '../config/env';
import { asyncHandler } from '../middleware/asyncHandler';

const router = Router();

router.get(
  '/health',
  asyncHandler(async (_req, res) => {
    let databaseHealthy = false;
    try {
      await prisma.$queryRaw`SELECT 1`;
      databaseHealthy = true;
    } catch {
      databaseHealthy = false;
    }

    res.status(200).json({
      status: 'healthy',
      database: databaseHealthy,
      environment: isDevelopment ? 'development' : 'production',
    });
  })
);

export default router;
