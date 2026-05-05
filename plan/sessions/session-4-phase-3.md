# Session 4: Phase 3 - Comments

## Goal
Implement comment functionality allowing users to comment on blog posts with proper nesting, cascade deletes, and authorization.

## Prerequisites
- ✅ Phase 2 posts CRUD complete
- ✅ Posts can be created and retrieved
- ✅ Authentication working
- ✅ Authorization pattern established (author-only deletes)

## LLM Implementation Instructions

This session adds nested resources (comments under posts). Key patterns:
1. Verify parent resource (post) exists before creating child (comment)
2. Use cascade deletes (when post deleted, comments auto-delete)
3. Join queries to include author username
4. RESTful nested routes: `POST /api/posts/{post_id}/comments`

## Implementation Tasks

### 1. Database Models
Create `app/models/comment.py`:

```python
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Comment(Base):
    """Comment database model."""
    
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    
    # Indexes
    __table_args__ = (
        Index("idx_comments_post", "post_id"),
        Index("idx_comments_author", "author_id"),
    )
```

**Important**: Update related models:

`app/models/post.py`:
```python
# Add to Post model
comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
```

`app/models/user.py`:
```python
# Add to User model
comments = relationship("Comment", back_populates="author")
```

### 2. Database Migration
```bash
alembic revision -m "Create comments table"
# Edit migration to create table with foreign keys and indexes
alembic upgrade head
```

**Migration must include:**
- `comments` table with all columns
- Foreign key to `posts.id` with ON DELETE CASCADE
- Foreign key to `users.id` with ON DELETE CASCADE
- Indexes on `post_id` and `author_id`

### 3. Repository Layer
Create `app/repositories/comment_repository.py`:
- `create_comment(post_id, author_id, content)` → Comment
- `list_comments_by_post(post_id)` → List[Comment]
- `get_comment_by_id(comment_id)` → Comment | None
- `delete_comment(comment_id)` → bool

### 4. Service Layer
Create `app/services/comment_service.py`:

```python
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.comment_repository import CommentRepository
from app.repositories.post_repository import PostRepository
from app.schemas.comments import CommentResponse


class CommentService:
    """Business logic for comments."""
    
    def __init__(self, db: AsyncSession):
        self.comment_repo = CommentRepository(db)
        self.post_repo = PostRepository(db)
    
    async def add_comment(
        self, 
        post_id: str, 
        author_id: str, 
        content: str
    ) -> CommentResponse:
        """Add comment to post. Verifies post exists first."""
        # CRITICAL: Verify post exists
        post = await self.post_repo.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post {post_id} not found"
            )
        
        comment = await self.comment_repo.create_comment(post_id, author_id, content)
        return CommentResponse.model_validate(comment)
    
    async def list_comments(self, post_id: str) -> list[CommentResponse]:
        """List all comments for a post."""
        comments = await self.comment_repo.list_comments_by_post(post_id)
        return [CommentResponse.model_validate(c) for c in comments]
    
    async def delete_comment(self, comment_id: str, user_id: str) -> None:
        """Delete comment. Only author can delete."""
        comment = await self.comment_repo.get_comment_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment {comment_id} not found"
            )
        
        # Authorization check
        if str(comment.author_id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment"
            )
        
        await self.comment_repo.delete_comment(comment_id)
```

**Key business rules:**
1. Cannot comment on non-existent post → 404
2. Only comment author can delete → 403
3. When post deleted, comments cascade delete automatically

### 5. Update API Routes
Replace mock implementations in `app/api/comments.py`:
- POST /api/posts/{post_id}/comments → Add comment (authenticated)
- GET /api/posts/{post_id}/comments → List comments for post (public)
- DELETE /api/comments/{comment_id} → Delete comment (author only)

### 6. Authorization Logic
- Only comment author can delete their comment
- Return 403 Forbidden if not authorized
- Verify post exists before adding comment (404 if not found)

### 7. Join User Data
- Include author username in comment responses
- Use SQLAlchemy relationships to join User data

### 8. E2E Tests
Create `tests/api/test_comments.py`:
- Test add comment to existing post
- Test add comment to non-existent post (404)
- Test list comments for post
- Test delete own comment (success)
- Test delete other user's comment (403)
- Test comment without auth (401)

## Verification Steps
1. Create post as user A
2. Add comment to post as user B
3. List comments for post
4. Delete comment as user B (success)
5. Try to delete comment as user A (should fail if not author)

## Acceptance Criteria

### Database Layer
- [ ] Comment model created with all fields
- [ ] Foreign keys to Post and User with CASCADE delete
- [ ] Alembic migration applied
- [ ] Indexes created on post_id and author_id
- [ ] Cascade delete works (deleting post removes comments)

### Repository Layer
- [ ] CommentRepository implements all methods async
- [ ] `create_comment` inserts into database
- [ ] `list_comments_by_post` returns all comments for post
- [ ] `list_comments_by_post` includes author username (join)
- [ ] `get_comment_by_id` returns None for non-existent
- [ ] `delete_comment` removes from database

### Service Layer
- [ ] Service verifies post exists before creating comment
- [ ] Returns 404 if commenting on non-existent post
- [ ] Only comment author can delete (403 otherwise)
- [ ] Service converts DB models to response schemas

### API Layer
- [ ] POST /api/posts/{post_id}/comments creates comment
- [ ] Returns 404 if post doesn't exist
- [ ] GET /api/posts/{post_id}/comments lists comments
- [ ] DELETE /api/comments/{comment_id} deletes comment
- [ ] Returns 403 if not comment author
- [ ] Comments include author username in response

### Testing
- [ ] Can add comment to existing post
- [ ] Returns 404 when commenting on non-existent post
- [ ] Can list all comments for post
- [ ] Comments include author username
- [ ] Can delete own comment
- [ ] Returns 403 when trying to delete other user's comment
- [ ] Comments auto-delete when post deleted (cascade)
- [ ] All 4+ comment E2E tests pass

## Troubleshooting

### Common Issues

**"Post not found" for valid post_id**
- Verify post_id is UUID, not string
- Check post exists: `await post_repo.get_post_by_id(post_id)`

**Comments missing author username**
- Use join in repository: `.join(User).options(selectinload(Comment.author))`
- Or: Access `comment.author.username` in response serialization

**Comments not deleted when post deleted**
- Ensure `ondelete="CASCADE"` in ForeignKey
- Check migration has `ON DELETE CASCADE` constraint
- Verify in database: `\d comments` should show CASCADE

**403 on own comment deletion**
- Convert UUIDs to strings for comparison: `str(comment.author_id) == user_id`

## Anti-Patterns to Avoid

**❌ BAD - Not verifying post exists:**
```python
async def add_comment(post_id, author_id, content):
    # What if post_id doesn't exist?
    return await repo.create_comment(post_id, author_id, content)
```

**✅ GOOD - Verify first:**
```python
async def add_comment(post_id, author_id, content):
    post = await post_repo.get_post_by_id(post_id)
    if not post:
        raise HTTPException(404, detail="Post not found")
    return await repo.create_comment(post_id, author_id, content)
```

**❌ BAD - N+1 query for author:**
```python
comments = await repo.list_comments_by_post(post_id)
for comment in comments:
    user = await user_repo.get_user_by_id(comment.author_id)  # N queries!
    comment.author_username = user.username
```

**✅ GOOD - Join in query:**
```python
# In repository
query = select(Comment).join(User).where(Comment.post_id == post_id)
query = query.options(selectinload(Comment.author))
```

**❌ BAD - Manual cascade delete:**
```python
# Don't do this manually
post = await repo.get_post(post_id)
comments = await repo.list_comments_by_post(post_id)
for comment in comments:
    await repo.delete_comment(comment.id)  # Unnecessary!
await repo.delete_post(post_id)
```

**✅ GOOD - Let database handle cascade:**
```python
# Just delete the post, comments delete automatically
await repo.delete_post(post_id)
# Cascade happens automatically via ON DELETE CASCADE
```

## Verification Steps

1. **Test comment creation:**
```bash
# Create post first
POST /api/posts {"title": "Test", "content": "Content"}
# Get post_id from response

# Add comment
POST /api/posts/{post_id}/comments {"content": "Great post!"}
```

2. **Test cascade delete:**
```bash
# Count comments: SELECT COUNT(*) FROM comments WHERE post_id = 'xxx';
# Delete post: DELETE /api/posts/{post_id}
# Count again: SELECT COUNT(*) FROM comments WHERE post_id = 'xxx';
# Should be 0
```

3. **Test authorization:**
```bash
# User A creates comment, gets comment_id
# User B tries to delete: DELETE /api/comments/{comment_id}
# Should return 403
```

## Session Completion

When complete:
1. Run tests: `pytest tests/ -v`
2. Test manually via `/docs`
3. Verify cascade: Delete a post, check comments table
4. Create session summary
5. Commit: `git commit -m "feat: implement comments (Phase 3)"`

## Next Session
Session 5 will implement Phase 4 (Tags) with many-to-many relationships.

## Session Duration
Estimated: 60-75 minutes
