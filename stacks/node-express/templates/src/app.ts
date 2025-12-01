import express from 'express';
import cors from 'cors';

const app = express();

app.use(cors());
app.use(express.json());

// Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

export default app;

