# Chatbot Tests Template

## E2E Tests

```python
# tests/api/test_chat.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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
    assert data["message"]  # Response should not be empty


def test_continue_conversation():
    """Test continuing an existing conversation"""
    # Start conversation
    start_response = client.post("/api/chat", json={
        "message": "Hello"
    })
    assert start_response.status_code == 200
    session_id = start_response.json()["sessionId"]
    
    # Continue conversation
    continue_response = client.post("/api/chat", json={
        "message": "What's my name?",
        "sessionId": session_id
    })
    assert continue_response.status_code == 200
    
    data = continue_response.json()
    assert data["sessionId"] == session_id
    assert "message" in data


def test_list_sessions():
    """Test listing user's chat sessions"""
    response = client.get("/api/chat/sessions")
    assert response.status_code == 200
    
    data = response.json()
    assert "sessions" in data
    assert "totalCount" in data
    assert isinstance(data["sessions"], list)


def test_get_session_messages():
    """Test retrieving messages for a session"""
    # Create conversation first
    start_response = client.post("/api/chat", json={
        "message": "Tell me a joke"
    })
    session_id = start_response.json()["sessionId"]
    
    # Get messages
    messages_response = client.get(f"/api/chat/sessions/{session_id}/messages")
    assert messages_response.status_code == 200
    
    data = messages_response.json()
    assert "messages" in data
    assert "sessionId" in data
    assert len(data["messages"]) == 2  # User message + assistant response


def test_get_session():
    """Test retrieving a specific session"""
    # Create conversation first
    start_response = client.post("/api/chat", json={
        "message": "Hello"
    })
    session_id = start_response.json()["sessionId"]
    
    # Get session
    session_response = client.get(f"/api/chat/sessions/{session_id}")
    assert session_response.status_code == 200
    
    data = session_response.json()
    assert data["sessionId"] == session_id
    assert "userId" in data
    assert "title" in data
    assert "createdAt" in data
    assert "updatedAt" in data


def test_update_session():
    """Test updating a session title"""
    # Create conversation first
    start_response = client.post("/api/chat", json={
        "message": "Hello"
    })
    session_id = start_response.json()["sessionId"]
    
    # Update session
    update_response = client.patch(
        f"/api/chat/sessions/{session_id}",
        params={"title": "Updated Title"}
    )
    assert update_response.status_code == 200
    
    data = update_response.json()
    assert data["title"] == "Updated Title"


def test_delete_session():
    """Test deleting a session"""
    # Create conversation first
    start_response = client.post("/api/chat", json={
        "message": "Hello"
    })
    session_id = start_response.json()["sessionId"]
    
    # Delete session
    delete_response = client.delete(f"/api/chat/sessions/{session_id}")
    assert delete_response.status_code == 200
    
    data = delete_response.json()
    assert data["success"] is True
    
    # Verify session is deleted
    get_response = client.get(f"/api/chat/sessions/{session_id}")
    assert get_response.status_code == 404


def test_continue_conversation_with_invalid_session():
    """Test continuing conversation with invalid session ID"""
    response = client.post("/api/chat", json={
        "message": "Hello",
        "sessionId": "invalid-session-id"
    })
    assert response.status_code == 404


def test_get_messages_for_invalid_session():
    """Test getting messages for invalid session"""
    response = client.get("/api/chat/sessions/invalid-id/messages")
    assert response.status_code == 404


def test_chat_with_empty_message():
    """Test sending empty message"""
    response = client.post("/api/chat", json={
        "message": ""
    })
    # Should either fail validation or handle gracefully
    assert response.status_code in [400, 422]
```

## Unit Tests with Mocked LLM

```python
# tests/modules/chat/test_chat_service.py

import pytest
from unittest.mock import Mock, patch
from app.modules.chat.models import Message, ChatSession, MessageCreate
from app.modules.chat.services.chat_service import ChatService


@pytest.fixture
def mock_llm_client():
    """Mock LLM client"""
    with patch('app.core.llm_client.llm_client') as mock:
        mock.chat_completion.return_value = {
            "content": "Mocked response from LLM"
        }
        yield mock


@pytest.fixture
def chat_service():
    """Create chat service instance"""
    return ChatService()


def test_get_llm_response(mock_llm_client):
    """Test LLM integration with mocked client"""
    service = ChatService()
    messages = [{"role": "user", "content": "Hello"}]
    
    result = service._get_llm_response(messages)
    
    assert result == "Mocked response from LLM"
    mock_llm_client.chat_completion.assert_called_once()


def test_build_conversation_context():
    """Test building conversation context from messages"""
    service = ChatService()
    
    messages = [
        Message(
            id="1",
            session_id="sess-1",
            role="user",
            content="Hello",
            created_at="2024-01-01T00:00:00"
        ),
        Message(
            id="2",
            session_id="sess-1",
            role="assistant",
            content="Hi there!",
            created_at="2024-01-01T00:00:01"
        )
    ]
    
    context = service._build_conversation_context(messages)
    
    assert len(context) == 3  # System prompt + 2 messages
    assert context[0]["role"] == "system"
    assert context[1]["role"] == "user"
    assert context[2]["role"] == "assistant"


def test_start_conversation_structure(mock_llm_client):
    """Test that start_conversation returns expected structure"""
    # This test would require mocking the database repositories
    # Implementation depends on database setup
    pass


def test_validate_session_ownership():
    """Test session ownership validation"""
    # This test would require mocking the session repository
    # Implementation depends on database setup
    pass
```

## Integration Tests (Optional)

```python
# tests/integration/test_chat_integration.py

import pytest
from app.modules.chat.services.chat_service import ChatService


@pytest.mark.integration
def test_full_conversation_flow():
    """Integration test for complete conversation flow"""
    # This test requires actual database and LLM setup
    # Skip if not in integration environment
    pass
```

## Test Configuration

```python
# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "permissions": ["read", "write"]
    }
```

