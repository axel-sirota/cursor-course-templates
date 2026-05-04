# Node.js Express Starter Template

Use these patterns when scaffolding the Phase 0 Skeleton.

## Configuration

### package.json
```json
{
  "scripts": {
    "build": "tsc",
    "dev": "ts-node-dev --respawn src/server.ts",
    "start": "node dist/server.js",
    "test": "jest --testPathPattern='.*\\.test\\.ts$'",
    "test:integration": "jest --testPathPattern='.*\\.integration\\.test\\.ts$'",
    "lint": "eslint src --ext .ts",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "express": "^4.21.0",
    "pino": "^9.0.0",
    "zod": "^3.23.0",
    "@prisma/client": "^5.0.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/express": "^5.0.0",
    "jest": "^29.0.0",
    "ts-jest": "^29.0.0",
    "supertest": "^7.0.0",
    "@types/supertest": "^6.0.0",
    "eslint": "^9.0.0",
    "prisma": "^5.0.0",
    "ts-node-dev": "^2.0.0"
  }
}
```

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "es2020",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "resolveJsonModule": true,
    "declaration": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "**/*.test.ts"]
}
```

## Entry Point

### src/server.ts
```typescript
import app from './app';
import dotenv from 'dotenv';
import pino from 'pino';

dotenv.config();

const logger = pino();

const PORT = process.env.PORT ?? 3000;

app.listen(PORT, () => {
  logger.info({ port: PORT }, 'Server started');
});
```

### src/app.ts
```typescript
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
```

## Zod Validation Middleware Pattern

```typescript
import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';

export const validate =
  (schema: ZodSchema) =>
  (req: Request, res: Response, next: NextFunction): void => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (err) {
      if (err instanceof ZodError) {
        res.status(400).json({ error: 'Validation failed', issues: err.issues });
        return;
      }
      next(err);
    }
  };
```
