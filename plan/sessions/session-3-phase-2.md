# Session 3: Phase 2 - Posts CRUD

## Goal
Implement full CRUD operations for blog posts with database persistence, authorization, and proper layering (Route → Service → Repository).

## Prerequisites
- ✅ Phase 1 authentication complete
- ✅ User registration and login working
- ✅ JWT authentication dependency working
- ✅ Alembic initialized and users table created
- ✅ Database connection working

## LLM Implementation Instructions

This session implements the Repository + Service pattern. Follow this order:
1. Database Model → 2. Migration → 3. Repository → 4. Service → 5. API Routes → 6. Tests

Always use async/await throughout. All database operations must be async.

## Implementation Tasks

### 1. Database Models
Create `app/models/post.py`:

```python
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Post(Base):
    """Post database model."""
    
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    
    # Indexes
    __table_args__ = (
        Index("idx_posts_author", "author_id"),
        Index("idx_posts_created", "created_at"),
    )
```

**Important**: Also update `app/models/user.py` to add the back relationship:
```python
# Add to User model
posts = relationship("Post", back_populates="author")
```

### 2. Database Migration
Create and run migration:

```bash
# Generate migration
alembic revision -m "Create posts table"

# Manually edit the migration file to add:
# - Table creation
# - Foreign key constraint
# - Indexes

# Run migration
alembic upgrade head

# Verify in database
psql $DATABASE_URL -c "\d posts"
```

**Migration file should create:**
- `posts` table with all columns
- Foreign key to `users.id` with ON DELETE CASCADE
- Index on `author_id`
- Index on `created_at DESC`

### 3. Repository Layer
Create `app/repositories/post_repository.py`:
- `create_post(title, content, author_id, published)` → Post
- `get_post_by_id(post_id)` → Post | None
- `list_posts(skip, limit)` → List[Post]
- `update_post(post_id, **updates)` → Post
- `delete_post(post_id)` → bool

### 4. Service Layer
Create `app/services/post_service.py`:
- `create_post(title, content, author_id, published)` → PostResponse
- `get_post(post_id)` → PostResponse
- `list_posts(page, page_size)` → PostListResponse
- `update_post(post_id, author_id, **updates)` → PostResponse
  - Verify author owns the post
- `delete_post(post_id, author_id)` → None
  - Verify author owns the post

### 5. Update API Routes
Replace mock implementations in `app/api/posts.py`:
- POST /api/posts → Create post (authenticated)
- GET /api/posts → List posts with pagination
- GET /api/posts/{post_id} → Get single post
- PUT /api/posts/{post_id} → Update post (author only)
- DELETE /api/posts/{post_id} → Delete post (author only)

### 6. Authorization Logic
- Check if user is post author before update/delete
- Return 403 Forbidden if not authorized
- Public endpoints (GET) don't require auth

### 7. Pagination
- Add query params: `?page=1&pageSize=10`
- Default: page=1, pageSize=20
- Return total count in response

### 8. E2E Tests
Create `tests/api/test_posts.py`:
- Test create post (authenticated)
- Test list posts (public)
- Test get post by ID (public)
- Test update own post (success)
- Test update other user's post (403)
- Test delete own post (success)
- Test delete other user's post (403)
- Test pagination

## Verification Steps
1. Create user and login to get token
2. Create post with token
3. List all posts (no token needed)
4. Get specific post by ID
5. Update post (with author token)
6. Try to update post (with different user token) → 403
7. Delete post (with author token)

## Acceptance Criteria

### Database Layer
- [ ] Post model created with all fields (id, title, content, author_id, created_at, updated_at, published)
- [ ] Foreign key relationship to User working
- [ ] Alembic migration applied successfully
- [ ] Database indexes created (author_id, created_at)
- [ ] Can query posts table directly in psql

### Repository Layer
- [ ] PostRepository implements all methods with async
- [ ] `create_post` returns Post object
- [ ] `get_post_by_id` returns None for non-existent posts
- [ ] `list_posts` supports skip/limit pagination
- [ ] `update_post` updates only provided fields
- [ ] `delete_post` removes from database

### Service Layer
- [ ] PostService validates business rules
- [ ] Only post author can update/delete (403 otherwise)
- [ ] Service converts DB models to response schemas
- [ ] Service handles None from repository (404)

### API Layer
- [ ] POST /api/posts creates post in database
- [ ] GET /api/posts returns paginated list
- [ ] GET /api/posts/{id} returns single post or 404
- [ ] PUT /api/posts/{id} updates post (author only)
- [ ] DELETE /api/posts/{id} deletes post (author only)
- [ ] Authorization checks prevent cross-user modifications
- [ ] Response includes author username (from join)

### Testing
- [ ] Can create post as authenticated user
- [ ] Created post persists in database
- [ ] Can list posts with pagination
- [ ] Can get single post by ID
- [ ] Returns 404 for non-existent post ID
- [ ] Can update own post
- [ ] Returns 403 when trying to update other user's post
- [ ] Can delete own post
- [ ] Returns 403 when trying to delete other user's post
- [ ] Timestamps (created_at, updated_at) work correctly
- [ ] All 6+ post E2E tests pass

## Troubleshooting

### Common Issues

**"no attribute 'posts' on User"**
- Add `posts = relationship("Post", back_populates="author")` to User model

**"Cannot update published field"**
- Ensure `published` is not excluded from update_post

**"403 on own post"**
- Check that current_user["user_id"] matches post.author_id (both UUID)

**"None returned from repository"**
- Service should convert None to HTTPException(404)

**Slow list queries**
- Add index on created_at
- Use pagination (don't load all posts)

## Anti-Patterns to Avoid

**❌ BAD - Allowing any user to modify any post:**
```python
async def update_post(post_id: str, request: UpdatePostRequest):
    # Missing authorization check!
    return await service.update_post(post_id, **request.dict())
```

**✅ GOOD - Check authorization:**
```python
async def update_post(
    post_id: str, 
    request: UpdatePostRequest,
    current_user: dict = Depends(require_auth)
):
    return await service.update_post(post_id, current_user["user_id"], **request.dict())
    # Service verifies current_user["user_id"] == post.author_id
```

**❌ BAD - Exposing password hash in response:**
```python
# Don't return full User object with password_hash
return post  # includes post.author.password_hash!
```

**✅ GOOD - Use response schema:**
```python
return PostResponse.model_validate(post)  # only includes specified fields
```

**❌ BAD - N+1 query problem:**
```python
posts = await repo.list_posts(skip, limit)
for post in posts:
    post.author_username = await get_user(post.author_id)  # N queries!
```

**✅ GOOD - Use joins:**
```python
query = select(Post).join(User).options(selectinload(Post.author))
# or
posts = await repo.list_posts_with_authors(skip, limit)
```

## Session Completion

When all acceptance criteria are met:
1. Run full test suite: `pytest tests/ -v`
2. Test manually via `/docs`
3. Verify in database: `psql $DATABASE_URL -c "SELECT * FROM posts LIMIT 5;"`
4. Create session summary document
5. Commit changes: `git add . && git commit -m "feat: implement posts CRUD (Phase 2)"`

## Next Session
Session 4 will implement Phase 3 (Comments) with nested resources and cascade deletes.

## Session Duration
Estimated: 90-120 minutes
