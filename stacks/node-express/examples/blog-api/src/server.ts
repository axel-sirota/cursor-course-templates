import app from './app';
import { env } from './config/env';
import { logger } from './config/logger';

app.listen(env.PORT, () => {
  logger.info(`Blog API listening on port ${env.PORT}`);
});
