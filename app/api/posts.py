"""Post endpoints - MOCK IMPLEMENTATION.

Phase 0: Returns hardcoded mock responses.
Phase 2: Will implement real CRUD operations with database.
"""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import require_auth
from app.schemas.posts import (
    CreatePostRequest,
    PostListResponse,
    PostResponse,
    UpdatePostRequest,
)

router = APIRouter(prefix="/api/posts", tags=["Posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    current_user: dict[str, str] = Depends(require_auth),
) -> PostResponse:
    """Create a new blog post - MOCK IMPLEMENTATION.
    
    Args:
        request: Post creation details
        current_user: Current authenticated user
        
    Returns:
        Mock post response
    """
    return PostResponse(
        post_id="mock-post-456",
        title=request.title,
        content=request.content,
        author_id=current_user["user_id"],
        author_username=current_user["username"],
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        published=request.published,
        tags=request.tags or [],
    )


@router.get("", response_model=PostListResponse)
async def list_posts(
    page: int = 1,
    page_size: int = 20,
) -> PostListResponse:
    """List all blog posts with pagination - MOCK IMPLEMENTATION.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of posts per page
        
    Returns:
        Mock paginated post list
    """
    mock_posts = [
        PostResponse(
            post_id=f"mock-post-{i}",
            title=f"Mock Post {i}",
            content=f"This is mock post content {i}",
            author_id="mock-user-123",
            author_username="mockuser",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            published=True,
            tags=["python", "fastapi"],
        )
        for i in range(1, 4)
    ]
    
    return PostListResponse(
        posts=mock_posts,
        total=3,
        page=page,
        page_size=page_size,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str) -> PostResponse:
    """Get a single blog post by ID - MOCK IMPLEMENTATION.
    
    Args:
        post_id: Post ID
        
    Returns:
        Mock post response
    """
    return PostResponse(
        post_id=post_id,
        title="Mock Post Title",
        content="This is mock post content with more details.",
        author_id="mock-user-123",
        author_username="mockuser",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        published=True,
        tags=["python", "fastapi", "tutorial"],
    )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    request: UpdatePostRequest,
    current_user: dict[str, str] = Depends(require_auth),
) -> PostResponse:
    """Update a blog post - MOCK IMPLEMENTATION.
    
    Args:
        post_id: Post ID to update
        request: Updated post details
        current_user: Current authenticated user
        
    Returns:
        Mock updated post response
    """
    return PostResponse(
        post_id=post_id,
        title=request.title or "Updated Mock Title",
        content=request.content or "Updated mock content",
        author_id=current_user["user_id"],
        author_username=current_user["username"],
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-02T00:00:00Z",
        published=request.published if request.published is not None else True,
        tags=request.tags or ["updated"],
    )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: dict[str, str] = Depends(require_auth),
) -> None:
    """Delete a blog post - MOCK IMPLEMENTATION.
    
    Args:
        post_id: Post ID to delete
        current_user: Current authenticated user
    """
    pass
