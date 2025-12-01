"""
Post Service Layer - Uses Raw SQL
"""
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PostService:
    """Service for post operations using raw SQL."""
    
    def __init__(self, conn):
        """
        Initialize post service with database connection.
        
        Args:
            conn: psycopg2 database connection
        """
        self.conn = conn
    
    def create_post(self, title: str, content: str, author_id: str) -> Dict[str, Any]:
        """
        Create a new post.
        
        Args:
            title: Post title
            content: Post content
            author_id: Author's user ID
            
        Returns:
            Dict: Created post record
            
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        if not title or len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        
        if not content or len(content.strip()) == 0:
            raise ValueError("Content cannot be empty")
        
        cursor = self.conn.cursor()
        
        # Create post
        cursor.execute(
            """
            INSERT INTO posts (title, content, author_id)
            VALUES (%s, %s, %s)
            RETURNING id, title, content, author_id, created_at, updated_at
            """,
            (title.strip(), content.strip(), author_id)
        )
        
        post = cursor.fetchone()
        logger.info(f"Created post: {post['id']}")
        
        return dict(post)
    
    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Get post by ID.
        
        Args:
            post_id: Post ID
            
        Returns:
            Dict: Post or None if not found
        """
        cursor = self.conn.cursor()
        
        cursor.execute(
            """
            SELECT id, title, content, author_id, created_at, updated_at
            FROM posts
            WHERE id = %s
            """,
            (post_id,)
        )
        
        post = cursor.fetchone()
        return dict(post) if post else None
