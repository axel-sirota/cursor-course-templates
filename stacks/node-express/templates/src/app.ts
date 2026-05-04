import express, { ErrorRequestHandler } from 'express';
import cors from 'cors';

const app = express();

app.use(cors());
app.use(express.json());

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Global error middleware — must be the last app.use
const errorHandler: ErrorRequestHandler = (err, req, res, next) => {
  const status = (err as { status?: number }).status ?? 500;
  res.status(status).json({
    error: err.message ?? 'Internal server error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  });
};

app.use(errorHandler);

export default app;
