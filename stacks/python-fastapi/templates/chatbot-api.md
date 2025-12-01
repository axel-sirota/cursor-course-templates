# Chatbot API Template

## Chat API Endpoints

```python
# app/api/chat.py

from fastapi import APIRouter, HTTPException, Depends, status
from app.core.dependencies import require_auth
from app.modules.chat.services.chat_service import ChatService
from .api_models import (
    ChatRequest,
    ChatResponse,
    SessionResponse,
    MessageResponse,
    SessionsListResponse,
    MessagesListResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# =============================================================================
# CHAT ENDPOINTS
# =============================================================================

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(require_auth)
):
    """Start or continue a chat conversation"""
    try:
        service = ChatService()
        
        if request.session_id:
            # Continue existing conversation
            response_data = await service.continue_conversation(
                session_id=request.session_id,
                message=request.message,
                user_id=current_user["user_id"]
            )
        else:
            # Start new conversation
            response_data = await service.start_conversation(
                user_id=current_user["user_id"],
                message=request.message
            )
        
        return ChatResponse(
            message=response_data["message"],
            sessionId=response_data["session_id"],
            messageId=response_data["message_id"]
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        if "not found" in str(e).lower() or "access denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process chat request"
            )


@router.get("/sessions", response_model=SessionsListResponse)
async def list_sessions(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(require_auth)
):
    """Get all chat sessions for the current user"""
    try:
        service = ChatService()
        sessions = await service.list_user_sessions(
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset
        )
        
        session_responses = [
            SessionResponse(
                sessionId=session.id,
                userId=session.user_id,
                title=session.title,
                createdAt=session.created_at.isoformat(),
                updatedAt=session.updated_at.isoformat()
            )
            for session in sessions
        ]
        
        return SessionsListResponse(
            sessions=session_responses,
            totalCount=len(session_responses)
        )
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@router.get("/sessions/{session_id}/messages", response_model=MessagesListResponse)
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(require_auth)
):
    """Get all messages for a specific session"""
    try:
        service = ChatService()
        messages = await service.get_conversation_history(
            session_id=session_id,
            user_id=current_user["user_id"]
        )
        
        message_responses = [
            MessageResponse(
                messageId=msg.id,
                sessionId=msg.session_id,
                role=msg.role,
                content=msg.content,
                createdAt=msg.created_at.isoformat()
            )
            for msg in messages
        ]
        
        return MessagesListResponse(
            messages=message_responses,
            sessionId=session_id
        )
        
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        if "not found" in str(e).lower() or "access denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve messages"
            )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: dict = Depends(require_auth)
):
    """Get a specific chat session"""
    try:
        service = ChatService()
        session = await service.get_session(
            session_id=session_id,
            user_id=current_user["user_id"]
        )
        
        return SessionResponse(
            sessionId=session.id,
            userId=session.user_id,
            title=session.title,
            createdAt=session.created_at.isoformat(),
            updatedAt=session.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        if "not found" in str(e).lower() or "access denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve session"
            )


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    title: str,
    current_user: dict = Depends(require_auth)
):
    """Update a chat session (currently only title)"""
    try:
        from app.modules.chat.models import ChatSessionUpdate
        
        service = ChatService()
        session = await service.update_session(
            session_id=session_id,
            session_data=ChatSessionUpdate(title=title),
            user_id=current_user["user_id"]
        )
        
        return SessionResponse(
            sessionId=session.id,
            userId=session.user_id,
            title=session.title,
            createdAt=session.created_at.isoformat(),
            updatedAt=session.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        if "not found" in str(e).lower() or "access denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update session"
            )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(require_auth)
):
    """Delete a chat session"""
    try:
        service = ChatService()
        success = await service.delete_session(
            session_id=session_id,
            user_id=current_user["user_id"]
        )
        
        if success:
            return {"success": True, "message": "Session deleted"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        if "not found" in str(e).lower() or "access denied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete session"
            )
```

## Register Router

```python
# app/main.py (add this line)

from app.api import chat

# In create_app() function:
app.include_router(chat.router)
```

## API Models (Referenced Above)

The API models are defined in `templates/chatbot-models.md` under the "API Models (camelCase)" section.

