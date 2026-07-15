# Express Project Boilerplate Guide

## Purpose

This guide provides step-by-step instructions for creating a complete Express + TypeScript project boilerplate with authentication, Prisma database integration, and a layered structure. After following this guide, you'll have a working API that starts with `npm run dev` and follows this stack's conventions (ESLint, Prettier, Jest, Supertest, Prisma, Zod).

## Quick Start Checklist

- [ ] Run `npm install` to install dependencies
- [ ] Copy .env.example to .env and configure
- [ ] Run `npx prisma migrate dev` to create the database schema
- [ ] Run `npm run dev`
- [ ] Test API at http://localhost:3000/health

## Project Structure

```
project_name/
├── .env.example
├── .env                    # Not in git
├── .gitignore
├── .nvmrc
├── package.json
├── package-lock.json
├── tsconfig.json
├── jest.config.ts
├── .eslintrc.json
├── .prettierrc
├── prisma/
│   └── schema.prisma
├── src/
│   ├── config/
│   │   ├── env.ts
│   │   ├── logger.ts
│   │   └── prisma.ts
│   ├── middleware/
│   │   ├── requestLogger.ts
│   │   ├── errorHandler.ts
│   │   └── auth.ts
│   ├── schemas/
│   │   └── auth.schema.ts
│   ├── routes/
│   │   ├── health.ts
│   │   └── auth.ts
│   ├── controllers/
│   │   └── auth.controller.ts
│   ├── services/
│   │   └── auth.service.ts
│   ├── repositories/
│   │   └── user.repository.ts
│   ├── errors/
│   │   └── index.ts
│   ├── app.ts
│   └── server.ts
└── tests/
    ├── setup.ts
    ├── routes/
    │   ├── health.test.ts
    │   └── auth.test.ts
    └── services/
        └── auth.service.test.ts
```

## Create Complete Project Structure

**Step-by-step file creation** (copy each file exactly as shown):

### 1. Create Directory Structure
```bash
mkdir my_project && cd my_project
mkdir -p src/config src/middleware src/schemas src/routes src/controllers src/services src/repositories src/errors
mkdir -p prisma tests/routes tests/services
```

### 2. Environment & Dependencies

Create each file with exact content:

**package.json**
```json
{
  "name": "my_project",
  "version": "1.0.0",
  "private": true,
  "main": "dist/server.js",
  "scripts": {
    "dev": "ts-node-dev --respawn --transpile-only src/server.ts",
    "build": "tsc -p tsconfig.json",
    "start": "node dist/server.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/ tests/",
    "lint:fix": "eslint src/ tests/ --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "prisma:generate": "prisma generate",
    "prisma:migrate": "prisma migrate dev"
  },
  "dependencies": {
    "express": "^4.19.2",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "zod": "^3.23.8",
    "@prisma/client": "^5.19.1",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "pino": "^9.4.0",
    "pino-http": "^10.3.0"
  },
  "devDependencies": {
    "typescript": "^5.5.4",
    "ts-node-dev": "^2.0.0",
    "@types/node": "^20.14.15",
    "@types/express": "^4.17.21",
    "@types/cors": "^2.8.17",
    "@types/jsonwebtoken": "^9.0.6",
    "@types/bcryptjs": "^2.4.6",
    "jest": "^29.7.0",
    "ts-jest": "^29.2.4",
    "@types/jest": "^29.5.12",
    "supertest": "^7.0.0",
    "@types/supertest": "^6.0.2",
    "eslint": "^8.57.0",
    "@typescript-eslint/parser": "^8.2.0",
    "@typescript-eslint/eslint-plugin": "^8.2.0",
    "prettier": "^3.3.3",
    "prisma": "^5.19.1"
  }
}
```

**.env.example**
```
# Server
PORT=3000
NODE_ENV=development

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8080

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/your_database

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRES_IN=30m
```

**.nvmrc**
```
20
```

**.gitignore**
```gitignore
# Dependencies
node_modules/

# Build output
dist/
build/
*.tsbuildinfo

# Environment
.env
.env.local
.env.test

# Testing
coverage/
.nyc_output/

# Logs
*.log
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Prisma
prisma/dev.db
```

### 3. TypeScript & Prisma Configuration

**tsconfig.json**
```json
{
  "compilerOptions": {
    "target": "ES2021",
    "lib": ["ES2021"],
    "module": "commonjs",
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": false,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

**prisma/schema.prisma**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id           String   @id @default(uuid())
  email        String   @unique
  passwordHash String
  fullName     String
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt

  @@map("users")
}
```

### 4. Core Configuration Files

**src/config/env.ts**
```typescript
import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const EnvSchema = z.object({
  PORT: z.coerce.number().default(3000),
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  DATABASE_URL: z.string().min(1, 'DATABASE_URL is required'),
  JWT_SECRET: z.string().min(1, 'JWT_SECRET is required'),
  JWT_EXPIRES_IN: z.string().default('30m'),
  ALLOWED_ORIGINS: z.string().default('http://localhost:5173'),
});

/**
 * Parsed, validated environment configuration.
 * Fails fast at startup if a required variable is missing or malformed.
 */
function loadEnv() {
  const parsed = EnvSchema.safeParse(process.env);
  if (!parsed.success) {
    // eslint-disable-next-line no-console
    console.error('Invalid environment configuration:', parsed.error.flatten().fieldErrors);
    process.exit(1);
  }
  return parsed.data;
}

export const env = loadEnv();

export const allowedOrigins = env.ALLOWED_ORIGINS.split(',').map((origin) => origin.trim());

export const isDevelopment = env.NODE_ENV === 'development';
export const isProduction = env.NODE_ENV === 'production';
export const isTest = env.NODE_ENV === 'test';
```

**src/config/logger.ts**
```typescript
import pino from 'pino';
import { isDevelopment } from './env';

/**
 * Structured logger. Pretty-printed in development, JSON in production
 * (JSON logs are what most log aggregators — Railway, Datadog, CloudWatch — expect).
 */
export const logger = pino({
  level: isDevelopment ? 'debug' : 'info',
  transport: isDevelopment
    ? { target: 'pino-pretty', options: { colorize: true, translateTime: 'HH:MM:ss' } }
    : undefined,
});
```

**src/config/prisma.ts**
```typescript
import { PrismaClient } from '@prisma/client';
import { isDevelopment } from './env';

/**
 * Singleton PrismaClient. Reused across the app to avoid exhausting
 * the database connection pool with a new client per request.
 */
export const prisma = new PrismaClient({
  log: isDevelopment ? ['query', 'warn', 'error'] : ['warn', 'error'],
});
```

### 5. Middleware & Error Types

**src/errors/index.ts**
```typescript
export class AppError extends Error {
  constructor(message: string, public readonly statusCode: number) {
    super(message);
    this.name = new.target.name;
  }
}

export class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 400);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 401);
  }
}

export class NotFoundError extends AppError {
  constructor(message = 'Resource not found') {
    super(message, 404);
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 409);
  }
}
```

**src/middleware/requestLogger.ts**
```typescript
import pinoHttp from 'pino-http';
import { randomUUID } from 'crypto';
import { logger } from '../config/logger';

/**
 * Request/response logging middleware with correlation IDs.
 * Equivalent to a FastAPI BaseHTTPMiddleware that stamps X-Correlation-ID.
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
```

**src/middleware/errorHandler.ts**
```typescript
import { ErrorRequestHandler } from 'express';
import { ZodError } from 'zod';
import { AppError } from '../errors';
import { logger } from '../config/logger';

/**
 * Centralized error-handling middleware. Register LAST, after all routes.
 * Maps known error types to HTTP status codes; logs and returns 500 for
 * anything unrecognized (never leaks internal error details to the client).
 */
export const errorHandler: ErrorRequestHandler = (err, req, res, _next) => {
  if (err instanceof ZodError) {
    res.status(400).json({ detail: err.issues.map((i) => i.message).join(', ') });
    return;
  }

  if (err instanceof AppError) {
    res.status(err.statusCode).json({ detail: err.message });
    return;
  }

  logger.error({ err, correlationId: req.id }, 'Unhandled error');
  res.status(500).json({ detail: 'Internal server error' });
};
```

**src/middleware/auth.ts**
```typescript
import { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import { env } from '../config/env';
import { UnauthorizedError } from '../errors';

export interface AuthenticatedUser {
  userId: string;
  email: string;
  permissions: string[];
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Express {
    interface Request {
      user?: AuthenticatedUser;
    }
  }
}

/**
 * Verifies the Bearer JWT and attaches the decoded user to req.user.
 * Equivalent to FastAPI's `Depends(require_auth)`.
 */
export function requireAuth(req: Request, _res: Response, next: NextFunction): void {
  const header = req.headers.authorization;
  if (!header?.startsWith('Bearer ')) {
    throw new UnauthorizedError('Missing or malformed Authorization header');
  }

  const token = header.slice('Bearer '.length);
  try {
    const decoded = jwt.verify(token, env.JWT_SECRET) as AuthenticatedUser;
    req.user = decoded;
    next();
  } catch {
    throw new UnauthorizedError('Invalid or expired token');
  }
}

/**
 * Permission-gated middleware factory, analogous to FastAPI's
 * `require_permission([Permission.READ])`.
 */
export function requirePermission(permission: string) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    if (!req.user?.permissions.includes(permission)) {
      throw new UnauthorizedError(`Missing required permission: ${permission}`);
    }
    next();
  };
}
```

### 6. Schemas

**src/schemas/auth.schema.ts**
```typescript
import { z } from 'zod';

export const RegisterRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  fullName: z.string().min(1),
});
export type RegisterRequest = z.infer<typeof RegisterRequestSchema>;

export const LoginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
});
export type LoginRequest = z.infer<typeof LoginRequestSchema>;

export const UserResponseSchema = z.object({
  userId: z.string(),
  email: z.string(),
  fullName: z.string(),
  permissions: z.array(z.string()),
});
export type UserResponse = z.infer<typeof UserResponseSchema>;
```

### 7. Repository, Service, Controller, Routes

**src/repositories/user.repository.ts**
```typescript
import { PrismaClient, User as PrismaUser } from '@prisma/client';

export interface User {
  userId: string;
  email: string;
  fullName: string;
  passwordHash: string;
}

export class UserRepository {
  constructor(private readonly prisma: PrismaClient) {}

  private toModel(row: PrismaUser): User {
    return {
      userId: row.id,
      email: row.email,
      fullName: row.fullName,
      passwordHash: row.passwordHash,
    };
  }

  async create(data: { email: string; passwordHash: string; fullName: string }): Promise<User> {
    const row = await this.prisma.user.create({ data });
    return this.toModel(row);
  }

  async findByEmail(email: string): Promise<User | null> {
    const row = await this.prisma.user.findUnique({ where: { email } });
    return row ? this.toModel(row) : null;
  }
}
```

**src/services/auth.service.ts**
```typescript
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { UserRepository, User } from '../repositories/user.repository';
import { env } from '../config/env';
import { ConflictError, UnauthorizedError } from '../errors';
import { logger } from '../config/logger';

export class AuthService {
  constructor(private readonly userRepo: UserRepository) {}

  /**
   * Register a new user, hashing the password with bcrypt before storage.
   * @throws {ConflictError} If the email is already registered.
   */
  async register(email: string, password: string, fullName: string): Promise<{ user: User; token: string }> {
    const existing = await this.userRepo.findByEmail(email);
    if (existing) {
      throw new ConflictError('User already registered');
    }

    const passwordHash = await bcrypt.hash(password, 10);
    const user = await this.userRepo.create({ email, passwordHash, fullName });
    logger.info({ userId: user.userId }, 'User registered');

    return { user, token: this.issueToken(user) };
  }

  /**
   * Authenticate a user by email/password.
   * @throws {UnauthorizedError} If credentials are invalid.
   */
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    const user = await this.userRepo.findByEmail(email);
    if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
      throw new UnauthorizedError('Invalid credentials');
    }
    logger.info({ userId: user.userId }, 'User logged in');
    return { user, token: this.issueToken(user) };
  }

  private issueToken(user: User): string {
    return jwt.sign(
      { userId: user.userId, email: user.email, permissions: ['read', 'write'] },
      env.JWT_SECRET,
      { expiresIn: env.JWT_EXPIRES_IN }
    );
  }
}
```

**src/controllers/auth.controller.ts**
```typescript
import { Request, Response } from 'express';
import { RegisterRequestSchema, LoginRequestSchema } from '../schemas/auth.schema';
import { AuthService } from '../services/auth.service';
import { UserRepository } from '../repositories/user.repository';
import { prisma } from '../config/prisma';

const authService = new AuthService(new UserRepository(prisma));

export async function register(req: Request, res: Response): Promise<void> {
  const parsed = RegisterRequestSchema.parse(req.body);
  const { user, token } = await authService.register(parsed.email, parsed.password, parsed.fullName);
  res.status(201).json({
    message: 'Registration successful',
    accessToken: token,
    user: { userId: user.userId, email: user.email, fullName: user.fullName },
  });
}

export async function login(req: Request, res: Response): Promise<void> {
  const parsed = LoginRequestSchema.parse(req.body);
  const { user, token } = await authService.login(parsed.email, parsed.password);
  res.status(200).json({
    message: 'Login successful',
    accessToken: token,
    user: { userId: user.userId, email: user.email, fullName: user.fullName },
  });
}

export async function me(req: Request, res: Response): Promise<void> {
  res.status(200).json({
    userId: req.user!.userId,
    email: req.user!.email,
    fullName: req.user!.email, // replace with a real lookup once profile fields grow
    permissions: req.user!.permissions,
  });
}

export async function logout(_req: Request, res: Response): Promise<void> {
  res.status(200).json({ message: 'Logged out successfully' });
}
```

**src/routes/health.ts**
```typescript
import { Router } from 'express';
import { prisma } from '../config/prisma';
import { isDevelopment } from '../config/env';

const router = Router();

router.get('/health', async (_req, res) => {
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
});

export default router;
```

**src/routes/auth.ts**
```typescript
import { Router } from 'express';
import { register, login, me, logout } from '../controllers/auth.controller';
import { requireAuth } from '../middleware/auth';

const router = Router();

router.post('/register', register);
router.post('/login', login);
router.get('/me', requireAuth, me);
router.post('/logout', logout);

export default router;
```

### 8. Main Application Files

**src/app.ts**
```typescript
import express from 'express';
import cors from 'cors';
import { allowedOrigins } from './config/env';
import { requestLogger } from './middleware/requestLogger';
import { errorHandler } from './middleware/errorHandler';
import healthRouter from './routes/health';
import authRouter from './routes/auth';

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

  // Error handler MUST be registered last
  app.use(errorHandler);

  return app;
}

const app = createApp();

export default app;
```

**src/server.ts** (entry point)
```typescript
import app from './app';
import { env } from './config/env';
import { logger } from './config/logger';

app.listen(env.PORT, () => {
  logger.info(`Server listening on port ${env.PORT}`);
});
```

### 9. Test Configuration

**jest.config.ts** — see `templates/test-scaffolding.md` for the full config plus `tests/setup.ts`.

### 10. Test Files

**tests/routes/health.test.ts**
```typescript
import request from 'supertest';
import app from '../../src/app';

describe('GET /health', () => {
  it('returns healthy status', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('healthy');
    expect(response.body).toHaveProperty('database');
    expect(response.body).toHaveProperty('environment');
  });
});
```

**tests/routes/auth.test.ts**
```typescript
import request from 'supertest';
import { randomUUID } from 'crypto';
import app from '../../src/app';

describe('Auth routes', () => {
  it('registers a new user', async () => {
    const response = await request(app).post('/api/auth/register').send({
      email: `test-${randomUUID()}@example.com`,
      password: 'testpassword',
      fullName: 'Test User',
    });
    expect(response.status).toBe(201);
    expect(response.body.message).toBe('Registration successful');
    expect(response.body).toHaveProperty('accessToken');
  });

  it('logs in a registered user', async () => {
    const email = `test-${randomUUID()}@example.com`;
    await request(app).post('/api/auth/register').send({ email, password: 'testpassword', fullName: 'Test User 2' });

    const response = await request(app).post('/api/auth/login').send({ email, password: 'testpassword' });
    expect(response.status).toBe(200);
    expect(response.body.message).toBe('Login successful');
  });

  it('rejects unauthenticated access to /me', async () => {
    const response = await request(app).get('/api/auth/me');
    expect(response.status).toBe(401);
  });
});
```

## Usage Instructions

### 1. Create Project and Install Dependencies
```bash
# Create project directory
mkdir my_project && cd my_project

# Pin Node version
echo "20" > .nvmrc

# Install dependencies
npm install
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

### 3. Set Up the Database
```bash
npx prisma migrate dev --name init
npx prisma generate
```

### 4. Run Application
```bash
# Start development server (hot reload)
npm run dev

# Or run tests
npm test
```

### 5. Test API
- Health check: `GET http://localhost:3000/health`
- Register user: `POST http://localhost:3000/api/auth/register`
- Login: `POST http://localhost:3000/api/auth/login`
- Access protected endpoint: `GET http://localhost:3000/api/auth/me`

## API Architecture Pattern

### Single API Surface (Simplified vs. the Python/FastAPI Dual-API Pattern)

The Python/FastAPI stack in this repo demonstrates a dual "Experience API" vs "Agent Tools API" split to teach service-to-service auth differences. This Node/Express stack keeps a **single API surface** under `src/routes/` for simplicity — all consumers (browser clients and any future automation) authenticate the same way via `requireAuth`.

If a course module later needs to demonstrate agent/service-to-service auth, mirror the FastAPI pattern by adding `src/routes/tools/` with its own auth middleware (e.g. an API-key check instead of JWT) and mounting it under a `/api/tools` prefix in `app.ts`. This is intentionally NOT scaffolded by default to keep Phase 0 skeletons simple.

## API Guidelines

### Request/Response Schemas
Zod schema field names are the wire format directly — no snake_case/camelCase translation layer exists in this stack (unlike Pydantic's `Field(alias=...)`):

```typescript
export const UserRequestSchema = z.object({
  fullName: z.string(),
  emailAddress: z.string().email(),
});
```

### Adding Protected Endpoints
```typescript
import { requireAuth, requirePermission } from '../middleware/auth';

router.get('/protected', requireAuth, requirePermission('read'), (req, res) => {
  res.json({ message: 'This is protected', userId: req.user!.userId });
});
```

### Error Handling
Throw a typed `AppError` subclass from the service layer; the centralized `errorHandler` middleware converts it to the right HTTP response:
```typescript
import { NotFoundError } from '../errors';

if (!resource) {
  throw new NotFoundError('Resource not found');
}
```

Controllers should be `async` functions with no internal `try/catch` for expected domain errors — wrap the Express app with an async-error-catching pattern (either Express 5's native async support, or `express-async-errors` for Express 4) so thrown errors reach `errorHandler` automatically.

## Code Quality & Error Prevention

### Development Tools Setup

**.eslintrc.json**
```json
{
  "root": true,
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "env": { "node": true, "es2021": true, "jest": true },
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": ["warn", { "allowExpressions": true }],
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

**.prettierrc**
```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
```

### Usage Commands

**Initial setup:**
```bash
npm install
```

**Manual quality checks (run when ready):**
```bash
npm run lint:fix      # ESLint, auto-fix
npm run format        # Prettier, write
npm run typecheck     # tsc --noEmit
npm test              # Jest
```

### IDE Integration

**VS Code settings.json:**
```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

### Quality Approach

**ESLint (all code):**
- Undefined variables and unused imports
- `no-explicit-any` enforcement
- Code style issues

**tsc --noEmit (all code):**
- Full static type checking — TypeScript checks the whole project by default, unlike mypy's opt-in "edge points only" approach in the Python stack. There's no equivalent scoping needed here.

### CI Integration Example

Add this to your CI pipeline:
```yaml
- name: Install dependencies
  run: npm ci

- name: Lint and type check
  run: |
    npm run lint
    npm run typecheck

- name: Run tests
  run: npm test -- --coverage
```

This setup ensures code quality from development through deployment.

## Next Steps

After creating the boilerplate:

1. **Configure Database**: Update .env with your database credentials
2. **Add Modules**: Create new route/controller/service/repository sets following the layered pattern
3. **Prisma Models**: Add models to prisma/schema.prisma and run migrations
4. **Production Setup**: Configure deployment settings (see rules/500-docker-node.mdc)

## Troubleshooting

**"Cannot find module" errors**: Run `npm run build` or check `tsconfig.json` `rootDir`/`outDir` paths
**Database connection fails**: Check `DATABASE_URL` in .env and that `docker compose up -d postgres` succeeded
**CORS errors**: Add your frontend URL to `ALLOWED_ORIGINS` in .env
**Prisma Client out of sync**: Run `npx prisma generate` after any schema.prisma change
