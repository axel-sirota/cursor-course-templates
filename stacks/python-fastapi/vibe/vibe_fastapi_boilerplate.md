# FastAPI Project Boilerplate Guide

## Purpose

This guide provides step-by-step instructions for creating a complete FastAPI project boilerplate with authentication, database integration, and modular structure. After following this guide, you'll have a working API that starts with `python main.py` and follows Python best practices with ruff, mypy, and pytest.

## Quick Start Checklist

- [ ] Create virtual environment and install dependencies
- [ ] Copy .env.example to .env and configure
- [ ] Run `python main.py`
- [ ] Test API at http://localhost:8000/docs

## Project Structure

```
project_name/
├── .env.example
├── .env                    # Not in git
├── .gitignore
├── requirements.txt
├── pyproject.toml          # Test configuration
├── main.py                 # Single entry point
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── database.py
│   │   ├── storage.py
│   │   ├── llm_client.py
│   │   ├── middleware.py
│   │   └── dependencies.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── auth.py
│   │   └── tools/          # Agent Tools APIs
│   │       ├── __init__.py
│   │       └── .gitkeep
│   └── modules/
│       ├── __init__.py
│       └── .gitkeep        # Keep directory in git
└── tests/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   ├── test_health.py
    │   ├── test_auth.py
    │   └── tools/          # Tests for Agent Tools APIs
    │       ├── __init__.py
    │       └── .gitkeep
    └── modules/
        ├── __init__.py
        └── .gitkeep        # Keep directory in git
```

## Create Complete Project Structure

**Step-by-step file creation** (copy each file exactly as shown):

### 1. Create Directory Structure
```bash
mkdir my_project && cd my_project
mkdir -p app/core app/api app/api/tools app/modules tests/api tests/api/tools tests/modules
touch app/__init__.py app/core/__init__.py app/api/__init__.py app/api/tools/__init__.py app/modules/__init__.py
touch tests/__init__.py tests/api/__init__.py tests/api/tools/__init__.py tests/modules/__init__.py
touch app/modules/.gitkeep app/api/tools/.gitkeep tests/modules/.gitkeep tests/api/tools/.gitkeep
```

### 2. Environment & Dependencies

Create each file with exact content:

**requirements.txt**
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic[email]==2.10.0
pydantic-settings==2.7.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
python-multipart==0.0.12
pytest==8.3.0
pytest-asyncio==0.24.0
httpx>=0.24.0,<0.28.0
```

**.env.example**
```
# Server
PORT=8000
HOST=0.0.0.0
DEBUG=True

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/your_database
DATABASE_NAME=your_database
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM (Optional - remove if not needed)
# OPENAI_API_KEY=your_openai_key
```

**.gitignore**
```
# Environment
.env
.venv/
venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

### 3. Core Configuration Files

**app/core/config.py**
```python
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    
    # Database
    database_url: str = ""
    database_name: str = "your_database"
    database_user: str = "postgres"
    database_password: str = "postgres"
    database_host: str = "localhost"
    database_port: int = 5432
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # LLM (Optional)
    openai_api_key: str = ""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    @property
    def allowed_origins(self) -> List[str]:
        """CORS allowed origins - read from environment variable"""
        # Check environment variable first
        env_origins = os.getenv("ALLOWED_ORIGINS")
        if env_origins:
            origins = [origin.strip() for origin in env_origins.split(",")]
            return origins
        
        # Fall back to hardcoded list for local development
        return [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ]

settings = Settings()
```

**app/core/logging.py**
```python
import logging
import json
import sys
from typing import Dict, Any
from app.core.config import settings

class RailwayJSONFormatter(logging.Formatter):
    """JSON formatter optimized for Railway deployment"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 'stack_info'):
                log_data[key] = value
        
        return json.dumps(log_data)

def setup_logging():
    """Configure logging for the application"""
    level = logging.DEBUG if settings.debug else logging.INFO
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.debug:
        # Use simple format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s [%(name)s]'
        )
    else:
        # Use JSON format for production/Railway
        formatter = RailwayJSONFormatter()
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("fastapi").setLevel(level)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)
```

**app/core/database.py**
```python
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

# Create global database instance
db = engine
```

**app/core/storage.py**
```python
from typing import Optional, BinaryIO
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageClient:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    def upload_file(self, bucket: str, path: str, file: BinaryIO) -> bool:
        """Upload file to local storage"""
        try:
            bucket_path = self.storage_path / bucket
            bucket_path.mkdir(exist_ok=True)
            
            file_path = bucket_path / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(file.read())
            
            logger.info(f"File uploaded successfully to {bucket}/{path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False
    
    def download_file(self, bucket: str, path: str) -> Optional[bytes]:
        """Download file from local storage"""
        try:
            file_path = self.storage_path / bucket / path
            if file_path.exists():
                with open(file_path, "rb") as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None

# Create global storage instance
storage = StorageClient()
```

**app/core/llm_client.py**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request"""
        pass

class MockLLMClient(LLMClient):
    """Mock LLM client for development/testing"""
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Return mock completion"""
        logger.info(f"Mock LLM completion request with {len(messages)} messages")
        
        return {
            "content": "Mock LLM response - implement real LLM client as needed",
            "model": "mock-model",
            "usage": {"total_tokens": 50}
        }

# Create global LLM client
llm_client = MockLLMClient()
```

### 4. Middleware & Dependencies Files

**app/core/middleware.py**
```python
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestResponseMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging and correlation IDs"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        
        # Add correlation ID to request state
        request.state.correlation_id = correlation_id
        
        # Log incoming request
        start_time = time.time()
        logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                "Request failed with exception",
                extra={
                    "correlation_id": correlation_id,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 4)
            }
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
```

**app/core/dependencies.py**
```python
from fastapi import HTTPException, status
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Simple in-memory user storage for demo purposes
USERS_DB = {}

class Permission:
    """Permission constants"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

def get_current_user() -> Optional[dict]:
    """Get current user - simplified for demo without authentication"""
    # For demo purposes, return a default user
    # In a real app, you might use session-based auth or other methods
    return {
        "user_id": "demo-user-123",
        "email": "demo@example.com",
        "full_name": "Demo User",
        "permissions": [Permission.READ, Permission.WRITE]
    }

def require_permission(required_permissions: List[str] = None):
    """Dependency factory for permission checking"""
    required_permissions = required_permissions or []
    
    def permission_checker() -> dict:
        current_user = get_current_user()
        
        # For demo, always return the demo user
        return current_user
    
    return permission_checker

# Common dependency instances
require_auth = require_permission([])
require_read = require_permission([Permission.READ])
require_write = require_permission([Permission.WRITE])
require_admin = require_permission([Permission.ADMIN])
```

### 5. API Implementation Files

**app/api/health.py**
```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.database import db
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    database: bool
    environment: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Check database connectivity
    db_healthy = False
    try:
        if db:
            # Simple connection test - execute a simple query
            with db.connect() as conn:
                conn.execute("SELECT 1")
            db_healthy = True
            logger.info("Database health check passed")
        else:
            logger.warning("Database not available - check database credentials")
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_healthy = False
    
    return HealthResponse(
        status="healthy",
        database=db_healthy,
        environment="development" if settings.debug else "production"
    )
```

**app/api/auth.py**
```python
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from app.core.dependencies import require_auth, Permission
from typing import List
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory user storage for development (replace with database in production)
USERS_DB = {}

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = Field(default="", alias="fullName")
    
    model_config = {"validate_by_name": True}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    message: str
    user: dict

class UserResponse(BaseModel):
    user_id: str = Field(alias="userId")
    email: str
    full_name: str = Field(alias="fullName") 
    permissions: List[str]
    
    model_config = {"validate_by_name": True}  # Allow both snake_case and camelCase

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    email = request.email.lower()
    
    # Check if user already exists
    if email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered"
        )
    
    # Create user
    user_id = secrets.token_urlsafe(16)
    
    USERS_DB[email] = {
        "user_id": user_id,
        "email": email,
        "full_name": request.full_name,
        "password": request.password,  # In real app, hash this
        "permissions": [Permission.READ, Permission.WRITE]  # Default permissions
    }
    
    logger.info(f"User registered: {email}")
    
    return AuthResponse(
        message="Registration successful",
        user={
            "userId": user_id,
            "email": email,
            "fullName": request.full_name
        }
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """User login"""
    email = request.email.lower()
    
    # Find user
    user = USERS_DB.get(email)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    logger.info(f"User logged in: {email}")
    
    return AuthResponse(
        message="Login successful",
        user={
            "userId": user["user_id"],
            "email": email,
            "fullName": user["full_name"]
        }
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(require_auth)):
    """Get current user information"""
    return UserResponse(
        userId=current_user["user_id"],
        email=current_user["email"],
        fullName=current_user.get("full_name", "Demo User"),
        permissions=current_user.get("permissions", [])
    )

@router.post("/logout")
async def logout():
    """User logout"""
    return {"message": "Logged out successfully"}
```

### 6. Main Application Files

**app/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.middleware import RequestResponseMiddleware
from app.api import health, auth
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Application starting up")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Allowed origins: {settings.allowed_origins}")
    yield
    # Shutdown
    logger.info("Application shutting down")

def create_app() -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="Project API",
        description="FastAPI project with authentication and modular structure",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(RequestResponseMiddleware)
    
    # Include routers
    app.include_router(health.router)
    app.include_router(auth.router)
    
    return app

app = create_app()
```

**main.py** (single entry point)
```python
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
```

### 7. Test Configuration

**pyproject.toml**
```toml
[tool.pytest.ini_options]
asyncio_default_fixture_loop_scope = "function"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["-v", "--tb=short"]
filterwarnings = [
    "ignore::DeprecationWarning:supabase",
    "ignore::DeprecationWarning:jose",
    "ignore::DeprecationWarning:pydantic",
    "ignore::pytest.PytestDeprecationWarning"
]
```

### 8. Test Files

**Test Organization**: Tests mirror the app directory structure for better organization and maintainability:
- `tests/api/` - Tests for API endpoints (health, auth, etc.)
- `tests/modules/` - Tests for business modules (each module gets its own subdirectory)

**tests/api/test_health.py**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "environment" in data
```

**tests/api/test_auth.py**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    """Test user registration"""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "user" in data
    assert data["message"] == "Registration successful"

def test_login():
    """Test user login"""
    # First register
    client.post("/api/auth/register", json={
        "email": "test2@example.com",
        "password": "testpassword",
        "full_name": "Test User 2"
    })
    
    # Then login
    response = client.post("/api/auth/login", json={
        "email": "test2@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert data["message"] == "Login successful"

def test_protected_endpoint():
    """Test accessing protected endpoint"""
    # Access protected endpoint (no auth needed in demo)
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    
    data = response.json()
    assert "userId" in data
    assert data["email"] == "demo@example.com"

def test_unauthorized_access():
    """Test accessing protected endpoint without auth"""
    response = client.get("/api/auth/me")
    assert response.status_code == 200  # No auth required in demo
```

## Usage Instructions

### 1. Create Project and Virtual Environment
```bash
# Create project directory
mkdir my_project && cd my_project

# Create virtual environment in project root
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies using virtual environment
.venv/bin/python3 -m pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

### 3. Run Application
```bash
# Start development server
python main.py

# Or run tests (warning-free)
pytest tests/
```

### 4. Test API
- Visit http://localhost:8000/docs for Swagger UI
- Test health: GET /health
- Register user: POST /api/auth/register
- Login: POST /api/auth/login
- Access protected endpoint: GET /api/auth/me

## API Architecture Pattern

### Dual API Structure

This boilerplate supports a **dual API architecture** that separates concerns based on API consumers:

1. **Experience APIs** (`/api/*`): UI-facing APIs for human users
   - Handle user authentication and authorization
   - Optimized for presentation layer concerns
   - Handle user authentication and authorization
   - Located in `app/api/`

2. **Agent Tools APIs** (`/api/tools/*`): Internal APIs for AI agents and automation
   - Handle service-to-service authentication
   - Optimized for programmatic access
   - Use service authentication
   - Located in `app/api/tools/`

### Example Dual API Implementation

**Experience API** (`app/api/module_api.py`):
```python
from fastapi import APIRouter, Depends
from app.core.dependencies import require_auth

router = APIRouter(prefix="/module", tags=["module"])

@router.get("/data")
async def get_data(current_user: dict = Depends(require_auth)):
    """UI-facing endpoint for human users"""
    return {"data": "UI-optimized response", "user_id": current_user["user_id"]}
```

**Agent Tools API** (`app/api/tools/module_tool_api.py`):
```python
from fastapi import APIRouter, Header
from typing import Optional

router = APIRouter(prefix="/tools/module", tags=["module_tools"])

@router.get("/data")
async def get_data_for_agent():
    """Agent-facing endpoint for automation"""
    # Service authentication would go here
    return {"data": "Agent-optimized response", "timestamp": "2024-01-01T00:00:00Z"}
```

**Register both routers** in `app/main.py`:
```python
from app.api import module_api
from app.api.tools import module_tool_api

# In create_app() function
app.include_router(module_api.router, prefix="/api")
app.include_router(module_tool_api.router, prefix="/api")
```

### Benefits of Dual API Pattern

- **Different authentication models**: User auth vs service auth
- **Different response formats**: UI-optimized vs agent-optimized
- **Different rate limiting**: User-based vs service-based quotas
- **Cleaner separation of concerns**: UI logic vs automation logic
- **Future flexibility**: Agent-specific features without affecting UI

## API Guidelines

### Request/Response Models
- Use snake_case in Python code
- Use camelCase for API JSON with Pydantic aliases:

```python
class UserRequest(BaseModel):
    full_name: str = Field(alias="fullName")
    email_address: str = Field(alias="emailAddress")
    
    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase
```

### Adding Protected Endpoints
```python
from app.core.dependencies import require_permission, Permission

@router.get("/protected")
async def protected_endpoint(
    user: dict = Depends(require_permission([Permission.READ]))
):
    return {"message": "This is protected", "user_id": user["user_id"]}
```

### Error Handling
```python
from fastapi import HTTPException, status

if not data:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found"
    )
```
## Code Quality & Error Prevention

### Development Tools Setup

Add these tools to catch errors before deployment. This setup focuses on **edge points only** for type checking to maintain development speed while ensuring quality at critical boundaries.

**requirements-dev.txt**
```
# Code quality tools
ruff==0.6.0
mypy==1.8.0
black==24.0.0
isort==5.13.0

# Testing tools
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==4.1.0
httpx>=0.24.0,<0.28.0
```

**pyproject.toml** (add to existing or create new)
```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = ["E501", "B008"]  # Line too long, function call in argument defaults

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = false
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# MyPy configuration for edge points only
# Only check type safety at external boundaries:
# - API endpoints (app/api/)
# - Core services (app/core/)
# - Service layer interfaces (app/modules/*/services/)

# External dependencies
[[tool.mypy.overrides]]
module = ["sqlalchemy.*", "jose.*", "alembic.*"]
ignore_missing_imports = true

# Skip internal implementation details
[[tool.mypy.overrides]]
module = [
    "app.modules.*.agents.*",
    "app.modules.*.processors.*",
    "app.modules.*.prompts.*",
    "app.models.*"
]
ignore_errors = true
```

**Makefile** (optional convenience commands)
```makefile
.PHONY: lint format type-check test quality install-dev

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

format:
	black app/ tests/
	isort app/ tests/

lint:
	ruff check app/ tests/

type-check:
	mypy app/api/ app/core/ app/modules/*/services/

test:
	pytest tests/ -v

quality: format lint type-check test
	@echo "All quality checks passed!"

fix:
	ruff check app/ tests/ --fix
	black app/ tests/
	isort app/ tests/
```

### Usage Commands

**Initial setup:**
```bash
pip install -r requirements-dev.txt
```

**Manual quality checks (run when ready):**
```bash
make quality
# Or individually:
ruff check app/ tests/ --fix  # Catch import errors, undefined names, auto-fix
mypy app/api/ app/core/ app/modules/*/services/  # Type checking (edge points only)
black app/ tests/             # Format code
pytest tests/ -v              # Run tests with verbose output
```

### IDE Integration

**VS Code settings.json:**
```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### Quality Approach

This setup uses a **focused approach** to code quality:

**Ruff (All Code):**
- Undefined variables and functions
- Missing imports
- Unused imports
- Syntax errors
- Code style issues

**MyPy (Edge Points Only):**
- Type safety at external boundaries
- API endpoint type validation
- Core service interface validation
- Service layer type checking

**Benefits:**
- ✅ **Faster development** - No type checking overhead on internal code
- ✅ **Focus on what matters** - Type safety where it's most critical
- ✅ **Reduced complexity** - Less type annotation maintenance
- ✅ **Better developer experience** - Less friction during development

**Example error catching:**
```python
# This will be caught by ruff (all code)
from nonexistent_module import something  # Import error
undefined_variable = 123  # Undefined variable

# This will be caught by mypy (edge points only)
@app.post("/api/analyze")
async def analyze_business(request: BusinessRequest) -> BusinessResponse:
    return request.upper()  # Type error: BusinessRequest != str
```

### CI Integration Example

Add this to your CI pipeline:
```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt -r requirements-dev.txt
    
- name: Lint and type check
  run: |
    ruff check app/ tests/ --fix
    mypy app/api/ app/core/ app/modules/*/services/
    
- name: Run tests
  run: pytest tests/ --cov=app
```

This setup ensures code quality from development through deployment, focusing type checking on critical boundaries while maintaining development speed.

## Next Steps

After creating the boilerplate:

1. **Configure Database**: Update .env with your database credentials
2. **Add Modules**: Create new modules in the modules/ directory following the modular pattern
3. **Implement Real LLM**: Replace mock LLM client with actual OpenAI integration
4. **Database Models**: Create SQLAlchemy models and run migrations
5. **Production Setup**: Configure deployment settings

## Troubleshooting

**"Module not found" errors**: Ensure all __init__.py files are present
**Database connection fails**: Check database credentials in .env
**CORS errors**: Add your frontend URL to ALLOWED_ORIGINS in .env