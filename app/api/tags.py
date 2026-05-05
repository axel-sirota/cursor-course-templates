"""Tag endpoints - MOCK IMPLEMENTATION.

Phase 0: Returns hardcoded mock responses.
Phase 4: Will implement real tag operations with database.
"""

from fastapi import APIRouter

from app.schemas.posts import PostResponse
from app.schemas.tags import TagPostsResponse, TagResponse

router = APIRouter(prefix="/api/tags", tags=["Tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags() -> list[TagResponse]:
    """List all tags with post counts - MOCK IMPLEMENTATION.
    
    Returns:
        Mock list of tags
    """
    return [
        TagResponse(tag_id="mock-tag-001", name="python", post_count=10),
        TagResponse(tag_id="mock-tag-002", name="fastapi", post_count=8),
        TagResponse(tag_id="mock-tag-003", name="tutorial", post_count=5),
    ]


@router.get("/{tag_name}/posts", response_model=TagPostsResponse)
async def get_posts_by_tag(tag_name: str) -> TagPostsResponse:
    """Get all posts with a specific tag - MOCK IMPLEMENTATION.
    
    Args:
        tag_name: Tag name to filter by
        
    Returns:
        Mock posts filtered by tag
    """
    mock_posts = [
        PostResponse(
            post_id=f"mock-post-{i}",
            title=f"Post about {tag_name} #{i}",
            content=f"Content related to {tag_name}",
            author_id="mock-user-123",
            author_username="mockuser",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            published=True,
            tags=[tag_name, "tutorial"],
        )
        for i in range(1, 3)
    ]
    
    return TagPostsResponse(
        tag=tag_name,
        posts=mock_posts,
        total=2,
    )
