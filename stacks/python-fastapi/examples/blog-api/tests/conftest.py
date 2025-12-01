"""
Pytest Configuration and Fixtures
Uses PostgreSQL for testing (same as production)
"""
import pytest
from fastapi.testclient import TestClient
import psycopg2
from psycopg2.extras import RealDictCursor
from app.main import app
from app.core.database import get_db
from app.core.config import settings

# Test database URL (uses same docker postgres)
TEST_DATABASE_URL = settings.DATABASE_URL


def get_test_db_connection():
    """Get test database connection."""
    conn = psycopg2.connect(TEST_DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


@pytest.fixture
def db_connection():
    """Create a fresh database for each test."""
    conn = get_test_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            author_id UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            author_id UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    conn.commit()
    
    try:
        yield conn
    finally:
        # Clean up tables after test
        cursor.execute("DROP TABLE IF EXISTS comments CASCADE")
        cursor.execute("DROP TABLE IF EXISTS posts CASCADE")
        cursor.execute("DROP TABLE IF EXISTS users CASCADE")
        conn.commit()
        conn.close()


@pytest.fixture
def client(db_connection):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_connection
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
