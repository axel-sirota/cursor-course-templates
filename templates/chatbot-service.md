# Chatbot Service Template

## Chat Service with LLM Integration

```python
# app/modules/chat/services/chat_service.py

from typing import List, Optional
from app.modules.chat.models import ChatSession, ChatSessionCreate, ChatSessionUpdate, Message, MessageCreate
from app.modules.chat.repository.repository import ChatSessionRepository, MessageRepository
from app.core.llm_client import llm_client
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

# System prompt for the chatbot
SYSTEM_PROMPT = """You are a helpful AI assistant. 
Provide concise, helpful responses to user questions.
Keep responses conversational and friendly.
"""

class ChatService:
    """Service for chat operations with LLM integration"""
    
    def __init__(self):
        # Initialize database session for repositories
        self.db = SessionLocal()
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'db'):
            self.db.close()
    
    async def start_conversation(self, user_id: str, message: str) -> dict:
        """Start a new conversation"""
        try:
            # Create chat session
            session_repo = ChatSessionRepository(self.db)
            session = session_repo.create(ChatSessionCreate(
                user_id=user_id,
                title=message[:50] if len(message) > 50 else message  # Use first 50 chars as title
            ))
            
            # Save user message
            message_repo = MessageRepository(self.db)
            user_msg = message_repo.create(MessageCreate(
                session_id=session.id,
                role="user",
                content=message
            ))
            
            # Get LLM response
            messages_for_llm = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
            
            llm_response_content = await self._get_llm_response(messages_for_llm)
            
            # Save assistant message
            assistant_msg = message_repo.create(MessageCreate(
                session_id=session.id,
                role="assistant",
                content=llm_response_content
            ))
            
            return {
                "message": llm_response_content,
                "session_id": session.id,
                "message_id": assistant_msg.id
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            raise
    
    async def continue_conversation(self, session_id: str, message: str, user_id: str) -> dict:
        """Continue an existing conversation"""
        try:
            # Validate session belongs to user
            session = await self._validate_session_ownership(session_id, user_id)
            
            # Save user message
            message_repo = MessageRepository(self.db)
            user_msg = message_repo.create(MessageCreate(
                session_id=session_id,
                role="user",
                content=message
            ))
            
            # Get conversation history
            history = message_repo.get_by_session_id(session_id)
            
            # Build conversation context for LLM
            messages_for_llm = self._build_conversation_context(history)
            messages_for_llm.append({"role": "user", "content": message})
            
            # Get LLM response
            llm_response_content = self._get_llm_response(messages_for_llm)
            
            # Save assistant message
            assistant_msg = message_repo.create(MessageCreate(
                session_id=session_id,
                role="assistant",
                content=llm_response_content
            ))
            
            return {
                "message": llm_response_content,
                "session_id": session_id,
                "message_id": assistant_msg.id
            }
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            raise
    
    async def get_conversation_history(self, session_id: str, user_id: str) -> List[Message]:
        """Get all messages in a conversation"""
        # Validate session belongs to user
        await self._validate_session_ownership(session_id, user_id)
        
        message_repo = MessageRepository(self.db)
        return message_repo.get_by_session_id(session_id)
    
    async def list_user_sessions(self, user_id: str, limit: int = 100, offset: int = 0) -> List[ChatSession]:
        """Get all sessions for a user"""
        session_repo = ChatSessionRepository(self.db)
        return session_repo.get_by_user_id(user_id, limit, offset)
    
    async def get_session(self, session_id: str, user_id: str) -> ChatSession:
        """Get a specific session"""
        session = await self._validate_session_ownership(session_id, user_id)
        return session
    
    async def update_session(self, session_id: str, session_data: ChatSessionUpdate, user_id: str) -> ChatSession:
        """Update a session"""
        # Validate session belongs to user
        await self._validate_session_ownership(session_id, user_id)
        
        session_repo = ChatSessionRepository(self.db)
        return session_repo.update(session_id, session_data)
    
    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session"""
        # Validate session belongs to user
        await self._validate_session_ownership(session_id, user_id)
        
        session_repo = ChatSessionRepository(self.db)
        return session_repo.delete(session_id)
    
    def _get_llm_response(self, messages: List[dict]) -> str:
        """Get response from LLM"""
        try:
            response = llm_client.chat_completion(
                messages=messages,
                model="gpt-4",
                temperature=0.7
            )
            return response["content"]
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise Exception("Failed to get AI response")
    
    def _build_conversation_context(self, messages: List[Message]) -> List[dict]:
        """Build conversation context for LLM"""
        messages_for_llm = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Add conversation history
        for msg in messages:
            messages_for_llm.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return messages_for_llm
    
    async def _validate_session_ownership(self, session_id: str, user_id: str) -> ChatSession:
        """Validate that session belongs to user"""
        session_repo = ChatSessionRepository(self.db)
        session = session_repo.get_by_id(session_id)
        
        if not session:
            raise Exception("Session not found")
        
        if session.user_id != user_id:
            raise Exception("Session access denied")
        
        return session
```

## Service Module Export

```python
# app/modules/chat/services/__init__.py

from .chat_service import ChatService

__all__ = ["ChatService"]
```

