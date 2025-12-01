"""
Comments API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.modules.comments.services.comment_service import CommentService

router = APIRouter()


class CreateCommentRequest(BaseModel):
    """Create comment request."""
    content: str
    authorId: str


class CommentResponse(BaseModel):
    """Comment response."""
    commentId: str
    postId: str
    content: str
    authorId: str
    createdAt: str


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: str,
    request: CreateCommentRequest,
    conn = Depends(get_db)
):
    """
    Create a new comment on a post.
    
    Args:
        post_id: Post ID
        request: Comment creation details
        conn: Database connection
        
    Returns:
        CommentResponse: Created comment details
    """
    try:
        comment_service = CommentService(conn)
        comment = comment_service.create_comment(
            post_id=post_id,
            content=request.content,
            author_id=request.authorId
        )
        
        return CommentResponse(
            commentId=str(comment["id"]),
            postId=str(comment["post_id"]),
            content=comment["content"],
            authorId=str(comment["author_id"]),
            createdAt=comment["created_at"].isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def list_comments(post_id: str, conn = Depends(get_db)):
    """
    List all comments for a post.
    
    Args:
        post_id: Post ID
        conn: Database connection
        
    Returns:
        List[CommentResponse]: List of comments
    """
    try:
        comment_service = CommentService(conn)
        comments = comment_service.list_comments_by_post(post_id)
        
        return [
            CommentResponse(
                commentId=str(comment["id"]),
                postId=str(comment["post_id"]),
                content=comment["content"],
                authorId=str(comment["author_id"]),
                createdAt=comment["created_at"].isoformat()
            )
            for comment in comments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
