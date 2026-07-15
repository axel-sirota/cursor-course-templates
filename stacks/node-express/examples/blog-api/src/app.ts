import express from 'express';
import cors from 'cors';
import { allowedOrigins } from './config/env';
import { requestLogger } from './middleware/requestLogger';
import { errorHandler } from './middleware/errorHandler';
import healthRouter from './routes/health';
import authRouter from './routes/auth';
import postsRouter from './routes/posts';

/**
 * Build the Express app without calling listen().
 * Keeping app.ts separate from server.ts lets Supertest import the app
 * directly in tests without binding a real port.
 */
function createApp() {
  const app = express();

  app.use(cors({ origin: allowedOrigins, credentials: true }));
  app.use(express.json());
  app.use(requestLogger);

  app.use('/', healthRouter);
  app.use('/api/auth', authRouter);
  app.use('/api/posts', postsRouter);

  // Error handler MUST be registered last
  app.use(errorHandler);

  return app;
}

const app = createApp();

export default app;
