# Chatbot Repository Template (Prisma-backed)

Prisma-backed repositories for `ChatSession` and `Message`, matching the schemas in `templates/chatbot-models.md`.

## src/repositories/chatSession.repository.ts

```typescript
import { PrismaClient, ChatSession as PrismaChatSession } from '@prisma/client';
import { ChatSession, ChatSessionCreate, ChatSessionUpdate } from '../schemas/chatSession.schema';

export class ChatSessionRepository {
  constructor(private readonly prisma: PrismaClient) {}

  /** Create a new chat session. */
  async create(data: ChatSessionCreate): Promise<ChatSession> {
    const row = await this.prisma.chatSession.create({ data });
    return this.toModel(row);
  }

  /** Get a session by ID, or null if it doesn't exist. */
  async getById(sessionId: string): Promise<ChatSession | null> {
    const row = await this.prisma.chatSession.findUnique({ where: { id: sessionId } });
    return row ? this.toModel(row) : null;
  }

  /** Get all sessions for a user, most recently updated first. */
  async getByUserId(userId: string, limit = 100): Promise<ChatSession[]> {
    const rows = await this.prisma.chatSession.findMany({
      where: { userId },
      take: limit,
      orderBy: { updatedAt: 'desc' },
    });
    return rows.map((row) => this.toModel(row));
  }

  /** Update a session (e.g. rename its title). */
  async update(sessionId: string, data: ChatSessionUpdate): Promise<ChatSession> {
    const row = await this.prisma.chatSession.update({ where: { id: sessionId }, data });
    return this.toModel(row);
  }

  /** Delete a session. Cascades to its messages via the Prisma relation. */
  async delete(sessionId: string): Promise<void> {
    await this.prisma.chatSession.delete({ where: { id: sessionId } });
  }

  private toModel(row: PrismaChatSession): ChatSession {
    return {
      sessionId: row.id,
      userId: row.userId,
      title: row.title ?? undefined,
      createdAt: row.createdAt.toISOString(),
      updatedAt: row.updatedAt.toISOString(),
    };
  }
}
```

## src/repositories/message.repository.ts

```typescript
import { PrismaClient, Message as PrismaMessage } from '@prisma/client';
import { Message, MessageCreate } from '../schemas/message.schema';

export class MessageRepository {
  constructor(private readonly prisma: PrismaClient) {}

  /** Create a new message within a session. */
  async create(data: MessageCreate): Promise<Message> {
    const row = await this.prisma.message.create({ data });
    return this.toModel(row);
  }

  /** Get all messages for a session, oldest first (chronological conversation order). */
  async getBySessionId(sessionId: string): Promise<Message[]> {
    const rows = await this.prisma.message.findMany({
      where: { sessionId },
      orderBy: { createdAt: 'asc' },
    });
    return rows.map((row) => this.toModel(row));
  }

  /** Get a single message by ID, or null if it doesn't exist. */
  async getById(messageId: string): Promise<Message | null> {
    const row = await this.prisma.message.findUnique({ where: { id: messageId } });
    return row ? this.toModel(row) : null;
  }

  private toModel(row: PrismaMessage): Message {
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

## Notes

- Both repositories accept a `PrismaClient` via constructor injection (not a global singleton import) so tests can pass a mock or a `Prisma.TransactionClient`.
- `toModel()` is `private` — repositories are the only layer that ever sees raw Prisma row shapes; everything above the repository works with the Zod-inferred domain types.
- Cascading delete for messages is declared once in `prisma/schema.prisma` (`onDelete: Cascade`) rather than implemented manually in the repository — let the database enforce referential integrity.
