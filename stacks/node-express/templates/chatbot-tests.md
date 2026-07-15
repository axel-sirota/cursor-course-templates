# Chatbot Tests Template (Supertest + Jest)

E2E and unit tests for the chatbot domain, following this stack's TDD conventions from `rules/400-testing-first.mdc`.

## tests/routes/chat.test.ts (E2E, Supertest)

```typescript
import request from 'supertest';
import app from '../../src/app';
import { getAuthHeaders } from '../setup';

describe('Chat routes', () => {
  it('starts a new conversation', async () => {
    const headers = await getAuthHeaders();

    const response = await request(app)
      .post('/api/chat')
      .set(headers)
      .send({ message: 'Hello, who are you?' });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('message');
    expect(response.body).toHaveProperty('sessionId');
    expect(response.body).toHaveProperty('messageId');
  });

  it('continues an existing conversation using the same sessionId', async () => {
    const headers = await getAuthHeaders();

    const start = await request(app).post('/api/chat').set(headers).send({ message: 'Hello' });
    const sessionId = start.body.sessionId;

    const cont = await request(app)
      .post('/api/chat')
      .set(headers)
      .send({ message: "What's my name?", sessionId });

    expect(cont.status).toBe(200);
    expect(cont.body.sessionId).toBe(sessionId);
  });

  it('rejects an empty message', async () => {
    const headers = await getAuthHeaders();

    const response = await request(app).post('/api/chat').set(headers).send({ message: '' });

    expect(response.status).toBe(400);
  });

  it('requires authentication', async () => {
    const response = await request(app).post('/api/chat').send({ message: 'Hello' });
    expect(response.status).toBe(401);
  });

  it('lists sessions for the authenticated user', async () => {
    const headers = await getAuthHeaders();
    await request(app).post('/api/chat').set(headers).send({ message: 'First session' });

    const response = await request(app).get('/api/chat/sessions').set(headers);

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body.length).toBeGreaterThanOrEqual(1);
  });

  it('retrieves message history for a session', async () => {
    const headers = await getAuthHeaders();
    const start = await request(app).post('/api/chat').set(headers).send({ message: 'Hello' });
    const sessionId = start.body.sessionId;

    const response = await request(app).get(`/api/chat/sessions/${sessionId}/messages`).set(headers);

    expect(response.status).toBe(200);
    expect(response.body).toHaveLength(2); // user message + assistant reply
    expect(response.body[0].role).toBe('user');
    expect(response.body[1].role).toBe('assistant');
  });

  it('returns 404 for a session that does not belong to the caller', async () => {
    const ownerHeaders = await getAuthHeaders();
    const otherHeaders = await getAuthHeaders();

    const start = await request(app).post('/api/chat').set(ownerHeaders).send({ message: 'Private' });
    const sessionId = start.body.sessionId;

    const response = await request(app)
      .get(`/api/chat/sessions/${sessionId}/messages`)
      .set(otherHeaders);

    expect(response.status).toBe(404);
  });

  it('deletes a session', async () => {
    const headers = await getAuthHeaders();
    const start = await request(app).post('/api/chat').set(headers).send({ message: 'Delete me' });
    const sessionId = start.body.sessionId;

    const del = await request(app).delete(`/api/chat/sessions/${sessionId}`).set(headers);
    expect(del.status).toBe(200);
    expect(del.body.success).toBe(true);

    const getAfter = await request(app).get(`/api/chat/sessions/${sessionId}/messages`).set(headers);
    expect(getAfter.status).toBe(404);
  });
});
```

Note: in E2E tests, the real `LLMClient` implementation should be swapped for the `MockLLMClient` (see `templates/llm-client.md`) via an environment flag (e.g. `LLM_PROVIDER=mock` in `.env.test`), so the test suite never makes real network calls to OpenAI and stays fast/deterministic.

## tests/services/chat.service.test.ts (Unit, mocked dependencies)

```typescript
import { ChatService } from '../../src/services/chat.service';
import { ChatSessionRepository } from '../../src/repositories/chatSession.repository';
import { MessageRepository } from '../../src/repositories/message.repository';
import { LLMClient } from '../../src/config/llmClient';

describe('ChatService', () => {
  let sessionRepo: jest.Mocked<ChatSessionRepository>;
  let messageRepo: jest.Mocked<MessageRepository>;
  let llmClient: jest.Mocked<LLMClient>;
  let service: ChatService;

  beforeEach(() => {
    sessionRepo = { create: jest.fn(), getById: jest.fn(), getByUserId: jest.fn() } as never;
    messageRepo = { create: jest.fn(), getBySessionId: jest.fn() } as never;
    llmClient = { chatCompletion: jest.fn() } as never;
    service = new ChatService(sessionRepo, messageRepo, llmClient);
  });

  it('starts a conversation and persists both messages', async () => {
    sessionRepo.create.mockResolvedValue({
      sessionId: 'session-1',
      userId: 'user-1',
      title: 'Hello',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    });
    messageRepo.create
      .mockResolvedValueOnce({
        messageId: 'msg-user-1',
        sessionId: 'session-1',
        role: 'user',
        content: 'Hello',
        createdAt: '2024-01-01T00:00:00Z',
      })
      .mockResolvedValueOnce({
        messageId: 'msg-assistant-1',
        sessionId: 'session-1',
        role: 'assistant',
        content: 'Hi there!',
        createdAt: '2024-01-01T00:00:01Z',
      });
    llmClient.chatCompletion.mockResolvedValue({ content: 'Hi there!', model: 'mock', usage: { totalTokens: 10 } });

    const result = await service.startConversation('user-1', 'Hello');

    expect(result.message).toBe('Hi there!');
    expect(result.sessionId).toBe('session-1');
    expect(messageRepo.create).toHaveBeenCalledTimes(2);
    expect(llmClient.chatCompletion).toHaveBeenCalledTimes(1);
  });

  it('propagates LLM errors without persisting an assistant message', async () => {
    messageRepo.create.mockResolvedValueOnce({
      messageId: 'msg-user-1',
      sessionId: 'session-1',
      role: 'user',
      content: 'Hello',
      createdAt: '2024-01-01T00:00:00Z',
    });
    llmClient.chatCompletion.mockRejectedValue(new Error('OpenAI unavailable'));

    await expect(service.continueConversation('session-1', 'Hello')).rejects.toThrow('OpenAI unavailable');
    expect(messageRepo.create).toHaveBeenCalledTimes(1); // only the user message, no assistant reply
  });

  it('caps conversation history sent to the LLM', async () => {
    const longHistory = Array.from({ length: 30 }, (_, i) => ({
      messageId: `msg-${i}`,
      sessionId: 'session-1',
      role: (i % 2 === 0 ? 'user' : 'assistant') as const,
      content: `Message ${i}`,
      createdAt: '2024-01-01T00:00:00Z',
    }));
    messageRepo.getBySessionId.mockResolvedValue(longHistory);
    messageRepo.create.mockResolvedValue({
      messageId: 'msg-new',
      sessionId: 'session-1',
      role: 'user',
      content: 'New message',
      createdAt: '2024-01-01T00:00:00Z',
    });
    llmClient.chatCompletion.mockResolvedValue({ content: 'Reply', model: 'mock', usage: { totalTokens: 5 } });

    await service.continueConversation('session-1', 'New message');

    const sentMessages = llmClient.chatCompletion.mock.calls[0][0];
    // system prompt + 20 history + 1 new user message = 22
    expect(sentMessages.length).toBeLessThanOrEqual(22);
  });
});
```

## Test Organization

```
tests/
├── routes/
│   └── chat.test.ts          # E2E — real DB (truncated between tests), mocked LLM client
└── services/
    └── chat.service.test.ts  # Unit — mocked repositories AND mocked LLM client
```
