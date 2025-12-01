"""
Posts API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.modules.posts.services.post_service import PostService

router = APIRouter()


class CreatePostRequest(BaseModel):
    """Create post request."""
    title: str
    content: str
    authorId: str


class PostResponse(BaseModel):
    """Post response."""
    postId: str
    title: str
    content: str
    authorId: str
    createdAt: str
    updatedAt: Optional[str] = None


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(request: CreatePostRequest, conn = Depends(get_db)):
    """
    Create a new blog post.
    
    Args:
        request: Post creation details
        conn: Database connection
        
    Returns:
        PostResponse: Created post details
    """
    try:
        post_service = PostService(conn)
        post = post_service.create_post(
            title=request.title,
            content=request.content,
            author_id=request.authorId
        )
        
        return PostResponse(
            postId=str(post["id"]),
            title=post["title"],
            content=post["content"],
            authorId=str(post["author_id"]),
            createdAt=post["created_at"].isoformat(),
            updatedAt=post["updated_at"].isoformat() if post.get("updated_at") else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, conn = Depends(get_db)):
    """
    Get a blog post by ID.
    
    Args:
        post_id: Post ID
        conn: Database connection
        
    Returns:
        PostResponse: Post details
    """
    try:
        post_service = PostService(conn)
        post = post_service.get_post_by_id(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return PostResponse(
            postId=str(post["id"]),
            title=post["title"],
            content=post["content"],
            authorId=str(post["author_id"]),
            createdAt=post["created_at"].isoformat(),
            updatedAt=post["updated_at"].isoformat() if post.get("updated_at") else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
