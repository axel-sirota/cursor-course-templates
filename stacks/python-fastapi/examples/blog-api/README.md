# Blog API Reference Solution

**TEACHER ONLY** - Complete working FastAPI application using raw SQL

## Architecture

### Key Technologies
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Production database (Docker)
- **psycopg2**: Raw SQL queries (NO SQLAlchemy/ORM)
- **Pydantic**: Request/response validation
- **pytest**: E2E testing

### Structure
```
blog-api/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── config.py          # Environment configuration
│   │   └── database.py        # Raw SQL connection management
│   ├── api/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── posts.py           # Blog post endpoints
│   │   └── comments.py        # Comment endpoints
│   └── modules/
│       ├── users/services/    # User business logic
│       ├── posts/services/    # Post business logic
│       └── comments/services/ # Comment business logic
├── tests/
│   ├── conftest.py            # Test configuration
│   ├── test_api.py            # Basic E2E tests
│   ├── test_scenarios.py      # Detailed test scenarios
│   └── README.md              # Test documentation
├── docker-compose.yml          # PostgreSQL + pgAdmin
├── requirements.txt            # Python dependencies
└── main.py                     # Application entry point
```

## Quick Start

### 1. Start Docker Services
```bash
cd solutions/blog-api
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- pgAdmin on port 5050 (http://localhost:5050)

### 2. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults should work)
```

### 4. Run Application
```bash
python main.py
```

Visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 5. Run Tests
```bash
pytest tests/ -v
```

## Raw SQL Architecture

### Connection Management
```python
# app/core/database.py
@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### Service Layer Pattern
```python
# app/modules/posts/services/post_service.py
class PostService:
    def __init__(self, conn):
        self.conn = conn
    
    def create_post(self, title, content, author_id):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO posts (title, content, author_id)
            VALUES (%s, %s, %s)
            RETURNING id, title, content, author_id, created_at
            """,
            (title, content, author_id)
        )
        return dict(cursor.fetchone())
```

### API Layer
```python
# app/api/posts.py
@router.post("", response_model=PostResponse)
async def create_post(request: CreatePostRequest, conn = Depends(get_db)):
    service = PostService(conn)
    post = service.create_post(request.title, request.content, request.authorId)
    return PostResponse(postId=str(post["id"]), ...)
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Posts Table
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Comments Table
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Posts
- `POST /api/posts` - Create blog post
- `GET /api/posts/{id}` - Get post by ID

### Comments
- `POST /api/posts/{id}/comments` - Create comment
- `GET /api/posts/{id}/comments` - List comments

## Testing Strategy

### E2E Tests
All tests use real PostgreSQL database (same as production):
- Tests create/drop tables for isolation
- Use `client` fixture for API testing
- Use `db_connection` fixture for direct database access

### Test Files
1. **test_api.py** - Basic smoke tests
2. **test_scenarios.py** - Detailed scenarios with input/output docs
3. **tests/README.md** - Complete testing guide

## Key Patterns to Show Students

### 1. Raw SQL with Parameterized Queries
```python
cursor.execute(
    "INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING id",
    (title, content)
)
```
**Never use string formatting - always use %s placeholders!**

### 2. RealDictCursor for Dict Results
```python
cursor = conn.cursor()  # Returns RealDictRow
post = cursor.fetchone()
print(post["id"])  # Access by key, not index
```

### 3. Layered Architecture
- **API Layer**: Request/response conversion (camelCase ↔ snake_case)
- **Service Layer**: Business logic, validation, raw SQL
- **Database**: PostgreSQL with raw SQL queries

### 4. Context Managers for Connections
```python
with get_db_connection() as conn:
    # Use connection
    pass  # Automatically commits/rolls back
```

### 5. FastAPI Dependency Injection
```python
async def endpoint(conn = Depends(get_db)):
    service = SomeService(conn)
    # Use service
```

## Common Issues & Solutions

### Database Connection Errors
```bash
# Check if PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Port Already in Use
```bash
# Change PORT in .env file
PORT=8001

# Or stop conflicting service
lsof -ti:8000 | xargs kill -9
```

### Tests Failing
```bash
# Ensure database is running
docker-compose ps

# Run with verbose output
pytest tests/ -v -s

# Run single test
pytest tests/test_api.py::test_health_check -v
```

## pgAdmin Access

1. Visit http://localhost:5050
2. Login:
   - Email: admin@blog.com
   - Password: admin
3. Add Server:
   - Host: postgres (or host.docker.internal on Mac/Windows)
   - Port: 5432
   - Database: blog_db
   - Username: postgres
   - Password: postgres

## Teaching Tips

### Session 1 Demo
1. Show docker-compose.yml (PostgreSQL setup)
2. Show database.py (raw SQL connections)
3. Show one complete flow: API → Service → SQL
4. Run one test showing input/output
5. Use pgAdmin to show actual database records

### Key Points to Emphasize
- ✅ Raw SQL (not ORM) for clarity and control
- ✅ Parameterized queries prevent SQL injection
- ✅ RealDictCursor returns dict-like rows
- ✅ Context managers handle commit/rollback
- ✅ Service layer contains business logic
- ✅ API layer just converts formats

### Common Student Mistakes
- ❌ Using string formatting in SQL (SQL injection!)
- ❌ Forgetting to commit transactions
- ❌ Not closing database connections
- ❌ Mixing business logic in API endpoints

## Next Steps

After understanding this reference:
1. Walk through one endpoint completely
2. Have students trace: Request → API → Service → SQL → Response
3. Show how tests validate the flow
4. Let students build similar endpoint independently

## Stopping Services

```bash
# Stop but keep data
docker-compose stop

# Stop and remove data
docker-compose down -v

# Deactivate virtual environment
deactivate
```

