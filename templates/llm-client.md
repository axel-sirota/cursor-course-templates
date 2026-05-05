# LLM Client Integration Template

## OpenAI Client Setup

```python
# app/core/llm_client.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available")


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send chat completion request to LLM"""
        pass


class OpenAILLMClient(LLMClient):
    """OpenAI LLM client implementation"""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-4"
        self.default_temperature = 0.7
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Send chat completion request to OpenAI"""
        try:
            logger.info(f"Sending chat completion request to {model}")
            
            completion_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens is not None:
                completion_kwargs["max_tokens"] = max_tokens
            
            # Add any additional kwargs
            completion_kwargs.update(kwargs)
            
            response = self.client.chat.completions.create(**completion_kwargs)
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Extract usage information
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            logger.info(f"Received response with {usage['total_tokens']} tokens")
            
            return {
                "content": content,
                "model": model,
                "usage": usage,
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class MockLLMClient(LLMClient):
    """Mock LLM client for development/testing"""
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Return mock completion"""
        logger.info(f"Mock LLM completion request with {len(messages)} messages")
        
        # Get the last user message for mock response
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        mock_response = f"Mock LLM response to: {last_user_message}"
        
        return {
            "content": mock_response,
            "model": "mock-model",
            "usage": {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75}
        }


# Initialize LLM client based on configuration
def get_llm_client() -> LLMClient:
    """Get the appropriate LLM client instance"""
    if settings.openai_api_key and OPENAI_AVAILABLE:
        try:
            return OpenAILLMClient()
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}. Using mock client.")
            return MockLLMClient()
    else:
        logger.warning("Using mock LLM client (OpenAI not configured)")
        return MockLLMClient()


# Global LLM client instance
llm_client = get_llm_client()
```

## Configuration

```python
# app/core/config.py (add to Settings class)

class Settings(BaseSettings):
    # ... existing settings ...
    
    # LLM
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4", description="Default OpenAI model")
    openai_temperature: float = Field(default=0.7, description="Default temperature")
    
    # ... rest of settings ...
```

## Environment Variables

```bash
# .env.example (add these lines)

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
```

## Usage Patterns

### Basic Usage

```python
from app.core.llm_client import llm_client

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"}
]

response = llm_client.chat_completion(messages)
print(response["content"])
```

### With Custom Parameters

```python
response = llm_client.chat_completion(
    messages=messages,
    model="gpt-3.5-turbo",
    temperature=0.9,
    max_tokens=500
)
```

### Error Handling

```python
try:
    response = llm_client.chat_completion(messages)
    content = response["content"]
except Exception as e:
    logger.error(f"LLM request failed: {e}")
    # Fallback or error handling
    content = "Sorry, I'm having trouble processing your request."
```

### With Retry Logic

```python
import time
from typing import Optional

def chat_completion_with_retry(
    messages: List[Dict[str, str]],
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Optional[str]:
    """Chat completion with automatic retry"""
    for attempt in range(max_retries):
        try:
            response = llm_client.chat_completion(messages)
            return response["content"]
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                raise
    
    return None
```

## Testing with Mocked Client

```python
# In your test files

from unittest.mock import AsyncMock, patch
from app.core.llm_client import llm_client

@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    return {
        "content": "Test response",
        "model": "gpt-4",
        "usage": {"total_tokens": 100}
    }

def test_with_mocked_llm(mock_llm_response):
    """Test with mocked LLM client"""
    with patch.object(llm_client, 'chat_completion') as mock:
        mock.return_value = mock_llm_response
        
        response = llm_client.chat_completion([
            {"role": "user", "content": "Hello"}
        ])
        
        assert response["content"] == "Test response"
        mock.assert_called_once()
```

## Rate Limiting

```python
# app/core/rate_limiter.py (optional)

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

class RateLimiter:
    """Simple rate limiter for LLM requests"""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

# Global rate limiter
rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
```

## Token Management

```python
# app/utils/token_estimator.py (optional)

def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """Rough token estimation"""
    # Simple approximation: ~4 characters per token for most models
    return len(text) // 4

def truncate_to_max_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to fit within token limit"""
    estimated = estimate_tokens(text)
    if estimated <= max_tokens:
        return text
    
    # Truncate to fit
    max_chars = max_tokens * 4
    return text[:max_chars]
```

## Security Considerations

### API Key Protection

```python
# Never log the API key
logger.info(f"Using model: {model}")  # ✅ OK
logger.info(f"API key: {api_key}")    # ❌ NEVER DO THIS

# Store in environment variables, not in code
```

### Input Validation

```python
def validate_message_length(content: str, max_length: int = 10000) -> str:
    """Validate and sanitize message content"""
    if len(content) > max_length:
        raise ValueError(f"Message too long (max {max_length} characters)")
    
    # Basic sanitization
    return content.strip()
```

### Response Validation

```python
def validate_llm_response(response: Dict[str, Any]) -> str:
    """Validate LLM response"""
    if "content" not in response:
        raise ValueError("Invalid LLM response: missing content")
    
    content = response["content"]
    
    if not content or not isinstance(content, str):
        raise ValueError("Invalid LLM response: content is not a string")
    
    return content
```

## Production Considerations

1. **Connection Pooling**: Reuse OpenAI client instance
2. **Timeout Settings**: Set appropriate timeouts for requests
3. **Error Handling**: Implement proper error handling and retries
4. **Logging**: Log requests and responses (without sensitive data)
5. **Monitoring**: Track token usage and costs
6. **Rate Limiting**: Implement rate limiting per user
7. **Caching**: Consider caching responses for repeated queries

## Next Steps

1. Add OpenAI to requirements.txt
2. Configure API key in environment variables
3. Implement error handling and retries
4. Add rate limiting if needed
5. Set up monitoring and logging
6. Test with mock client in development

