# Chatbot Domain Guide

## Purpose

This guide provides domain-specific patterns for building a chatbot API with FastAPI and OpenAI integration. This guide focuses on conversation management, message handling, and LLM integration patterns.

## Domain Overview

### Core Entities

**Chat Session**
- Represents a conversation between a user and the chatbot
- Contains metadata about the conversation (user_id, title, created_at, updated_at)
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

### Layered Pydantic Models

Follow the layered model architecture:

**ChatSession Models**
- `ChatSessionBase`: Business fields (user_id, title)
- `ChatSession`: Full model with id, timestamps
- `ChatSessionCreate`: For creation
- `ChatSessionUpdate`: For updates

**Message Models**
- `MessageBase`: Business fields (session_id, role, content)
- `Message`: Full model with id, timestamps
- `MessageCreate`: For creation
- `MessageUpdate`: For updates (rarely used)

### API Models (camelCase)

**Request Models**
```python
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(alias="sessionId", default=None, description="Session ID for continuing conversation")
    
    model_config = {"validate_by_name": True}
```

**Response Models**
```python
class ChatResponse(BaseModel):
    message: str = Field(alias="message", description="Assistant response")
    session_id: str = Field(alias="sessionId", description="Chat session ID")
    message_id: str = Field(alias="messageId", description="Message ID")
    
    model_config = {"validate_by_name": True}

class SessionResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    title: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    
    model_config = {"validate_by_name": True}
```

## Repository Patterns

### ChatSession Repository

```python
class ChatSessionRepository:
    """Repository for chat session operations"""
    
    def create(self, session_data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session"""
        pass
    
    def get_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        pass
    
    def get_by_user_id(self, user_id: str, limit: int = 100) -> List[ChatSession]:
        """Get all sessions for a user"""
        pass
    
    def update(self, session_id: str, session_data: ChatSessionUpdate) -> ChatSession:
        """Update a session"""
        pass
    
    def delete(self, session_id: str) -> bool:
        """Delete a session"""
        pass
```

### Message Repository

```python
class MessageRepository:
    """Repository for message operations"""
    
    def create(self, message_data: MessageCreate) -> Message:
        """Create a new message"""
        pass
    
    def get_by_session_id(self, session_id: str) -> List[Message]:
        """Get all messages for a session"""
        pass
    
    def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        pass
```

## Service Layer Patterns

### Chat Service

The service layer orchestrates chat operations and LLM integration:

```python
class ChatService:
    """Service for chat operations with LLM integration"""
    
    def __init__(self):
        self.session_repo = ChatSessionRepository()
        self.message_repo = MessageRepository()
        self.llm_client = LLMClient()
    
    async def start_conversation(self, user_id: str, message: str) -> ChatResponse:
        """Start a new conversation"""
        # 1. Create chat session
        # 2. Send user message to LLM
        # 3. Save both messages
        # 4. Return response
        pass
    
    async def continue_conversation(self, session_id: str, message: str) -> ChatResponse:
        """Continue existing conversation"""
        # 1. Get chat session
        # 2. Get conversation history
        # 3. Send to LLM with context
        # 4. Save messages
        # 5. Return response
        pass
    
    async def get_conversation_history(self, session_id: str) -> List[Message]:
        """Get all messages in a conversation"""
        return await self.message_repo.get_by_session_id(session_id)
    
    async def list_user_sessions(self, user_id: str) -> List[ChatSession]:
        """Get all sessions for a user"""
        return await self.session_repo.get_by_user_id(user_id)
```

### LLM Integration Pattern

```python
def _get_llm_response(self, messages: List[Dict[str, str]]) -> str:
    """Get response from LLM"""
    try:
        response = self.llm_client.chat_completion(
            messages=messages,
            model="gpt-4",  # or configurable
            temperature=0.7
        )
        return response["content"]
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise
```

## API Endpoints

### Experience APIs (for users)

**POST /api/chat**
- Start new conversation or continue existing
- Request: `ChatRequest`
- Response: `ChatResponse`

**GET /api/chat/sessions**
- List user's chat sessions
- Response: `List[SessionResponse]`

**GET /api/chat/sessions/{session_id}/messages**
- Get messages for a session
- Response: `List[MessageResponse]`

**POST /api/chat/sessions/{session_id}**
- Update session title
- Request: `{"title": "..."}`
- Response: `SessionResponse`

**DELETE /api/chat/sessions/{session_id}**
- Delete a session
- Response: `{"success": true}`

## Testing Strategy

### E2E Tests

Test the complete flow:
```python
def test_start_conversation():
    """Test starting a new conversation"""
    response = client.post("/api/chat", json={
        "message": "Hello, who are you?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "sessionId" in data
    assert "messageId" in data

def test_continue_conversation():
    """Test continuing an existing conversation"""
    # Start conversation
    start_response = client.post("/api/chat", json={"message": "Hello"})
    session_id = start_response.json()["sessionId"]
    
    # Continue
    continue_response = client.post("/api/chat", json={
        "message": "What's my name?",
        "sessionId": session_id
    })
    assert continue_response.status_code == 200
    assert continue_response.json()["sessionId"] == session_id

def test_get_conversation_history():
    """Test retrieving conversation history"""
    # Create conversation with multiple messages
    # Retrieve history
    # Verify all messages are returned
    pass
```

### Unit Tests with Mocked LLM

Mock the LLM client for fast unit tests:
```python
@pytest.fixture
def mock_llm_client():
    """Mock LLM client"""
    with patch('app.core.llm_client.llm_client') as mock:
        mock.chat_completion.return_value = {"content": "Mocked response"}
        yield mock

def test_get_llm_response(mock_llm_client):
    """Test LLM integration with mocked client"""
    service = ChatService()
    messages = [{"role": "user", "content": "Hello"}]
    
    result = service._get_llm_response(messages)
    
    assert result == "Mocked response"
    mock_llm_client.chat_completion.assert_called_once()
```

## Session Management Patterns

### Conversation Context

Maintain conversation history for LLM context:
```python
def _build_conversation_context(self, messages: List[Message]) -> List[Dict[str, str]]:
    """Build conversation context for LLM"""
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
```

### Session Validation

Validate session ownership:
```python
async def validate_session_ownership(self, session_id: str, user_id: str) -> ChatSession:
    """Validate that session belongs to user"""
    session = await self.session_repo.get_by_id(session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
```

## OpenAI Integration

### Client Setup

See `templates/llm-client.md` for OpenAI client patterns.

### Prompt Engineering

**System Prompt**
```python
SYSTEM_PROMPT = """You are a helpful AI assistant. 
Provide concise, helpful responses to user questions.
Keep responses conversational and friendly.
"""
```

**Context Management**
```python
def _prepare_messages(self, user_message: str, history: List[Message]) -> List[Dict[str, str]]:
    """Prepare messages for LLM with system prompt"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Add conversation history
    messages.extend([
        {"role": msg.role, "content": msg.content}
        for msg in history
    ])
    
    # Add current message
    messages.append({"role": "user", "content": user_message})
    
    return messages
```

## Error Handling

### LLM Errors

```python
try:
    response = self.llm_client.chat_completion(messages)
except OpenAIError as e:
    logger.error(f"OpenAI error: {e}")
    raise HTTPException(status_code=503, detail="AI service unavailable")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Performance Considerations

### Token Management

Track token usage for cost management:
- Estimate tokens before sending
- Set token limits per conversation
- Cache responses when appropriate

### Rate Limiting

Implement rate limiting for LLM calls:
- Per-user rate limits
- Per-session limits
- Exponential backoff on errors

## Security Considerations

### Input Validation

Validate and sanitize user input:
```python
def validate_message(message: str) -> str:
    """Validate and sanitize message"""
    if len(message) > 10000:  # Token limit
        raise ValueError("Message too long")
    return message.strip()
```

### User Isolation

Ensure conversations are properly isolated:
- Always validate user ownership
- Never expose other users' conversations
- Use parameterized queries to prevent SQL injection

## Example Endpoint Implementation

```python
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(require_auth)
):
    """Start or continue a chat conversation"""
    service = ChatService()
    
    if request.session_id:
        # Continue existing conversation
        response = await service.continue_conversation(
            session_id=request.session_id,
            message=request.message,
            user_id=current_user["user_id"]
        )
    else:
        # Start new conversation
        response = await service.start_conversation(
            user_id=current_user["user_id"],
            message=request.message
        )
    
    return response
```

## Database Schema Suggestions

```sql
-- Chat sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_sessions_user_id ON chat_sessions(user_id);
```

## Next Steps

1. Create database models following layered architecture
2. Implement repositories for chat sessions and messages
3. Create chat service with LLM integration
4. Build API endpoints with proper error handling
5. Add comprehensive E2E tests
6. Implement rate limiting and security measures

## Anti-Patterns to Avoid

❌ **Don't store LLM responses in raw database fields**
✅ **Use structured models with proper validation**

❌ **Don't send full conversation history on every request**
✅ **Cache conversation context efficiently**

❌ **Don't expose internal LLM errors to users**
✅ **Return user-friendly error messages**

❌ **Don't skip input validation**
✅ **Validate and sanitize all user input**

❌ **Don't use async LLM calls when not needed**
✅ **Use synchronous LLM operations for simpler integration**

