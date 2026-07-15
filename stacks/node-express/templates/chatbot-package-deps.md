# Chatbot Package Dependencies Template

## package.json Dependencies for Chatbot with OpenAI

```json
{
  "dependencies": {
    "express": "^4.19.2",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "zod": "^3.23.8",
    "@prisma/client": "^5.19.1",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "pino": "^9.4.0",
    "pino-http": "^10.3.0",
    "openai": "^4.56.0"
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

Install with:
```bash
npm install express cors dotenv zod @prisma/client jsonwebtoken bcryptjs pino pino-http openai
npm install --save-dev typescript ts-node-dev @types/node @types/express @types/cors \
  @types/jsonwebtoken @types/bcryptjs jest ts-jest @types/jest supertest @types/supertest \
  eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier prisma
```

## Key Dependencies Explained

### Core Application
- **express**: Web framework
- **cors**: CORS middleware
- **zod**: Runtime request/response validation (this stack's equivalent of Pydantic)
- **dotenv**: Environment variable loading

### LLM Integration
- **openai**: Official OpenAI Node SDK for LLM integration

### Database
- **@prisma/client**: Generated, typed database client
- **prisma** (dev dependency): CLI for migrations and client generation

### Auth
- **jsonwebtoken**: JWT issuance/verification
- **bcryptjs**: Password hashing (pure-JS, no native build step — friendlier in course environments than `bcrypt`)

### Logging
- **pino** + **pino-http**: Structured, fast JSON logging with request correlation IDs

### Testing
- **jest** + **ts-jest**: Test runner with TypeScript support
- **supertest**: HTTP assertions against the Express app without binding a real port

### Code Quality
- **eslint** + **@typescript-eslint/***: Linting
- **prettier**: Formatting
- **typescript**: Compiler / `tsc --noEmit` for type checking

## Installation Commands

```bash
# Pin Node version
echo "20" > .nvmrc

# Install dependencies
npm install

# Or install a fresh clone reproducibly
npm ci
```

## Environment Variables

```bash
# .env.example
PORT=3000
NODE_ENV=development

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatbot_db

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# JWT
JWT_SECRET=change-in-production
JWT_EXPIRES_IN=30m

# CORS
ALLOWED_ORIGINS=http://localhost:5173
```

## Version Notes

- **openai**: Use v4+ for the current SDK shape (`client.chat.completions.create`)
- **express**: v4.19+ for current security patches (Express 5 is available but this stack targets the widely-deployed v4 line)
- **zod**: v3.23+ for `.transform()`/`.refine()` ergonomics used throughout this stack
- **prisma**: v5.19+ for stable `$transaction` and typed client generation

## Optional Dependencies

If you need additional features:

```bash
# Redis for caching (optional)
npm install ioredis

# BullMQ for background jobs (optional)
npm install bullmq

# Sentry for error tracking (optional)
npm install @sentry/node

# Rate limiting (optional)
npm install express-rate-limit

# WebSocket support (optional)
npm install ws
npm install --save-dev @types/ws
```

## Development Dependencies

```bash
# Development tools
npm install --save-dev nodemon        # Alternative to ts-node-dev
npm install --save-dev npm-run-all    # Compose multiple npm scripts
```

## Security Considerations

- Always use latest patch versions with security fixes
- Pin exact or caret-range versions consistently — never mix `^`, `~`, and bare versions in one package.json
- Regularly update dependencies (`npm outdated`, then `npm update`)
- Use `npm audit` to check for vulnerabilities

```bash
npm audit
npm audit fix
```
