# ✅ Reference Solution - Setup Complete!

## What's Ready

A complete, working FastAPI blog application using **raw SQL with psycopg2** (no ORM).

### Location
```
solutions/blog-api/
```

### Status
✅ Virtual environment created
✅ Dependencies installed  
✅ Docker PostgreSQL running (port 5433)
✅ Application starts successfully
✅ Database tables auto-created on startup
✅ All code follows raw SQL patterns

## Quick Start

```bash
cd solutions/blog-api

# Start Docker services
docker-compose up -d

# Activate virtual environment
source .venv/bin/activate

# Run the app
python main.py

# Visit http://localhost:8000/docs
```

## Important Notes

### Port Configuration
- **PostgreSQL**: Port **5433** (not 5432)
  - Your local PostgreSQL is on 5432
  - Docker PostgreSQL is on 5433 to avoid conflict
- **FastAPI**: Port 8000
- **pgAdmin**: Port 5050

### Database Connection
```
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/blog_db
```

## Architecture

### Raw SQL (No ORM)
```python
# Service layer uses psycopg2 directly
cursor.execute(
    """
    INSERT INTO posts (title, content, author_id)
    VALUES (%s, %s, %s)
    RETURNING id, title, content, created_at
    """,
    (title, content, author_id)
)
post = dict(cursor.fetchone())  # RealDictCursor
```

### Key Features
- ✅ **Context managers** for connections
- ✅ **Parameterized queries** (prevents SQL injection)
- ✅ **RealDictCursor** for dict-like results
- ✅ **Auto commit/rollback** on success/error
- ✅ **Database tables** created on startup

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

### Health
- `GET /health` - Health check

## Testing

### Run Tests
```bash
cd solutions/blog-api
source .venv/bin/activate
pytest tests/ -v
```

### Test Files
- `tests/test_api.py` - Basic E2E tests
- `tests/test_scenarios.py` - Detailed scenarios with input/output docs ⭐
- `tests/README.md` - Complete test documentation

## Teaching with This Solution

### Show Students
1. **Raw SQL patterns** in service layer
2. **Connection management** with context managers
3. **Parameterized queries** for security
4. **Layered architecture**: API → Service → SQL
5. **Test-driven approach** with clear input/output

### Key Files to Reference
- `app/core/database.py` - Connection management
- `app/modules/*/services/*.py` - Raw SQL examples
- `app/api/*.py` - Request/response conversion
- `tests/test_scenarios.py` - Test examples with docs

## Stopping Services

```bash
# Stop but keep data
docker-compose stop

# Stop and remove all data
docker-compose down -v

# Deactivate virtual environment
deactivate
```

## Troubleshooting

### Can't connect to database
- Check port 5433 (not 5432)
- Ensure Docker is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

### Port already in use
- Change PORT in `.env`
- Or stop conflicting service

### App won't start
- Check `.env` exists
- Ensure DATABASE_URL uses port 5433
- Verify Docker containers are healthy

## Next Steps

1. ✅ Application is ready to run
2. Test all endpoints at http://localhost:8000/docs
3. Use as reference during teaching
4. Show students the test scenarios
5. Walk through one complete flow: API → Service → SQL → Response

## Perfect for Teaching

This solution demonstrates:
- ✅ Professional FastAPI structure
- ✅ Raw SQL (no ORM magic)
- ✅ Security best practices
- ✅ Test-driven development
- ✅ Clear layered architecture
- ✅ Complete documentation

**Ready to use as teaching reference!** 🎓

