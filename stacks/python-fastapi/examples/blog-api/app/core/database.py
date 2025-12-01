"""
Database Configuration and Connection Management
Uses raw SQL with psycopg2 (not SQLAlchemy)
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.core.config import settings
from typing import Generator
import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    Get database connection context manager.
    
    Yields:
        connection: psycopg2 connection with RealDictCursor
    """
    conn = None
    try:
        conn = psycopg2.connect(
            settings.DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_db():
    """
    FastAPI dependency for database connection.
    
    Yields:
        connection: Database connection
    """
    with get_db_connection() as conn:
        yield conn


def init_db():
    """Initialize database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create index on username
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username)
        """)
        
        # Create posts table
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
        
        # Create indexes on posts
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_author_id 
            ON posts(author_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_created_at 
            ON posts(created_at)
        """)
        
        # Create comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                author_id UUID NOT NULL REFERENCES users(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create indexes on comments
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_post_id 
            ON comments(post_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_author_id 
            ON comments(author_id)
        """)
        
        conn.commit()
        logger.info("Database tables initialized successfully")
