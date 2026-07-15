# Chatbot API Template

Express routes and controllers for the chatbot domain. Pair with `templates/chatbot-models.md` (schemas), `templates/chatbot-repository.md`, and `templates/chatbot-service.md`.

## src/routes/chat.ts

```typescript
import { Router } from 'express';
import { requireAuth } from '../middleware/auth';
import {
  chat,
  listSessions,
  getSessionMessages,
  updateSession,
  deleteSession,
} from '../controllers/chat.controller';

const router = Router();

router.post('/chat', requireAuth, chat);
router.get('/chat/sessions', requireAuth, listSessions);
router.get('/chat/sessions/:sessionId/messages', requireAuth, getSessionMessages);
router.patch('/chat/sessions/:sessionId', requireAuth, updateSession);
router.delete('/chat/sessions/:sessionId', requireAuth, deleteSession);

export default router;
```

## src/controllers/chat.controller.ts

```typescript
import { Request, Response } from 'express';
import { ChatRequestSchema } from '../schemas/chat.schema';
import { NotFoundError, UnauthorizedError } from '../errors';
import { chatService, sessionRepo } from './deps';

/**
 * POST /api/chat
 * Start a new conversation (no sessionId) or continue an existing one.
 */
export async function chat(req: Request, res: Response): Promise<void> {
  const parsed = ChatRequestSchema.parse(req.body);
  const userId = req.user!.userId;

  const response = parsed.sessionId
    ? await chatService.continueConversation(parsed.sessionId, parsed.message)
    : await chatService.startConversation(userId, parsed.message);

  res.status(200).json(response);
}

/**
 * GET /api/chat/sessions
 * List all chat sessions belonging to the authenticated user.
 */
export async function listSessions(req: Request, res: Response): Promise<void> {
  const sessions = await chatService.listUserSessions(req.user!.userId);
  res.status(200).json(sessions);
}

/**
 * GET /api/chat/sessions/:sessionId/messages
 * Get the full message history for a session (owner-only).
 */
export async function getSessionMessages(req: Request, res: Response): Promise<void> {
  const { sessionId } = req.params;
  await assertSessionOwnership(sessionId, req.user!.userId);

  const messages = await chatService.getConversationHistory(sessionId);
  res.status(200).json(messages);
}

/**
 * PATCH /api/chat/sessions/:sessionId
 * Update a session's title.
 */
export async function updateSession(req: Request, res: Response): Promise<void> {
  const { sessionId } = req.params;
  await assertSessionOwnership(sessionId, req.user!.userId);

  const { title } = req.body as { title: string };
  const updated = await sessionRepo.update(sessionId, { title });
  res.status(200).json(updated);
}

/**
 * DELETE /api/chat/sessions/:sessionId
 * Delete a session and its messages (cascade via Prisma relation).
 */
export async function deleteSession(req: Request, res: Response): Promise<void> {
  const { sessionId } = req.params;
  await assertSessionOwnership(sessionId, req.user!.userId);

  await sessionRepo.delete(sessionId);
  res.status(200).json({ success: true });
}

async function assertSessionOwnership(sessionId: string, userId: string): Promise<void> {
  const session = await sessionRepo.getById(sessionId);
  if (!session) {
    throw new NotFoundError('Session not found');
  }
  if (session.userId !== userId) {
    throw new UnauthorizedError('Session does not belong to you');
  }
}
```

## src/controllers/deps.ts

Manual dependency wiring (no DI container needed at this scale):

```typescript
import { prisma } from '../config/prisma';
import { ChatSessionRepository } from '../repositories/chatSession.repository';
import { MessageRepository } from '../repositories/message.repository';
import { ChatService } from '../services/chat.service';
import { openAIClient } from '../config/llmClient';

export const sessionRepo = new ChatSessionRepository(prisma);
export const messageRepo = new MessageRepository(prisma);
export const chatService = new ChatService(sessionRepo, messageRepo, openAIClient);
```

## Mounting in src/app.ts

```typescript
import chatRouter from './routes/chat';
// ...
app.use('/api', chatRouter);
```

## Example Requests

**Start a conversation:**
```http
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{ "message": "Hello, who are you?" }
```

**Continue a conversation:**
```http
POST /api/chat
Authorization: Bearer <token>
Content-Type: application/json

{ "message": "What's my name?", "sessionId": "abc-123" }
```

**List sessions:**
```http
GET /api/chat/sessions
Authorization: Bearer <token>
```
