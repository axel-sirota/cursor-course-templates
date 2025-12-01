"""
User Service Layer - Uses Raw SQL
"""
import hashlib
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations using raw SQL."""
    
    def __init__(self, conn):
        """
        Initialize user service with database connection.
        
        Args:
            conn: psycopg2 database connection
        """
        self.conn = conn
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA256.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Dict: Created user record
            
        Raises:
            ValueError: If username already exists
        """
        cursor = self.conn.cursor()
        
        # Check if username exists
        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            (username,)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            raise ValueError(f"Username '{username}' already exists")
        
        # Create new user
        password_hash = self._hash_password(password)
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            RETURNING id, username, created_at
            """,
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        logger.info(f"Created user: {username}")
        
        return dict(user)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Dict: Authenticated user or None if invalid
        """
        cursor = self.conn.cursor()
        
        password_hash = self._hash_password(password)
        cursor.execute(
            """
            SELECT id, username, created_at
            FROM users
            WHERE username = %s AND password_hash = %s
            """,
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        
        if user:
            logger.info(f"User authenticated: {username}")
            return dict(user)
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: User or None if not found
        """
        cursor = self.conn.cursor()
        
        cursor.execute(
            """
            SELECT id, username, created_at
            FROM users
            WHERE id = %s
            """,
            (user_id,)
        )
        
        user = cursor.fetchone()
        return dict(user) if user else None
