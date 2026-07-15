# LLM Client Integration Template

## Interface + OpenAI Implementation + Mock

```typescript
// src/config/llmClient.ts
import OpenAI from 'openai';
import { env } from './env';
import { logger } from './logger';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatCompletionResult {
  content: string;
  model: string;
  usage: { totalTokens: number };
}

export interface LLMClient {
  chatCompletion(
    messages: ChatMessage[],
    options?: { model?: string; temperature?: number; maxTokens?: number }
  ): Promise<ChatCompletionResult>;
}

export class OpenAILLMClient implements LLMClient {
  private readonly client: OpenAI;
  private readonly defaultModel: string;

  constructor() {
    if (!env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY not configured');
    }
    this.client = new OpenAI({ apiKey: env.OPENAI_API_KEY });
    this.defaultModel = env.OPENAI_MODEL ?? 'gpt-4o-mini';
  }

  async chatCompletion(
    messages: ChatMessage[],
    options: { model?: string; temperature?: number; maxTokens?: number } = {}
  ): Promise<ChatCompletionResult> {
    const model = options.model ?? this.defaultModel;

    try {
      logger.info({ model, messageCount: messages.length }, 'Sending chat completion request');

      const response = await this.client.chat.completions.create({
        model,
        messages,
        temperature: options.temperature ?? 0.7,
        ...(options.maxTokens ? { max_tokens: options.maxTokens } : {}),
      });

      const content = response.choices[0]?.message?.content ?? '';
      const totalTokens = response.usage?.total_tokens ?? 0;

      logger.info({ totalTokens }, 'Received chat completion response');

      return { content, model, usage: { totalTokens } };
    } catch (error) {
      logger.error({ err: error }, 'OpenAI API error');
      throw error;
    }
  }
}

export class MockLLMClient implements LLMClient {
  async chatCompletion(messages: ChatMessage[]): Promise<ChatCompletionResult> {
    logger.info({ messageCount: messages.length }, 'Mock LLM completion request');
    return {
      content: 'Mock LLM response - implement real LLM client as needed',
      model: 'mock-model',
      usage: { totalTokens: 50 },
    };
  }
}

/**
 * Select the LLM client implementation via LLM_PROVIDER env var.
 * Tests and CI default to 'mock' so no real API key or network call is required.
 */
function createLLMClient(): LLMClient {
  const provider = process.env.LLM_PROVIDER ?? (env.NODE_ENV === 'test' ? 'mock' : 'openai');
  return provider === 'mock' ? new MockLLMClient() : new OpenAILLMClient();
}

export const openAIClient: LLMClient = createLLMClient();
```

## Environment Variables

Add to `.env.example`:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
LLM_PROVIDER=openai
```

Add to `.env.test`:
```
LLM_PROVIDER=mock
```

Add to `src/config/env.ts`'s Zod schema:
```typescript
OPENAI_API_KEY: z.string().optional(),
OPENAI_MODEL: z.string().default('gpt-4o-mini'),
```

## Usage in a Service

```typescript
import { openAIClient } from '../config/llmClient';

export class ChatService {
  constructor(
    // ...
    private readonly llmClient: LLMClient = openAIClient
  ) {}
}
```

Injecting `LLMClient` via the constructor (rather than importing `openAIClient` directly inside methods) is what makes `ChatService` unit-testable with `MockLLMClient` or a Jest mock without any network access — see `templates/chatbot-tests.md`.

## Streaming (Optional Extension)

For streaming responses (e.g. server-sent events to the client), extend the interface rather than overloading `chatCompletion`:

```typescript
export interface LLMClient {
  chatCompletion(messages: ChatMessage[], options?: object): Promise<ChatCompletionResult>;
  streamChatCompletion?(messages: ChatMessage[], options?: object): AsyncIterable<string>;
}
```

```typescript
async *streamChatCompletion(messages: ChatMessage[]): AsyncIterable<string> {
  const stream = await this.client.chat.completions.create({
    model: this.defaultModel,
    messages,
    stream: true,
  });
  for await (const chunk of stream) {
    const delta = chunk.choices[0]?.delta?.content;
    if (delta) yield delta;
  }
}
```

Only implement this once a course module actually needs streaming — most chatbot exercises are fine with the simpler request/response `chatCompletion`.
