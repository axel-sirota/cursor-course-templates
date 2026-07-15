import pinoHttp from 'pino-http';
import { randomUUID } from 'crypto';
import { logger } from '../config/logger';

/**
 * Request/response logging middleware with correlation IDs.
 */
export const requestLogger = pinoHttp({
  logger,
  genReqId: (req, res) => {
    const existing = req.headers['x-correlation-id'];
    const correlationId = typeof existing === 'string' ? existing : randomUUID();
    res.setHeader('X-Correlation-ID', correlationId);
    return correlationId;
  },
});
