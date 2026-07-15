# Chatbot Models Template (Zod Schemas + Prisma Models)

Layered Zod schemas and the matching Prisma models for the chatbot domain. Since TypeScript, JSON, and Zod all use camelCase natively, there is no snake_case↔camelCase aliasing to write here (unlike Pydantic's `Field(alias=...)` pattern) — the schema field names ARE the wire format ARE the TypeScript types.

## src/schemas/chatSession.schema.ts

```typescript
import { z } from 'zod';

// Base: business fields only
export const ChatSessionBaseSchema = z.object({
  userId: z.string(),
  title: z.string().max(255).optional(),
});

// Full: includes generated/database fields
export const ChatSessionSchema = ChatSessionBaseSchema.extend({
  sessionId: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
});

// Create: same shape as base
export const ChatSessionCreateSchema = ChatSessionBaseSchema;

// Update: all fields optional
export const ChatSessionUpdateSchema = ChatSessionBaseSchema.partial();

export type ChatSession = z.infer<typeof ChatSessionSchema>;
export type ChatSessionCreate = z.infer<typeof ChatSessionCreateSchema>;
export type ChatSessionUpdate = z.infer<typeof ChatSessionUpdateSchema>;
```

## src/schemas/message.schema.ts

```typescript
import { z } from 'zod';

export const MessageRoleSchema = z.enum(['user', 'assistant']);

export const MessageBaseSchema = z.object({
  sessionId: z.string(),
  role: MessageRoleSchema,
  content: z.string().min(1).max(10000),
});

export const MessageSchema = MessageBaseSchema.extend({
  messageId: z.string(),
  createdAt: z.string(),
});

export const MessageCreateSchema = MessageBaseSchema;

export type Message = z.infer<typeof MessageSchema>;
export type MessageCreate = z.infer<typeof MessageCreateSchema>;
```

## src/schemas/chat.schema.ts

API request/response schemas (distinct from the domain schemas above — these shape what crosses the wire):

```typescript
import { z } from 'zod';

export const ChatRequestSchema = z.object({
  message: z.string().min(1).max(10000),
  sessionId: z.string().optional(),
});
export type ChatRequest = z.infer<typeof ChatRequestSchema>;

export const ChatResponseSchema = z.object({
  message: z.string(),
  sessionId: z.string(),
  messageId: z.string(),
});
export type ChatResponse = z.infer<typeof ChatResponseSchema>;

export const SessionResponseSchema = z.object({
  sessionId: z.string(),
  title: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
});
export type SessionResponse = z.infer<typeof SessionResponseSchema>;

export const MessageResponseSchema = z.object({
  messageId: z.string(),
  sessionId: z.string(),
  role: z.enum(['user', 'assistant']),
  content: z.string(),
  createdAt: z.string(),
});
export type MessageResponse = z.infer<typeof MessageResponseSchema>;
```

## prisma/schema.prisma (excerpt)

```prisma
model ChatSession {
  id        String    @id @default(uuid())
  userId    String
  title     String?
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
  messages  Message[]

  @@index([userId])
  @@map("chat_sessions")
}

model Message {
  id        String      @id @default(uuid())
  sessionId String
  session   ChatSession @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  role      String      // 'user' | 'assistant' — kept as String in Prisma, narrowed by Zod at the API boundary
  content   String
  createdAt DateTime    @default(now())

  @@index([sessionId])
  @@map("messages")
}
```

## Why Zod `.extend()` Replaces Pydantic Inheritance

FastAPI's layered model pattern uses Python class inheritance:
```python
class ChatSessionBase(BaseModel): ...
class ChatSession(ChatSessionBase): ...       # adds id, timestamps
class ChatSessionCreate(ChatSessionBase): ... # same fields as base
class ChatSessionUpdate(BaseModel): ...       # all fields Optional
```

Zod achieves the same layering with composition instead of inheritance, which is idiomatic in a structurally-typed language:
```typescript
const Base = z.object({ /* ... */ });
const Full = Base.extend({ id: z.string(), createdAt: z.string() });
const Create = Base;                 // identical shape, separate name for intent
const Update = Base.partial();       // every field becomes optional
```

Both approaches produce the same four schema variants per entity — Base / Full / Create / Update — the composition style just fits TypeScript's structural type system better than mimicking class inheritance would.
