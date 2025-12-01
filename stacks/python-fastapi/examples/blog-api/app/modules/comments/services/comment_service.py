"""
Comment Service Layer - Uses Raw SQL
"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CommentService:
    """Service for comment operations using raw SQL."""
    
    def __init__(self, conn):
        """
        Initialize comment service with database connection.
        
        Args:
            conn: psycopg2 database connection
        """
        self.conn = conn
    
    def create_comment(self, post_id: str, content: str, author_id: str) -> Dict[str, Any]:
        """
        Create a new comment on a post.
        
        Args:
            post_id: Post ID
            content: Comment content
            author_id: Author's user ID
            
        Returns:
            Dict: Created comment record
            
        Raises:
            ValueError: If validation fails or post not found
        """
        # Validate content
        if not content or len(content.strip()) == 0:
            raise ValueError("Content cannot be empty")
        
        cursor = self.conn.cursor()
        
        # Verify post exists
        cursor.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        
        if not post:
            raise ValueError(f"Post with ID {post_id} not found")
        
        # Create comment
        cursor.execute(
            """
            INSERT INTO comments (post_id, content, author_id)
            VALUES (%s, %s, %s)
            RETURNING id, post_id, content, author_id, created_at
            """,
            (post_id, content.strip(), author_id)
        )
        
        comment = cursor.fetchone()
        logger.info(f"Created comment: {comment['id']} on post: {post_id}")
        
        return dict(comment)
    
    def list_comments_by_post(self, post_id: str) -> List[Dict[str, Any]]:
        """
        List all comments for a post.
        
        Args:
            post_id: Post ID
            
        Returns:
            List[Dict]: List of comments ordered by creation date
        """
        cursor = self.conn.cursor()
        
        cursor.execute(
            """
            SELECT id, post_id, content, author_id, created_at
            FROM comments
            WHERE post_id = %s
            ORDER BY created_at ASC
            """,
            (post_id,)
        )
        
        comments = cursor.fetchall()
        return [dict(comment) for comment in comments]
