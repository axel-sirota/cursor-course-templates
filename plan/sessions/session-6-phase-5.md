# Session 6: Phase 5 - Polish & Deploy

## Goal
Add production-ready features: advanced filtering, sorting, search, comprehensive error handling, rate limiting, and production Docker setup.

## Prerequisites
- ✅ All core features complete (Auth, Posts, Comments, Tags)
- ✅ Basic E2E tests passing
- ✅ Development environment stable
- ✅ Docker Compose working

## LLM Implementation Instructions

This is the final polish phase. Focus areas:
1. **User Experience**: Advanced filtering, sorting, search
2. **Production Readiness**: Error handling, validation, rate limiting
3. **Deployment**: Production Dockerfile, optimizations
4. **Observability**: Logging, monitoring, health checks
5. **Performance**: Database indexes, query optimization

Work incrementally: implement one feature, test, commit, then move to next.

## Implementation Tasks

### 1. Advanced Filtering & Sorting

Update `app/api/posts.py` to support query parameters:

```python
from typing import Literal

@router.get("", response_model=PostListResponse)
async def list_posts(
    page: int = 1,
    page_size: int = 20,
    # Filtering
    author_id: str | None = None,
    published: bool | None = None,
    tag: str | None = None,
    # Sorting
    sort: Literal["created_at", "updated_at", "title"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    # Search
    q: str | None = None,  # Search query
    db: AsyncSession = Depends(get_db),
) -> PostListResponse:
    """List posts with advanced filtering, sorting, and search."""
    service = PostService(db)
    return await service.list_posts(
        page=page,
        page_size=page_size,
        author_id=author_id,
        published=published,
        tag=tag,
        sort_by=sort,
        sort_order=order,
        search_query=q,
    )
```

Update `PostRepository.list_posts()`:

```python
async def list_posts(
    self,
    skip: int,
    limit: int,
    author_id: str | None = None,
    published: bool | None = None,
    tag: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    search_query: str | None = None,
) -> tuple[list[Post], int]:
    """List posts with filtering, sorting, and search.
    
    Returns:
        Tuple of (posts, total_count)
    """
    query = select(Post).options(selectinload(Post.tags))
    count_query = select(func.count(Post.id))
    
    # Filtering
    if author_id:
        query = query.where(Post.author_id == author_id)
        count_query = count_query.where(Post.author_id == author_id)
    
    if published is not None:
        query = query.where(Post.published == published)
        count_query = count_query.where(Post.published == published)
    
    if tag:
        # Filter by tag (requires join)
        normalized_tag = normalize_tag_name(tag)
        query = query.join(Post.tags).where(Tag.name == normalized_tag)
        count_query = count_query.join(post_tags).join(Tag).where(Tag.name == normalized_tag)
    
    # Search
    if search_query:
        search_pattern = f"%{search_query}%"
        search_condition = or_(
            Post.title.ilike(search_pattern),
            Post.content.ilike(search_pattern),
        )
        query = query.where(search_condition)
        count_query = count_query.where(search_condition)
    
    # Sorting
    sort_column = getattr(Post, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    # Execute
    result = await self.db.execute(query)
    posts = result.scalars().all()
    
    count_result = await self.db.execute(count_query)
    total = count_result.scalar()
    
    return posts, total
```

### 2. Comprehensive Error Handling

Create `app/core/errors.py`:

```python
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import uuid


class APIError(Exception):
    """Base API error with code and message."""
    
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    request_id: str,
    details: list | None = None,
) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "requestId": request_id,
            }
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors (422)."""
    request_id = str(uuid.uuid4())
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    return create_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request_id=request_id,
        details=errors,
    )


async def integrity_error_handler(
    request: Request,
    exc: IntegrityError,
) -> JSONResponse:
    """Handle database integrity errors (unique constraint, etc.)."""
    request_id = str(uuid.uuid4())
    
    # Parse common integrity errors
    error_message = str(exc.orig)
    if "unique constraint" in error_message.lower():
        if "email" in error_message.lower():
            message = "Email address already exists"
            code = "EMAIL_EXISTS"
        elif "username" in error_message.lower():
            message = "Username already exists"
            code = "USERNAME_EXISTS"
        else:
            message = "Duplicate entry"
            code = "DUPLICATE_ENTRY"
    else:
        message = "Database constraint violation"
        code = "INTEGRITY_ERROR"
    
    return create_error_response(
        code=code,
        message=message,
        status_code=status.HTTP_400_BAD_REQUEST,
        request_id=request_id,
    )


async def sqlalchemy_error_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """Handle general SQLAlchemy errors."""
    request_id = str(uuid.uuid4())
    
    # Log full error for debugging
    import logging
    logging.error(f"SQLAlchemy error: {exc}", exc_info=True)
    
    return create_error_response(
        code="DATABASE_ERROR",
        message="A database error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all exception handler."""
    request_id = str(uuid.uuid4())
    
    # Log full error
    import logging
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return create_error_response(
        code="INTERNAL_ERROR",
        message="An internal server error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )
```

Register error handlers in `app/main.py`:

```python
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.errors import (
    validation_exception_handler,
    integrity_error_handler,
    sqlalchemy_error_handler,
    generic_exception_handler,
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

### 3. Request Validation

Update Pydantic schemas with validation:

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreatePostRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10000)
    tags: list[str] | None = Field(None, max_length=10)
    published: bool = True
    
    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        
        for tag in v:
            if len(tag) > 50:
                raise ValueError("Tag name cannot exceed 50 characters")
            if not tag.strip():
                raise ValueError("Tag name cannot be empty")
        
        return v


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v
    
    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
```

### 4. Rate Limiting

Create `app/core/rate_limit.py`:

```python
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from typing import Dict, Tuple


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests: int = 100, window: int = 60):
        """
        Args:
            requests: Number of requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.clients: Dict[str, list[datetime]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """Check if client is allowed to make request.
        
        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window)
        
        # Remove old requests
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if req_time > cutoff
        ]
        
        # Check limit
        if len(self.clients[client_id]) >= self.requests:
            oldest = self.clients[client_id][0]
            retry_after = int((oldest + timedelta(seconds=self.window) - now).total_seconds())
            return False, retry_after
        
        # Record request
        self.clients[client_id].append(now)
        return True, 0


rate_limiter = RateLimiter(requests=100, window=60)


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    client_ip = request.client.host
    
    allowed, retry_after = rate_limiter.is_allowed(client_ip)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            headers={"Retry-After": str(retry_after)},
        )
    
    response = await call_next(request)
    return response
```

Add to `app/main.py`:

```python
from app.core.rate_limit import rate_limit_middleware

app.middleware("http")(rate_limit_middleware)
```

### 5. Production Dockerfile

Create `Dockerfile`:

```dockerfile
# Multi-stage build for smaller image size

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app/ /app/app/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G

  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${PORT:-8000}:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: production
      DEBUG: "false"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  postgres_data:
```

### 7. Database Optimization

Add indexes for common queries:

```bash
alembic revision -m "Add performance indexes"
```

In migration:
```python
def upgrade():
    # Index for filtering published posts
    op.create_index(
        "idx_posts_published_created",
        "posts",
        ["published", "created_at"],
        postgresql_where=sa.text("published = true"),
    )
    
    # Index for author's posts
    op.create_index(
        "idx_posts_author_created",
        "posts",
        ["author_id", "created_at"],
    )
    
    # Index for full-text search on title
    op.execute(
        "CREATE INDEX idx_posts_title_search ON posts USING gin(to_tsvector('english', title))"
    )
    
    # Index for email lookups (if not already exists)
    op.create_index("idx_users_email_lower", "users", [sa.text("LOWER(email)")])
```

### 8. Structured Logging

Update `app/core/logging.py`:

```python
import logging
import json
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format logs as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "request_id"):
            log_data["requestId"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["userId"] = record.user_id
        
        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

Call in `app/main.py`:
```python
from app.core.logging import setup_logging

setup_logging(level=settings.log_level)
```

### 9. Enhanced Health Check

Update `app/api/health.py`:

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str | dict]:
    """Health check with database connectivity test."""
    health = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {},
    }
    
    # Test database connection
    try:
        await db.execute(text("SELECT 1"))
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["status"] = "degraded"
        health["checks"]["database"] = f"error: {str(e)}"
    
    status_code = status.HTTP_200_OK if health["status"] == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return health
```

### 10. Integration Tests

Create `tests/integration/test_full_workflow.py`:

```python
import pytest
from fastapi.testclient import TestClient


def test_complete_user_journey(client: TestClient):
    """Test complete user journey: register → login → create post → comment → tag → search."""
    
    # 1. Register user
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "johndoe",
            "email": "john@example.com",
            "password": "SecurePass123",
        },
    )
    assert register_response.status_code == 201
    token = register_response.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create post with tags
    post_response = client.post(
        "/api/posts",
        headers=headers,
        json={
            "title": "My First Blog Post",
            "content": "This is a comprehensive guide to Python programming.",
            "tags": ["python", "tutorial", "beginner"],
            "published": True,
        },
    )
    assert post_response.status_code == 201
    post_id = post_response.json()["postId"]
    
    # 3. Add comment
    comment_response = client.post(
        f"/api/posts/{post_id}/comments",
        headers=headers,
        json={"content": "Great post!"},
    )
    assert comment_response.status_code == 201
    
    # 4. Search for post
    search_response = client.get("/api/posts?q=Python")
    assert search_response.status_code == 200
    assert len(search_response.json()["posts"]) >= 1
    
    # 5. Filter by tag
    tag_response = client.get("/api/tags/python/posts")
    assert tag_response.status_code == 200
    assert len(tag_response.json()["posts"]) >= 1
    
    # 6. Update post
    update_response = client.put(
        f"/api/posts/{post_id}",
        headers=headers,
        json={"title": "Updated Title"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"
    
    # 7. List own posts
    my_posts_response = client.get(
        f"/api/posts?authorId={register_response.json()['userId']}",
        headers=headers,
    )
    assert my_posts_response.status_code == 200
    assert len(my_posts_response.json()["posts"]) >= 1
```

## Acceptance Criteria

### Filtering & Search
- [ ] Can filter posts by author_id
- [ ] Can filter posts by published status
- [ ] Can filter posts by tag
- [ ] Can search posts by title/content
- [ ] Can combine multiple filters
- [ ] Can sort by created_at, updated_at, title
- [ ] Can sort ascending/descending

### Error Handling
- [ ] Validation errors return 422 with details
- [ ] Duplicate email/username returns 400
- [ ] Database errors caught and logged
- [ ] All errors have consistent format
- [ ] Error responses include request ID

### Validation
- [ ] Title length validated (1-200 chars)
- [ ] Content length validated (1-10000 chars)
- [ ] Email format validated
- [ ] Password strength validated
- [ ] Tag count limited (max 10)

### Rate Limiting
- [ ] Requests limited to 100/minute per IP
- [ ] Returns 429 when limit exceeded
- [ ] Includes Retry-After header

### Production Docker
- [ ] Dockerfile builds successfully
- [ ] Multi-stage build reduces image size
- [ ] Runs as non-root user
- [ ] Health check passes
- [ ] docker-compose.prod.yml works

### Database Optimization
- [ ] Indexes created for common queries
- [ ] Query performance acceptable (<100ms for lists)
- [ ] Connection pooling configured

### Logging
- [ ] Logs in JSON format
- [ ] All errors logged with stack traces
- [ ] Request IDs tracked

### Testing
- [ ] Integration test passes (full workflow)
- [ ] All previous tests still pass
- [ ] 40+ total E2E tests passing

## Session Completion

When complete:
1. Build production image: `docker build -t blog-api .`
2. Test production stack: `docker-compose -f docker-compose.prod.yml up`
3. Run full test suite: `pytest tests/ -v --cov=app`
4. Load test with 100 concurrent requests
5. Create session summary
6. Commit: `git commit -m "feat: production polish and deployment (Phase 5)"`

## Production Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables documented
- [ ] Database migrations up to date
- [ ] Docker image builds and runs
- [ ] Health check endpoint responding
- [ ] Error handling comprehensive
- [ ] Logging configured
- [ ] Rate limiting active
- [ ] Security headers configured
- [ ] API documentation complete

## Next Steps

After this session, the API is production-ready. Next steps:
- Deploy to cloud platform (AWS ECS, GCP Cloud Run, etc.)
- Set up CI/CD pipeline (GitHub Actions, GitLab CI)
- Configure domain and SSL certificate
- Add monitoring (Sentry, DataDog, Prometheus)
- Set up backup strategy for database
- Performance testing and optimization
- Security audit

## Session Duration
Estimated: 120-150 minutes
