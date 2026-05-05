# Session 5: Phase 4 - Tags

## Goal
Implement tag functionality with many-to-many relationships, tag normalization, and aggregate queries for post counts.

## Prerequisites
- ✅ Phase 3 comments complete
- ✅ Posts and comments working
- ✅ Understanding of many-to-many relationships
- ✅ JOIN queries familiar

## LLM Implementation Instructions

This session implements many-to-many relationships using a junction table. Key patterns:
1. Junction table: `post_tags` (post_id, tag_id) with composite primary key
2. Get-or-create pattern for tags (avoid duplicates)
3. Tag normalization: lowercase + trim whitespace
4. Aggregate queries: COUNT posts per tag
5. Update existing Post endpoints to include/handle tags

**SQLAlchemy many-to-many requires:**
- Junction table model OR Table() definition
- `relationship()` with `secondary=` parameter
- Handle both sides: Post.tags and Tag.posts

## Implementation Tasks

### 1. Database Models
Create `app/models/tag.py`:

```python
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


# Junction table for many-to-many relationship
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Index("idx_post_tags_post", "post_id"),
    Index("idx_post_tags_tag", "tag_id"),
)


class Tag(Base):
    """Tag database model."""
    
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Many-to-many relationship
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
```

**Update `app/models/post.py`:**
```python
from app.models.tag import post_tags

# Add to Post model
tags = relationship("Tag", secondary=post_tags, back_populates="posts")
```

### 2. Database Migration
```bash
alembic revision -m "Create tags and post_tags tables"
# Edit migration to create both tables
alembic upgrade head
```

**Migration must create:**
- `tags` table (id, name UNIQUE, created_at)
- `post_tags` junction table (post_id, tag_id) with composite PK
- Foreign keys with CASCADE delete
- Indexes on both columns of junction table

### 3. Tag Normalization Utility
Create `app/core/utils.py`:

```python
def normalize_tag_name(name: str) -> str:
    """Normalize tag name: lowercase and trim whitespace.
    
    Examples:
        "Python" -> "python"
        "  FastAPI  " -> "fastapi"
        "WEB-Dev" -> "web-dev"
    """
    if not name:
        raise ValueError("Tag name cannot be empty")
    
    normalized = name.strip().lower()
    
    if not normalized:
        raise ValueError("Tag name cannot be only whitespace")
    
    # Optional: validate characters (alphanumeric + hyphens only)
    if not all(c.isalnum() or c in ("-", "_") for c in normalized):
        raise ValueError("Tag name can only contain letters, numbers, hyphens, and underscores")
    
    return normalized
```

### 4. Repository Layer
Create `app/repositories/tag_repository.py`:

```python
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import Post
from app.models.tag import Tag, post_tags
from app.core.utils import normalize_tag_name


class TagRepository:
    """Data access layer for tags."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_tag(self, name: str) -> Tag:
        """Get existing tag or create new one. Names are normalized."""
        normalized_name = normalize_tag_name(name)
        
        # Try to get existing
        query = select(Tag).where(Tag.name == normalized_name)
        result = await self.db.execute(query)
        tag = result.scalar_one_or_none()
        
        if tag:
            return tag
        
        # Create new
        tag = Tag(name=normalized_name)
        self.db.add(tag)
        await self.db.flush()  # Get ID without committing
        return tag
    
    async def list_all_tags(self) -> list[tuple[Tag, int]]:
        """List all tags with post counts.
        
        Returns:
            List of (Tag, post_count) tuples
        """
        query = (
            select(Tag, func.count(post_tags.c.post_id).label("post_count"))
            .outerjoin(post_tags, Tag.id == post_tags.c.tag_id)
            .group_by(Tag.id)
            .order_by(func.count(post_tags.c.post_id).desc())
        )
        result = await self.db.execute(query)
        return result.all()
    
    async def get_posts_by_tag(self, tag_name: str) -> list[Post]:
        """Get all posts with a specific tag."""
        normalized_name = normalize_tag_name(tag_name)
        
        query = (
            select(Post)
            .join(post_tags, Post.id == post_tags.c.post_id)
            .join(Tag, Tag.id == post_tags.c.tag_id)
            .where(Tag.name == normalized_name)
            .options(selectinload(Post.tags))  # Load tags for each post
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def add_tags_to_post(self, post: Post, tag_names: list[str]) -> None:
        """Add tags to a post. Creates tags if they don't exist."""
        # Clear existing tags
        post.tags.clear()
        
        # Add new tags
        for tag_name in tag_names:
            tag = await self.get_or_create_tag(tag_name)
            post.tags.append(tag)
        
        await self.db.flush()
    
    async def get_tags_for_post(self, post_id: str) -> list[Tag]:
        """Get all tags for a post."""
        query = (
            select(Tag)
            .join(post_tags, Tag.id == post_tags.c.tag_id)
            .where(post_tags.c.post_id == post_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
```

### 5. Update Post Service
Modify `app/services/post_service.py` to handle tags:

```python
# Add to PostService.__init__
from app.repositories.tag_repository import TagRepository

def __init__(self, db: AsyncSession):
    self.post_repo = PostRepository(db)
    self.tag_repo = TagRepository(db)  # Add this
    self.db = db

# Update create_post method
async def create_post(
    self, 
    title: str, 
    content: str, 
    author_id: str, 
    published: bool = True,
    tags: list[str] | None = None  # Add this parameter
) -> PostResponse:
    """Create a new post with optional tags."""
    post = await self.post_repo.create_post(title, content, author_id, published)
    
    # Add tags if provided
    if tags:
        await self.tag_repo.add_tags_to_post(post, tags)
        await self.db.commit()
        await self.db.refresh(post)
    
    # Convert to response (will include tags via relationship)
    return PostResponse.model_validate(post)

# Update update_post method similarly
```

### 6. Create Tag API Routes
Create `app/api/tags.py` (replace mock implementation):

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.tags import TagResponse, TagPostsResponse
from app.services.tag_service import TagService

router = APIRouter(prefix="/api/tags", tags=["Tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)) -> list[TagResponse]:
    """List all tags with post counts."""
    service = TagService(db)
    return await service.list_all_tags()


@router.get("/{tag_name}/posts", response_model=TagPostsResponse)
async def get_posts_by_tag(
    tag_name: str,
    db: AsyncSession = Depends(get_db)
) -> TagPostsResponse:
    """Get all posts with a specific tag."""
    service = TagService(db)
    return await service.get_posts_by_tag(tag_name)
```

### 7. Update Post Schemas
Modify `app/schemas/posts.py`:

```python
class CreatePostRequest(BaseModel):
    title: str
    content: str
    tags: list[str] | None = None  # Add this
    published: bool = True

class UpdatePostRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None  # Add this
    published: bool | None = None

class PostResponse(BaseModel):
    # ... existing fields ...
    tags: list[str] = Field(default_factory=list)  # Add this
    
    @classmethod
    def from_orm_with_tags(cls, post: Post) -> "PostResponse":
        """Convert Post model to response, extracting tag names."""
        return cls(
            post_id=str(post.id),
            # ... other fields ...
            tags=[tag.name for tag in post.tags],
        )
```

### 8. E2E Tests
Create `tests/api/test_tags_real.py`:

```python
import pytest
from fastapi.testclient import TestClient


def test_create_post_with_tags(client: TestClient, auth_headers: dict):
    """Test creating a post with tags."""
    response = client.post(
        "/api/posts",
        headers=auth_headers,
        json={
            "title": "Python Tutorial",
            "content": "Learn Python",
            "tags": ["python", "tutorial", "beginner"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert set(data["tags"]) == {"python", "tutorial", "beginner"}


def test_tags_are_normalized(client: TestClient, auth_headers: dict):
    """Test that tag names are normalized (lowercase, trimmed)."""
    response = client.post(
        "/api/posts",
        headers=auth_headers,
        json={
            "title": "Test",
            "content": "Content",
            "tags": ["  Python  ", "FASTAPI", "Web-Dev"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert set(data["tags"]) == {"python", "fastapi", "web-dev"}


def test_duplicate_tags_prevented(client: TestClient, auth_headers: dict):
    """Test that duplicate tags (after normalization) are merged."""
    # Create first post with "python" tag
    client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Post 1", "content": "Content", "tags": ["python"]},
    )
    
    # Create second post with "Python" tag (should use same tag)
    client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Post 2", "content": "Content", "tags": ["Python"]},
    )
    
    # Check tags list - should only have one "python" tag
    response = client.get("/api/tags")
    assert response.status_code == 200
    tags = response.json()
    python_tags = [t for t in tags if t["name"] == "python"]
    assert len(python_tags) == 1
    assert python_tags[0]["postCount"] == 2


def test_list_all_tags(client: TestClient, auth_headers: dict):
    """Test listing all tags with post counts."""
    # Create posts with tags
    client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Post 1", "content": "C1", "tags": ["python", "fastapi"]},
    )
    client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Post 2", "content": "C2", "tags": ["python"]},
    )
    
    # List tags
    response = client.get("/api/tags")
    assert response.status_code == 200
    tags = response.json()
    
    python_tag = next(t for t in tags if t["name"] == "python")
    assert python_tag["postCount"] == 2
    
    fastapi_tag = next(t for t in tags if t["name"] == "fastapi")
    assert fastapi_tag["postCount"] == 1


def test_get_posts_by_tag(client: TestClient, auth_headers: dict):
    """Test filtering posts by tag."""
    # Create posts
    r1 = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Python Post", "content": "C1", "tags": ["python"]},
    )
    r2 = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Go Post", "content": "C2", "tags": ["golang"]},
    )
    
    # Get posts by "python" tag
    response = client.get("/api/tags/python/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["tag"] == "python"
    assert len(data["posts"]) == 1
    assert data["posts"][0]["title"] == "Python Post"


def test_update_post_tags(client: TestClient, auth_headers: dict):
    """Test updating post tags."""
    # Create post
    r = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Post", "content": "C", "tags": ["python"]},
    )
    post_id = r.json()["postId"]
    
    # Update tags
    response = client.put(
        f"/api/posts/{post_id}",
        headers=auth_headers,
        json={"tags": ["golang", "backend"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert set(data["tags"]) == {"golang", "backend"}
    
    # Verify old tag removed
    response = client.get(f"/api/posts/{post_id}")
    assert "python" not in response.json()["tags"]
```

## Acceptance Criteria

### Database Layer
- [ ] Tag model created with unique name constraint
- [ ] post_tags junction table created with composite PK
- [ ] Foreign keys with CASCADE delete
- [ ] Indexes on both columns of junction table
- [ ] Alembic migration applied successfully
- [ ] Many-to-many relationship accessible from both sides

### Tag Normalization
- [ ] Tag names converted to lowercase
- [ ] Whitespace trimmed from tag names
- [ ] "Python" and "python" treated as same tag
- [ ] Empty/whitespace-only names rejected
- [ ] Invalid characters rejected (optional)

### Repository Layer
- [ ] `get_or_create_tag` returns existing or creates new
- [ ] `list_all_tags` returns tags with counts
- [ ] `get_posts_by_tag` filters by normalized name
- [ ] `add_tags_to_post` handles tag creation
- [ ] `add_tags_to_post` replaces existing tags

### Service/API Layer
- [ ] POST /api/posts accepts tags array
- [ ] PUT /api/posts accepts tags array
- [ ] GET /api/posts includes tags in response
- [ ] GET /api/posts/{id} includes tags
- [ ] GET /api/tags returns all tags with counts
- [ ] GET /api/tags/{name}/posts filters posts

### Testing
- [ ] Can create post with tags
- [ ] Tags are normalized correctly
- [ ] Duplicate tags (different case) merged
- [ ] Can list all tags with counts
- [ ] Can filter posts by tag
- [ ] Can update post tags
- [ ] Old tags removed when updating
- [ ] All 6+ tag E2E tests pass

## Troubleshooting

### Common Issues

**"Could not locate table 'post_tags'"**
- Ensure junction table defined before Tag model
- Import order: base → post_tags Table() → Tag model

**"Tags not loading with post"**
- Use `options(selectinload(Post.tags))` in query
- Or access `post.tags` and let lazy loading work (but prefer eager loading)

**"Duplicate tags created"**
- Ensure using `get_or_create_tag` pattern
- Verify tag name normalization applied before lookup

**"Tags not removed when updating"**
- Call `post.tags.clear()` before adding new tags
- Ensure session.commit() called

## Anti-Patterns to Avoid

**❌ BAD - Case-sensitive tag matching:**
```python
tag = await session.execute(select(Tag).where(Tag.name == name))  # "Python" != "python"
```

**✅ GOOD - Normalize first:**
```python
normalized = normalize_tag_name(name)
tag = await session.execute(select(Tag).where(Tag.name == normalized))
```

**❌ BAD - Creating duplicate tags:**
```python
tag = Tag(name=name)
session.add(tag)  # Might already exist!
```

**✅ GOOD - Get or create:**
```python
tag = await get_or_create_tag(name)
```

**❌ BAD - N+1 queries for tag names:**
```python
posts = await get_posts()
for post in posts:
    tags = await get_tags_for_post(post.id)  # N queries!
```

**✅ GOOD - Eager load:**
```python
query = select(Post).options(selectinload(Post.tags))
posts = await session.execute(query)
```

**❌ BAD - Manual junction table management:**
```python
# Don't manually insert into post_tags!
await session.execute(insert(post_tags).values(post_id=p_id, tag_id=t_id))
```

**✅ GOOD - Use relationship:**
```python
post.tags.append(tag)  # SQLAlchemy handles junction table
```

## Session Completion

When complete:
1. Run tests: `pytest tests/ -v`
2. Test manually via `/docs`
3. Verify normalization: Create posts with "Python" and "python", check tags list
4. Verify counts: Check post_count in GET /api/tags
5. Create session summary
6. Commit: `git commit -m "feat: implement tags with many-to-many (Phase 4)"`

## Next Session
Session 6 will implement Phase 5 (Polish & Deploy) with production features.

## Session Duration
Estimated: 75-90 minutes
