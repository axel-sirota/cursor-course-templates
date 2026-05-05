# Blog API

RESTful blog API built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.

## Features

- **Authentication**: User registration, login with JWT tokens
- **Posts**: CRUD operations for blog posts
- **Comments**: Add comments to posts
- **Tags**: Organize posts with tags
- **Pagination**: Paginated list endpoints
- **OpenAPI**: Auto-generated API documentation

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy 2.0 AsyncIO)
- **Migrations**: Alembic
- **Testing**: Pytest
- **Linting**: Ruff
- **Type Checking**: Mypy

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- pip

### 1. Clone and Install

```bash
# Copy environment variables
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Database

```bash
# Start PostgreSQL with Docker Compose
docker-compose up -d

# Wait for database to be ready
docker-compose logs -f db
```

### 3. Run Application

```bash
# Start FastAPI server
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Project Structure

```
.
├── app/
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings
│   │   └── dependencies.py # FastAPI dependencies
│   ├── api/                # API endpoints
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── posts.py        # Post endpoints
│   │   ├── comments.py     # Comment endpoints
│   │   └── tags.py         # Tag endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic layer
│   └── main.py             # Application entrypoint
├── tests/                  # Tests
│   ├── api/                # API endpoint tests
│   └── conftest.py         # Pytest fixtures
├── plan/                   # Development plans
│   ├── api-design.md       # API design document
│   └── sessions/           # Session plans
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker setup
├── pyproject.toml          # Tool configuration
└── README.md               # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Posts
- `POST /api/posts` - Create post (authenticated)
- `GET /api/posts` - List posts (paginated)
- `GET /api/posts/{post_id}` - Get single post
- `PUT /api/posts/{post_id}` - Update post (author only)
- `DELETE /api/posts/{post_id}` - Delete post (author only)

### Comments
- `POST /api/posts/{post_id}/comments` - Add comment (authenticated)
- `GET /api/posts/{post_id}/comments` - List comments
- `DELETE /api/comments/{comment_id}` - Delete comment (author only)

### Tags
- `GET /api/tags` - List all tags
- `GET /api/tags/{tag_name}/posts` - Get posts by tag

### Health
- `GET /health` - Health check

## Development Phases

### Phase 0: Skeleton ✅
- Project structure created
- Mock endpoints implemented
- All endpoints return mock data
- Tests passing

### Phase 1: Authentication (Next)
- Real user authentication
- Password hashing with bcrypt
- JWT token generation
- Database persistence

### Phase 2: Posts CRUD
- Full CRUD operations for posts
- Authorization (author-only updates/deletes)
- Pagination

### Phase 3: Comments
- Comment functionality
- Nested resources
- Authorization

### Phase 4: Tags
- Many-to-many relationships
- Tag management
- Filter posts by tag

### Phase 5: Polish & Deploy
- Advanced filtering and sorting
- Search functionality
- Error handling
- Production Docker setup

## Development

### Run Linter

```bash
ruff check app/ tests/
```

### Run Type Checker

```bash
mypy app/
```

### Format Code

```bash
ruff format app/ tests/
```

## Environment Variables

See `.env.example` for all required environment variables:

- `PORT` - Application port (default: 8000)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `JWT_EXPIRATION_DAYS` - Token expiration (default: 7)
- `CORS_ORIGINS` - Allowed CORS origins

## Current Status

**Phase 0 (Skeleton) - Complete**

All 13 endpoints implemented with mock data. Ready to begin Phase 1 (Authentication).

To continue development, see `plan/sessions/session-2-phase-1.md` for next steps.

## License

MIT
