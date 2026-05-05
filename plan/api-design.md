# Blog API Design

## Architecture
REST API — FastAPI async endpoints, SQLAlchemy 2.0 ORM, Alembic migrations, Pydantic v2 schemas. Modular monolith pattern.

## API Endpoints

### Authentication
- `POST /api/auth/register` — Register new user
- `POST /api/auth/login` — Login and get JWT token
- `GET /api/auth/me` — Get current user profile

### Posts
- `POST /api/posts` — Create a new blog post (authenticated)
- `GET /api/posts` — List all posts (paginated, public)
- `GET /api/posts/{post_id}` — Get single post by ID (public)
- `PUT /api/posts/{post_id}` — Update post (authenticated, author only)
- `DELETE /api/posts/{post_id}` — Delete post (authenticated, author only)

### Comments
- `POST /api/posts/{post_id}/comments` — Add comment to post (authenticated)
- `GET /api/posts/{post_id}/comments` — List comments for post (public)
- `DELETE /api/comments/{comment_id}` — Delete comment (authenticated, author only)

### Tags
- `GET /api/tags` — List all tags (public)
- `GET /api/tags/{tag_name}/posts` — Get posts by tag (public)

### Health
- `GET /health` — Health check endpoint

## Data Models

### User
- `id` (UUID, primary key)
- `username` (string, unique)
- `email` (string, unique)
- `password_hash` (string)
- `created_at` (timestamp)

### Post
- `id` (UUID, primary key)
- `title` (string)
- `content` (text)
- `author_id` (UUID, foreign key to User)
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `published` (boolean)

### Comment
- `id` (UUID, primary key)
- `post_id` (UUID, foreign key to Post)
- `author_id` (UUID, foreign key to User)
- `content` (text)
- `created_at` (timestamp)

### Tag
- `id` (UUID, primary key)
- `name` (string, unique)

### PostTag (many-to-many junction)
- `post_id` (UUID, foreign key to Post)
- `tag_id` (UUID, foreign key to Tag)

## Request/Response Schemas

### Authentication
- `RegisterRequest`: { username, email, password }
- `LoginRequest`: { email, password }
- `AuthResponse`: { accessToken, tokenType, userId, username }
- `UserResponse`: { userId, username, email, createdAt }

### Posts
- `CreatePostRequest`: { title, content, tags?, published? }
- `UpdatePostRequest`: { title?, content?, tags?, published? }
- `PostResponse`: { postId, title, content, authorId, authorUsername, createdAt, updatedAt, published, tags[] }
- `PostListResponse`: { posts[], total, page, pageSize }

### Comments
- `CreateCommentRequest`: { content }
- `CommentResponse`: { commentId, postId, authorId, authorUsername, content, createdAt }

### Tags
- `TagResponse`: { tagId, name, postCount }

## Authentication
- JWT token-based authentication
- Token in Authorization header: `Bearer <token>`
- Token expiry: 7 days
- Protected routes require valid token

## Phase Breakdown

### Phase 0: Skeleton
Create walking skeleton with mock data for all endpoints. No database, no real auth.

### Phase 1: Authentication
Implement user registration, login, JWT generation. Create User model, repository, service.

### Phase 2: Posts CRUD
Implement posts creation, listing, retrieval, update, delete. Create Post model, repository, service.

### Phase 3: Comments
Implement comment creation and listing. Create Comment model, repository, service.

### Phase 4: Tags
Implement tags and post-tag relationships. Create Tag model, repository, service.

### Phase 5: Polish & Deploy
Add pagination, filtering, sorting. Docker production setup. Documentation.
