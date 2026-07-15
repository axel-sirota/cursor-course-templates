# Chatbot Service Template

`ChatService` orchestrates session/message persistence and LLM calls. It depends on the `LLMClient` interface (see `templates/llm-client.md`) rather than the OpenAI SDK directly, so it can be unit-tested with a mock client and swapped for a different provider without touching business logic.

## src/services/chat.service.ts

```typescript
import { ChatSessionRepository } from '../repositories/chatSession.repository';
import { MessageRepository } from '../repositories/message.repository';
import { LLMClient, ChatMessage } from '../config/llmClient';
import { ChatResponse } from '../schemas/chat.schema';
import { Message } from '../schemas/message.schema';
import { ChatSession } from '../schemas/chatSession.schema';
import { logger } from '../config/logger';

const SYSTEM_PROMPT =
  'You are a helpful AI assistant. Provide concise, helpful responses to user questions. ' +
  'Keep responses conversational and friendly.';

const MAX_HISTORY_MESSAGES = 20;

export class ChatService {
  constructor(
    private readonly sessionRepo: ChatSessionRepository,
    private readonly messageRepo: MessageRepository,
    private readonly llmClient: LLMClient
  ) {}

  /**
   * Start a brand-new conversation: creates a session (title derived from
   * the first message), sends the message to the LLM, and persists both
   * the user message and the assistant reply.
   */
  async startConversation(userId: string, message: string): Promise<ChatResponse> {
    const session = await this.sessionRepo.create({
      userId,
      title: message.slice(0, 50),
    });
    return this.exchangeMessage(session.sessionId, message, []);
  }

  /**
   * Continue an existing conversation, using its stored history as context
   * for the LLM call.
   *
   * @throws {Error} If the session does not exist (propagated from the repository/service caller).
   */
  async continueConversation(sessionId: string, message: string): Promise<ChatResponse> {
    const history = await this.messageRepo.getBySessionId(sessionId);
    return this.exchangeMessage(sessionId, message, history);
  }

  /** Get the full message history for a session, oldest first. */
  async getConversationHistory(sessionId: string): Promise<Message[]> {
    return this.messageRepo.getBySessionId(sessionId);
  }

  /** List all sessions belonging to a user, most recently updated first. */
  async listUserSessions(userId: string): Promise<ChatSession[]> {
    return this.sessionRepo.getByUserId(userId);
  }

  private async exchangeMessage(
    sessionId: string,
    userMessage: string,
    history: Message[]
  ): Promise<ChatResponse> {
    await this.messageRepo.create({ sessionId, role: 'user', content: userMessage });

    const messages = this.buildContext(userMessage, history);

    let assistantContent: string;
    try {
      const completion = await this.llmClient.chatCompletion(messages);
      assistantContent = completion.content;
    } catch (error) {
      logger.error({ err: error, sessionId }, 'LLM error during chat exchange');
      throw error;
    }

    const assistantMessage = await this.messageRepo.create({
      sessionId,
      role: 'assistant',
      content: assistantContent,
    });

    return {
      message: assistantContent,
      sessionId,
      messageId: assistantMessage.messageId,
    };
  }

  /** Cap history length sent to the LLM to control token usage/cost. */
  private buildContext(userMessage: string, history: Message[]): ChatMessage[] {
    const trimmedHistory = history.slice(-MAX_HISTORY_MESSAGES);
    return [
      { role: 'system', content: SYSTEM_PROMPT },
      ...trimmedHistory.map((m) => ({ role: m.role, content: m.content })),
      { role: 'user', content: userMessage },
    ];
  }
}
```

## Session Ownership Validation

Ownership checks belong in the controller (see `templates/chatbot-api.md`'s `assertSessionOwnership`) rather than the service, keeping the service free of HTTP-layer concerns (it throws domain errors, not `res.status()` calls). If a project wants ownership enforced closer to the data layer, add a `validateSessionOwnership` method to the service instead:

```typescript
async validateSessionOwnership(sessionId: string, userId: string): Promise<ChatSession> {
  const session = await this.sessionRepo.getById(sessionId);
  if (!session || session.userId !== userId) {
    throw new NotFoundError('Session not found');
  }
  return session;
}
```

## Testing the Service in Isolation

Because `ChatService` only depends on interfaces (`ChatSessionRepository`, `MessageRepository`, `LLMClient`) injected via its constructor, unit tests never touch a real database or the OpenAI API — see `templates/chatbot-tests.md` for the mocked unit test pattern.
