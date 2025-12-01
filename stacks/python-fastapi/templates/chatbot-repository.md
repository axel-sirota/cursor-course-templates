# Chatbot Repository Template

## ChatSession Repository

```python
# app/modules/chat/repository/repository.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.chat.models import ChatSession, ChatSessionCreate, ChatSessionUpdate
from app.modules.chat.models.database_models import ChatSessionDB
import logging

logger = logging.getLogger(__name__)

class ChatSessionRepository:
    """Repository for ChatSession table operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, session_data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session"""
        try:
            db_session = ChatSessionDB(
                user_id=session_data.user_id,
                title=session_data.title or "New Chat"
            )
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            
            return ChatSession(
                id=str(db_session.id),
                user_id=db_session.user_id,
                title=db_session.title,
                created_at=db_session.created_at,
                updated_at=db_session.updated_at
            )
                
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            self.db.rollback()
            raise
    
    def get_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        try:
            db_session = self.db.query(ChatSessionDB).filter(
                ChatSessionDB.id == session_id
            ).first()
            
            if db_session:
                return ChatSession(
                    id=str(db_session.id),
                    user_id=db_session.user_id,
                    title=db_session.title,
                    created_at=db_session.created_at,
                    updated_at=db_session.updated_at
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting session by ID {session_id}: {e}")
            raise
    
    def get_by_user_id(self, user_id: str, limit: int = 100, offset: int = 0) -> List[ChatSession]:
        """Get all sessions for a user"""
        try:
            db_sessions = (
                self.db.query(ChatSessionDB)
                .filter(ChatSessionDB.user_id == user_id)
                .order_by(ChatSessionDB.updated_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            return [
                ChatSession(
                    id=str(db_session.id),
                    user_id=db_session.user_id,
                    title=db_session.title,
                    created_at=db_session.created_at,
                    updated_at=db_session.updated_at
                )
                for db_session in db_sessions
            ]
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            raise
    
    def update(self, session_id: str, session_data: ChatSessionUpdate) -> ChatSession:
        """Update an existing session"""
        try:
            db_session = self.db.query(ChatSessionDB).filter(
                ChatSessionDB.id == session_id
            ).first()
            
            if not db_session:
                raise Exception("Session not found")
            
            update_data = session_data.model_dump(exclude_none=True)
            for field, value in update_data.items():
                setattr(db_session, field, value)
            
            self.db.commit()
            self.db.refresh(db_session)
            
            return ChatSession(
                id=str(db_session.id),
                user_id=db_session.user_id,
                title=db_session.title,
                created_at=db_session.created_at,
                updated_at=db_session.updated_at
            )
                
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            self.db.rollback()
            raise
    
    def delete(self, session_id: str) -> bool:
        """Delete a session by ID"""
        try:
            db_session = self.db.query(ChatSessionDB).filter(
                ChatSessionDB.id == session_id
            ).first()
            
            if db_session:
                self.db.delete(db_session)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            self.db.rollback()
            raise
```

## Message Repository

```python
# app/modules/chat/repository/repository.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.chat.models import Message, MessageCreate, MessageUpdate
from app.modules.chat.models.database_models import MessageDB
import logging

logger = logging.getLogger(__name__)

class MessageRepository:
    """Repository for Message table operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, message_data: MessageCreate) -> Message:
        """Create a new message"""
        try:
            db_message = MessageDB(
                session_id=message_data.session_id,
                role=message_data.role,
                content=message_data.content
            )
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            
            return Message(
                id=str(db_message.id),
                session_id=str(db_message.session_id),
                role=db_message.role,
                content=db_message.content,
                created_at=db_message.created_at
            )
                
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            self.db.rollback()
            raise
    
    def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        try:
            db_message = self.db.query(MessageDB).filter(
                MessageDB.id == message_id
            ).first()
            
            if db_message:
                return Message(
                    id=str(db_message.id),
                    session_id=str(db_message.session_id),
                    role=db_message.role,
                    content=db_message.content,
                    created_at=db_message.created_at
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting message by ID {message_id}: {e}")
            raise
    
    def get_by_session_id(self, session_id: str) -> List[Message]:
        """Get all messages for a session"""
        try:
            db_messages = (
                self.db.query(MessageDB)
                .filter(MessageDB.session_id == session_id)
                .order_by(MessageDB.created_at.asc())
                .all()
            )
            
            return [
                Message(
                    id=str(db_message.id),
                    session_id=str(db_message.session_id),
                    role=db_message.role,
                    content=db_message.content,
                    created_at=db_message.created_at
                )
                for db_message in db_messages
            ]
            
        except Exception as e:
            logger.error(f"Error getting messages for session {session_id}: {e}")
            raise
    
    def delete(self, message_id: str) -> bool:
        """Delete a message by ID"""
        try:
            db_message = self.db.query(MessageDB).filter(
                MessageDB.id == message_id
            ).first()
            
            if db_message:
                self.db.delete(db_message)
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")
            self.db.rollback()
            raise
```

## Repository Module Export

```python
# app/modules/chat/repository/__init__.py

# Repositories are not exported - access through services only
__all__ = []
```

## Database Models

```python
# app/modules/chat/models/database_models.py

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from datetime import datetime
import uuid

class ChatSessionDB(Base):
    """SQLAlchemy model for chat sessions"""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class MessageDB(Base):
    """SQLAlchemy model for messages"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
```

