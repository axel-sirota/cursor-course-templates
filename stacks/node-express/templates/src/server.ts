import app from './app';
import dotenv from 'dotenv';
import pino from 'pino';

dotenv.config();

const logger = pino();

const PORT = process.env.PORT ?? 3000;

app.listen(PORT, () => {
  logger.info({ port: PORT }, 'Server started');
});
