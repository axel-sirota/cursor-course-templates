# Chatbot Domain Guide

## Purpose

This guide provides domain-specific patterns for building a chatbot API with Express and OpenAI integration. This guide focuses on conversation management, message handling, and LLM integration patterns.

## Domain Overview

### Core Entities

**Chat Session**
- Represents a conversation between a user and the chatbot
- Contains metadata about the conversation (userId, title, createdAt, updatedAt)
- Persists across multiple messages

**Message**
- Individual user or assistant message within a chat session
- Contains content, role (user/assistant), and timestamp
- Links to a chat session

**Conversation Flow**
```
User → API → LLM (OpenAI) → Response → API → User
```

### Basic Workflows

1. **Start Conversation**: Create a new chat session
2. **Send Message**: User sends message, system gets LLM response
3. **Continue Conversation**: Add to existing chat session
4. **List Conversations**: Retrieve user's chat history
5. **View Messages**: Get messages for a specific conversation

## Data Modeling

### Layered Zod Schemas

Follow the layered schema architecture used throughout this stack. Zod's `.extend()` / `.omit()` / `.partial()` give the same composability FastAPI gets from Pydantic base-class inheritance — and because TypeScript/JSON/Zod all share camelCase natively, there is no snake_case↔camelCase aliasing step to write.

**ChatSession Schemas**
- `ChatSessionBaseSchema`: Business fields (userId, title)
- `ChatSessionSchema`: Full schema with sessionId, timestamps
- `ChatSessionCreateSchema`: For creation
- `ChatSessionUpdateSchema`: For updates (`.partial()`)

**Message Schemas**
- `MessageBaseSchema`: Business fields (sessionId, role, content)
- `MessageSchema`: Full schema with messageId, timestamp
- `MessageCreateSchema`: For creation

### API Schemas (all camelCase — no aliasing layer needed)

**Request Schemas**
```typescript
// src/schemas/chat.schema.ts
import { z } from 'zod';

export const ChatRequestSchema = z.object({
  message: z.string().min(1).max(10000),
  sessionId: z.string().optional(),
});
export type ChatRequest = z.infer<typeof ChatRequestSchema>;
```

**Response Schemas**
```typescript
export const ChatResponseSchema = z.object({
  message: z.string(),
  sessionId: z.string(),
  messageId: z.string(),
});
export type ChatResponse = z.infer<typeof ChatResponseSchema>;

export const SessionResponseSchema = z.object({
  sessionId: z.string(),
  title: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});
export type SessionResponse = z.infer<typeof SessionResponseSchema>;
```

## Repository Patterns

### ChatSession Repository

```typescript
// src/repositories/chatSession.repository.ts
import { PrismaClient } from '@prisma/client';
import { ChatSession, ChatSessionCreate, ChatSessionUpdate } from '../schemas/chatSession.schema';

export class ChatSessionRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async create(data: ChatSessionCreate): Promise<ChatSession> {
    const row = await this.prisma.chatSession.create({ data });
    return this.toModel(row);
  }

  async getById(sessionId: string): Promise<ChatSession | null> {
    const row = await this.prisma.chatSession.findUnique({ where: { id: sessionId } });
    return row ? this.toModel(row) : null;
  }

  async getByUserId(userId: string, limit = 100): Promise<ChatSession[]> {
    const rows = await this.prisma.chatSession.findMany({
      where: { userId },
      take: limit,
      orderBy: { updatedAt: 'desc' },
    });
    return rows.map((row) => this.toModel(row));
  }

  async update(sessionId: string, data: ChatSessionUpdate): Promise<ChatSession> {
    const row = await this.prisma.chatSession.update({ where: { id: sessionId }, data });
    return this.toModel(row);
  }

  async delete(sessionId: string): Promise<void> {
    await this.prisma.chatSession.delete({ where: { id: sessionId } });
  }

  private toModel(row: {
    id: string;
    userId: string;
    title: string;
    createdAt: Date;
    updatedAt: Date;
  }): ChatSession {
    return {
      sessionId: row.id,
      userId: row.userId,
      title: row.title,
      createdAt: row.createdAt.toISOString(),
      updatedAt: row.updatedAt.toISOString(),
    };
  }
}
```

### Message Repository

```typescript
// src/repositories/message.repository.ts
import { PrismaClient } from '@prisma/client';
import { Message, MessageCreate } from '../schemas/message.schema';

export class MessageRepository {
  constructor(private readonly prisma: PrismaClient) {}

  async create(data: MessageCreate): Promise<Message> {
    const row = await this.prisma.message.create({ data });
    return this.toModel(row);
  }

  async getBySessionId(sessionId: string): Promise<Message[]> {
    const rows = await this.prisma.message.findMany({
      where: { sessionId },
      orderBy: { createdAt: 'asc' },
    });
    return rows.map((row) => this.toModel(row));
  }

  private toModel(row: {
    id: string;
    sessionId: string;
    role: string;
    content: string;
    createdAt: Date;
  }): Message {
    return {
      messageId: row.id,
      sessionId: row.sessionId,
      role: row.role as 'user' | 'assistant',
      content: row.content,
      createdAt: row.createdAt.toISOString(),
    };
  }
}
```

## Service Layer Patterns

### Chat Service

The service layer orchestrates chat operations and LLM integration:

```typescript
// src/services/chat.service.ts
import { ChatSessionRepository } from '../repositories/chatSession.repository';
import { MessageRepository } from '../repositories/message.repository';
import { LLMClient } from '../config/llmClient';
import { ChatResponse } from '../schemas/chat.schema';
import { logger } from '../config/logger';

const SYSTEM_PROMPT =
  'You are a helpful AI assistant. Provide concise, helpful responses to user questions. ' +
  'Keep responses conversational and friendly.';

export class ChatService {
  constructor(
    private readonly sessionRepo: ChatSessionRepository,
    private readonly messageRepo: MessageRepository,
    private readonly llmClient: LLMClient
  ) {}

  /** Start a new conversation: create a session, get the first LLM reply, persist both messages. */
  async startConversation(userId: string, message: string): Promise<ChatResponse> {
    const session = await this.sessionRepo.create({ userId, title: message.slice(0, 50) });
    return this.exchangeMessage(session.sessionId, message, []);
  }

  /** Continue an existing conversation using stored history as LLM context. */
  async continueConversation(sessionId: string, message: string): Promise<ChatResponse> {
    const history = await this.messageRepo.getBySessionId(sessionId);
    return this.exchangeMessage(sessionId, message, history);
  }

  async getConversationHistory(sessionId: string) {
    return this.messageRepo.getBySessionId(sessionId);
  }

  async listUserSessions(userId: string) {
    return this.sessionRepo.getByUserId(userId);
  }

  private async exchangeMessage(
    sessionId: string,
    userMessage: string,
    history: Array<{ role: string; content: string }>
  ): Promise<ChatResponse> {
    await this.messageRepo.create({ sessionId, role: 'user', content: userMessage });

    const messages = [
      { role: 'system' as const, content: SYSTEM_PROMPT },
      ...history.map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content })),
      { role: 'user' as const, content: userMessage },
    ];

    let assistantContent: string;
    try {
      const completion = await this.llmClient.chatCompletion(messages);
      assistantContent = completion.content;
    } catch (error) {
      logger.error({ err: error }, 'LLM error');
      throw error;
    }

    const assistantMessage = await this.messageRepo.create({
      sessionId,
      role: 'assistant',
      content: assistantContent,
    });

    return { message: assistantContent, sessionId, messageId: assistantMessage.messageId };
  }
}
```

## API Endpoints

### Experience APIs (for users)

**POST /api/chat**
- Start new conversation or continue existing
- Request: `ChatRequestSchema`
- Response: `ChatResponseSchema`

**GET /api/chat/sessions**
- List user's chat sessions
- Response: `SessionResponseSchema[]`

**GET /api/chat/sessions/:sessionId/messages**
- Get messages for a session
- Response: `MessageResponseSchema[]`

**PATCH /api/chat/sessions/:sessionId**
- Update session title
- Request: `{ "title": "..." }`
- Response: `SessionResponseSchema`

**DELETE /api/chat/sessions/:sessionId**
- Delete a session
- Response: `{ "success": true }`

## Testing Strategy

### E2E Tests

Test the complete flow with Supertest:
```typescript
it('starts a new conversation', async () => {
  const response = await request(app)
    .post('/api/chat')
    .set(authHeaders)
    .send({ message: 'Hello, who are you?' });

  expect(response.status).toBe(200);
  expect(response.body).toHaveProperty('message');
  expect(response.body).toHaveProperty('sessionId');
  expect(response.body).toHaveProperty('messageId');
});

it('continues an existing conversation', async () => {
  const start = await request(app).post('/api/chat').set(authHeaders).send({ message: 'Hello' });
  const sessionId = start.body.sessionId;

  const cont = await request(app)
    .post('/api/chat')
    .set(authHeaders)
    .send({ message: "What's my name?", sessionId });

  expect(cont.status).toBe(200);
  expect(cont.body.sessionId).toBe(sessionId);
});
```

### Unit Tests with Mocked LLM

Mock the LLM client for fast, deterministic unit tests:
```typescript
jest.mock('../../src/config/llmClient');

it('gets an LLM response', async () => {
  const mockClient = { chatCompletion: jest.fn().mockResolvedValue({ content: 'Mocked response' }) };
  const service = new ChatService(sessionRepo, messageRepo, mockClient as never);

  const result = await service.startConversation('user-1', 'Hello');

  expect(result.message).toBe('Mocked response');
  expect(mockClient.chatCompletion).toHaveBeenCalledTimes(1);
});
```

## OpenAI Integration

### Client Setup

See `templates/llm-client.md` for the full `LLMClient` interface with a Mock and OpenAI implementation.

### Prompt Engineering

**System Prompt**
```typescript
const SYSTEM_PROMPT = `You are a helpful AI assistant.
Provide concise, helpful responses to user questions.
Keep responses conversational and friendly.`;
```

**Context Management**
```typescript
function prepareMessages(userMessage: string, history: Message[]): ChatMessage[] {
  return [
    { role: 'system', content: SYSTEM_PROMPT },
    ...history.map((m) => ({ role: m.role, content: m.content })),
    { role: 'user', content: userMessage },
  ];
}
```

## Error Handling

### LLM Errors

```typescript
try {
  const response = await llmClient.chatCompletion(messages);
} catch (error) {
  logger.error({ err: error }, 'OpenAI error');
  throw new AppError('AI service unavailable', 503);
}
```

## Performance Considerations

### Token Management

Track token usage for cost management:
- Estimate tokens before sending
- Set token limits per conversation
- Cache responses when appropriate

### Rate Limiting

Implement rate limiting for LLM calls (e.g. `express-rate-limit`):
- Per-user rate limits
- Per-session limits
- Exponential backoff on errors

## Security Considerations

### Input Validation

Validate and sanitize user input with Zod:
```typescript
export const ChatRequestSchema = z.object({
  message: z.string().min(1).max(10000).transform((v) => v.trim()),
  sessionId: z.string().optional(),
});
```

### User Isolation

Ensure conversations are properly isolated:
- Always validate session ownership before returning history
- Never expose other users' conversations
- Use Prisma's parameterized queries (never string-interpolated raw SQL)

## Example Endpoint Implementation

```typescript
// src/controllers/chat.controller.ts
import { Request, Response } from 'express';
import { ChatRequestSchema } from '../schemas/chat.schema';
import { chatService } from './deps';

export async function chat(req: Request, res: Response): Promise<void> {
  const parsed = ChatRequestSchema.parse(req.body);
  const userId = req.user!.userId;

  const response = parsed.sessionId
    ? await chatService.continueConversation(parsed.sessionId, parsed.message)
    : await chatService.startConversation(userId, parsed.message);

  res.status(200).json(response);
}
```

## Database Schema (Prisma)

```prisma
model ChatSession {
  id        String   @id @default(uuid())
  userId    String
  title     String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  messages  Message[]

  @@index([userId])
  @@map("chat_sessions")
}

model Message {
  id        String      @id @default(uuid())
  sessionId String
  session   ChatSession @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  role      String      // 'user' or 'assistant'
  content   String
  createdAt DateTime    @default(now())

  @@index([sessionId])
  @@map("messages")
}
```

## Next Steps

1. Create Zod schemas following layered architecture
2. Implement repositories for chat sessions and messages
3. Create chat service with LLM integration
4. Build API endpoints with proper error handling
5. Add comprehensive E2E tests
6. Implement rate limiting and security measures

## Anti-Patterns to Avoid

❌ **Don't store LLM responses in untyped fields**
✅ **Use Zod-validated schemas end to end**

❌ **Don't send full conversation history on every request without limits**
✅ **Cache conversation context efficiently, cap history length**

❌ **Don't expose internal LLM errors to users**
✅ **Return user-friendly error messages via the centralized error handler**

❌ **Don't skip input validation**
✅ **Validate and sanitize all user input with Zod**

❌ **Don't call the OpenAI SDK directly from controllers**
✅ **Route all LLM calls through the `LLMClient` interface in the service layer**
