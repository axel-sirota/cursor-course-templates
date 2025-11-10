# Chatbot Requirements Template

## Requirements.txt for Chatbot with OpenAI

```txt
# FastAPI and Server
fastapi==0.115.0
uvicorn[standard]==0.32.0

# Data Validation and Configuration
pydantic[email]==2.10.0
pydantic-settings==2.7.0

# Database (if using database)
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# LLM Integration
openai>=1.30.0

# Authentication (if needed)
python-jose[cryptography]==3.3.0
python-multipart==0.0.12

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==4.1.0
httpx>=0.24.0,<0.28.0

# Code Quality
ruff==0.6.0
black==24.0.0
mypy==1.8.0
isort==5.13.0

# Environment
python-dotenv==1.0.0
```

## Key Dependencies Explained

### Core Application
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **pydantic-settings**: Configuration management

### LLM Integration
- **openai**: OpenAI API client for LLM integration

### Database (Optional)
- **sqlalchemy**: ORM for database operations
- **alembic**: Database migration tool
- **psycopg2-binary**: PostgreSQL driver

### Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for testing FastAPI

### Code Quality
- **ruff**: Fast linter and formatter
- **black**: Code formatter
- **mypy**: Static type checker
- **isort**: Import sorting

## Installation Commands

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -r requirements.txt
```

## Environment Variables

```bash
# .env.example
PORT=8000
HOST=0.0.0.0
DEBUG=True

# Database (if using)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatbot_db

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## Version Notes

- **OpenAI**: Use version 1.30.0+ for latest async support
- **FastAPI**: 0.115.0+ for latest features
- **Pydantic**: 2.10.0 for v2 API with email validation
- **SQLAlchemy**: 2.0.25 for modern ORM patterns

## Optional Dependencies

If you need additional features:

```txt
# Redis for caching (optional)
redis==5.0.0

# Celery for background tasks (optional)
celery==5.3.0

# Sentry for error tracking (optional)
sentry-sdk==1.40.0

# Rate limiting (optional)
slowapi==0.1.9

# WebSocket support (optional)
websockets==12.0
```

## Development Dependencies

```txt
# Development tools
ipython==8.20.0  # Interactive Python
ipdb==0.13.13    # Debugger
pytest-watch==4.2.0  # Auto-run tests on file changes
blackd==24.0.0   # Black daemon for faster formatting
```

## Security Considerations

- Always use latest versions with security fixes
- Pin specific versions in production
- Regularly update dependencies
- Use `pip-audit` to check for vulnerabilities

```bash
pip install pip-audit
pip-audit
```

