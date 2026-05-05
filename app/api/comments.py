"""Comment endpoints - MOCK IMPLEMENTATION.

Phase 0: Returns hardcoded mock responses.
Phase 3: Will implement real comment operations with database.
"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import require_auth
from app.schemas.comments import CommentResponse, CreateCommentRequest

router = APIRouter(prefix="/api", tags=["Comments"])


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    post_id: str,
    request: CreateCommentRequest,
    current_user: dict[str, str] = Depends(require_auth),
) -> CommentResponse:
    """Add a comment to a blog post - MOCK IMPLEMENTATION.
    
    Args:
        post_id: Post ID to comment on
        request: Comment content
        current_user: Current authenticated user
        
    Returns:
        Mock comment response
    """
    return CommentResponse(
        comment_id="mock-comment-789",
        post_id=post_id,
        author_id=current_user["user_id"],
        author_username=current_user["username"],
        content=request.content,
        created_at="2024-01-01T00:00:00Z",
    )


@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
async def list_comments(post_id: str) -> list[CommentResponse]:
    """List all comments for a blog post - MOCK IMPLEMENTATION.
    
    Args:
        post_id: Post ID
        
    Returns:
        Mock list of comments
    """
    return [
        CommentResponse(
            comment_id=f"mock-comment-{i}",
            post_id=post_id,
            author_id="mock-user-123",
            author_username="mockuser",
            content=f"This is mock comment {i}",
            created_at="2024-01-01T00:00:00Z",
        )
        for i in range(1, 3)
    ]


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: dict[str, str] = Depends(require_auth),
) -> None:
    """Delete a comment - MOCK IMPLEMENTATION.
    
    Args:
        comment_id: Comment ID to delete
        current_user: Current authenticated user
    """
    pass
