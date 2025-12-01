# Chatbot Models Template

## Layered Pydantic Models for Chatbot

### Chat Session Models

```python
# app/modules/chat/models/domain_models.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# =============================================================================
# CHAT SESSION MODELS - Layered Architecture
# =============================================================================

class ChatSessionBase(BaseModel):
    """Base ChatSession model with only business fields (no id, timestamps)"""
    user_id: str = Field(..., description="User identifier")
    title: Optional[str] = Field(default=None, description="Chat session title")
    
    class Config:
        from_attributes = True

class ChatSession(ChatSessionBase):
    """Full ChatSession model with all database fields"""
    id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: datetime = Field(..., description="Session update timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class ChatSessionCreate(ChatSessionBase):
    """ChatSession creation model (inherits from ChatSessionBase)"""
    pass

class ChatSessionUpdate(BaseModel):
    """ChatSession update model (only fields that can be updated)"""
    title: Optional[str] = Field(default=None, description="Chat session title")
    
    class Config:
        from_attributes = True
```

### Message Models

```python
# app/modules/chat/models/domain_models.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# =============================================================================
# MESSAGE MODELS - Layered Architecture
# =============================================================================

class MessageBase(BaseModel):
    """Base Message model with only business fields (no id, timestamps)"""
    session_id: str = Field(..., description="Chat session identifier")
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    
    class Config:
        from_attributes = True

class Message(MessageBase):
    """Full Message model with all database fields"""
    id: str = Field(..., description="Unique message identifier")
    created_at: datetime = Field(..., description="Message creation timestamp")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class MessageCreate(MessageBase):
    """Message creation model (inherits from MessageBase)"""
    pass

class MessageUpdate(BaseModel):
    """Message update model (only updatable fields)"""
    content: Optional[str] = Field(default=None, description="Message content")
    
    class Config:
        from_attributes = True
```

### Export Models

```python
# app/modules/chat/models/__init__.py

from .domain_models import (
    ChatSession,
    ChatSessionCreate,
    ChatSessionUpdate,
    Message,
    MessageCreate,
    MessageUpdate,
)

__all__ = [
    "ChatSession",
    "ChatSessionCreate",
    "ChatSessionUpdate",
    "Message",
    "MessageCreate",
    "MessageUpdate",
]
```

## API Models (camelCase)

```python
# app/api/chat.py

from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(
        alias="sessionId", 
        default=None, 
        description="Session ID for continuing conversation"
    )
    
    model_config = {"validate_by_name": True}


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str = Field(..., description="Assistant response")
    session_id: str = Field(alias="sessionId", description="Chat session ID")
    message_id: str = Field(alias="messageId", description="Message ID")
    
    model_config = {"validate_by_name": True}


class SessionResponse(BaseModel):
    """Response model for chat session"""
    session_id: str = Field(alias="sessionId", description="Session ID")
    user_id: str = Field(alias="userId", description="User ID")
    title: Optional[str] = Field(..., description="Session title")
    created_at: str = Field(alias="createdAt", description="Creation timestamp")
    updated_at: str = Field(alias="updatedAt", description="Update timestamp")
    
    model_config = {"validate_by_name": True}


class MessageResponse(BaseModel):
    """Response model for message"""
    message_id: str = Field(alias="messageId", description="Message ID")
    session_id: str = Field(alias="sessionId", description="Session ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    created_at: str = Field(alias="createdAt", description="Creation timestamp")
    
    model_config = {"validate_by_name": True}


class SessionsListResponse(BaseModel):
    """Response model for sessions list"""
    sessions: List[SessionResponse]
    total_count: int = Field(alias="totalCount")
    
    model_config = {"validate_by_name": True}


class MessagesListResponse(BaseModel):
    """Response model for messages list"""
    messages: List[MessageResponse]
    session_id: str = Field(alias="sessionId", description="Session ID")
    
    model_config = {"validate_by_name": True}
```

