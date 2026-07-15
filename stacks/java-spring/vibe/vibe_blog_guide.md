# Blog API Domain Guide

## Purpose

This guide provides domain-specific patterns for building a blog API with Spring Boot: posts,
comments, and users, wired together with JWT authentication and PostgreSQL persistence. It is
the Java/Spring Boot analog of `vibe_chatbot_guide.md` in the `python-fastapi` stack, and it
deliberately mirrors the **same posts + comments + users domain** as that stack's `blog-api`
reference solution so instructors can compare FastAPI and Spring Boot implementations of an
identical feature set side by side.

Matching template files: `templates/blog-controller.md`, `templates/blog-entity.md`,
`templates/blog-repository.md`, `templates/blog-service.md`, `templates/blog-tests.md`,
`templates/blog-dependencies.md`.

## Domain Overview

### Core Entities

**User**
- Represents an author who can create posts and comments
- Fields: `id` (UUID), `email`, `passwordHash`, `fullName`, `createdAt`
- Authenticated via email + password → JWT access token

**Post**
- A blog post written by a user
- Fields: `id` (UUID), `title`, `content`, `authorId`, `createdAt`, `updatedAt`
- Owned by exactly one `User` (via `authorId` foreign key, no JPA relationship mapping — see
  the design note in `templates/blog-entity.md`)

**Comment**
- A comment left on a post by a user
- Fields: `id` (UUID), `postId`, `authorId`, `content`, `createdAt`
- Belongs to exactly one `Post` and one `User`

### Entity Relationships

```
User (1) ──writes──> (N) Post
User (1) ──writes──> (N) Comment
Post (1) ──has──────> (N) Comment
```

### Basic Workflows

1. **Register**: Create a new user account, receive a JWT
2. **Login**: Authenticate an existing user, receive a JWT
3. **Create Post**: Authenticated user creates a blog post
4. **Read Post**: Anyone can read a single post by ID
5. **List Posts**: Anyone can browse posts, paginated
6. **Comment on Post**: Authenticated user comments on an existing post
7. **List Comments**: Anyone can read all comments for a post

## Data Modeling

### Layered Architecture

Follow the layered architecture from `rules/300-java-spring-style.mdc`:

```
web/                  # @RestController + DTOs — HTTP concerns only
  ├── AuthController.java
  ├── PostController.java
  ├── CommentController.java
  └── dto/
      ├── RegisterRequest.java / LoginRequest.java / AuthResponse.java
      ├── CreatePostRequest.java / PostResponse.java
      └── CreateCommentRequest.java / CommentResponse.java
service/              # @Service — business logic, @Transactional
  ├── UserService.java
  ├── PostService.java
  └── CommentService.java
repository/           # Spring Data JpaRepository interfaces
  ├── UserRepository.java
  ├── PostRepository.java
  └── CommentRepository.java
model/                # @Entity classes — persistence concerns only
  ├── User.java
  ├── Post.java
  └── Comment.java
```

### DTO Records (API Contract)

**Request DTOs**
```java
public record RegisterRequest(
    @NotBlank @Email String email,
    @NotBlank @Size(min = 8) String password,
    @NotBlank String fullName
) {}

public record CreatePostRequest(
    @NotBlank @Size(max = 200) String title,
    @NotBlank @Size(max = 10000) String content
) {}

public record CreateCommentRequest(@NotBlank @Size(max = 1000) String content) {}
```

**Response DTOs** — always constructed via a `from(entity)` static factory so the mapping is
explicit and greppable, never returning an `@Entity` directly:
```java
public record PostResponse(UUID postId, String title, String content, UUID authorId, Instant createdAt) {
    public static PostResponse from(Post post) {
        return new PostResponse(post.getId(), post.getTitle(), post.getContent(), post.getAuthorId(), post.getCreatedAt());
    }
}
```

See `templates/blog-controller.md` for the full DTO set.

### `@Entity` Classes (Persistence Contract)

See `templates/blog-entity.md` for the complete `User`/`Post`/`Comment` entities. Key points:
- UUID primary keys via `GenerationType.UUID` (Hibernate 6+), not database-generated `SERIAL`
- `@CreationTimestamp`/`@UpdateTimestamp` for audit columns — no manual `@PrePersist` needed
- Foreign keys (`authorId`, `postId`) are plain `UUID` columns, not `@ManyToOne` object
  references — a deliberate simplification for a first pass through the domain (see the design
  note in `templates/blog-entity.md` for when to introduce real JPA relationships)

## Authentication Flow

### JWT Issuing (`JwtService`)

```java
@Service
public class JwtService {

    @Value("${app.jwt.secret}")
    private String secret;

    @Value("${app.jwt.expiration-minutes:30}")
    private long expirationMinutes;

    public String generateToken(UUID userId) {
        SecretKey key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        return Jwts.builder()
            .subject(userId.toString())
            .issuedAt(new Date())
            .expiration(Date.from(Instant.now().plus(expirationMinutes, ChronoUnit.MINUTES)))
            .signWith(key)
            .compact();
    }

    public UUID extractUserId(String token) {
        SecretKey key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        Claims claims = Jwts.parser().verifyWith(key).build().parseSignedClaims(token).getPayload();
        return UUID.fromString(claims.getSubject());
    }
}
```

### Security Filter Chain (`SecurityConfig`)

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthFilter jwtAuthFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/actuator/health", "/swagger-ui/**", "/v3/api-docs/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/posts/**").permitAll()
                .anyRequest().authenticated())
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

### Custom JWT Filter (`JwtAuthFilter`)

```java
@Component
@RequiredArgsConstructor
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            try {
                UUID userId = jwtService.extractUserId(header.substring(7));
                var auth = new UsernamePasswordAuthenticationToken(
                    userId.toString(), null, List.of());
                SecurityContextHolder.getContext().setAuthentication(auth);
            } catch (JwtException e) {
                // Invalid/expired token — leave SecurityContext empty, request falls through as unauthenticated
            }
        }
        chain.doFilter(request, response);
    }
}
```

This is a **simplified, teaching-scale auth setup**: `UserDetails.getUsername()` is overloaded
to carry the raw UUID string rather than loading a full `UserDetails` from the database on every
request. State plainly to students that a production system would typically implement a real
`UserDetailsService` backed by `UserRepository`. This mirrors how the `python-fastapi` stack's
blog-api reference explicitly flags its own simplified in-memory auth as a teaching shortcut —
see `stacks/java-spring/examples/SETUP_COMPLETE.md`.

## Phase-by-Phase Build Order

Following `rules/000-core-workflow.mdc`'s 4-phase workflow, the blog domain breaks into these
sessions:

| Session | Phase | Endpoint | Depends On |
|---------|-------|----------|-----------|
| 1 | 0 (Skeleton) | All endpoints, mocked | — |
| 2 | 1 | `POST /api/auth/register` | Phase 0 |
| 3 | 2 | `POST /api/auth/login` | Phase 1 (User entity/repo) |
| 4 | 3 | `POST /api/posts` | Phase 2 (JWT auth working) |
| 5 | 4 | `GET /api/posts/{id}` | Phase 3 (Post entity/repo) |
| 6 | 5 | `GET /api/posts` (paginated) | Phase 4 |
| 7 | 6 | `POST /api/posts/{id}/comments` | Phase 4 (Post exists check) |
| 8 | 7 | `GET /api/posts/{id}/comments` | Phase 7 (Comment entity/repo) |

Each session follows `rules/301-endpoint-phase.mdc`: test first, then migration, then entity,
then repository, then service, then controller.

## Database Migrations

```sql
-- V1__create_users_table.sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- V2__create_posts_table.sql
CREATE TABLE posts (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_posts_author_id ON posts (author_id);
CREATE INDEX idx_posts_created_at ON posts (created_at);

-- V3__create_comments_table.sql
CREATE TABLE comments (
    id UUID PRIMARY KEY,
    post_id UUID NOT NULL REFERENCES posts(id),
    author_id UUID NOT NULL REFERENCES users(id),
    content VARCHAR(1000) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_comments_post_id ON comments (post_id);
```

Note that the SQL schema declares real foreign key constraints (`REFERENCES users(id)`) even
though the JPA `@Entity` classes use plain `UUID` columns instead of `@ManyToOne` — referential
integrity is still enforced at the database level, it's just not modeled as an object graph in
Hibernate for this teaching example.

## Testing Strategy

Following `rules/400-testing-first.mdc`, each endpoint gets:
1. A `@WebMvcTest` controller test (success, validation, auth, not-found cases)
2. A Mockito `@ExtendWith(MockitoExtension.class)` service unit test for business rules
3. At least one `@SpringBootTest` + Testcontainers integration test per sub-system (auth, posts,
   comments) exercising the full stack against real Postgres

See `templates/blog-tests.md` for the complete, runnable test classes — including the shared
`AbstractIntegrationTest` base class that all Testcontainers-backed tests extend.

## Common Pitfalls

### Returning `@Entity` Objects Directly
```java
// Bad — leaks Hibernate proxy objects, lazy-loading exceptions outside a transaction
@GetMapping("/{postId}")
public Post getPost(@PathVariable UUID postId) {
    return postRepository.findById(postId).orElseThrow();
}

// Good — service returns the entity, controller maps to DTO
@GetMapping("/{postId}")
public ResponseEntity<PostResponse> getPost(@PathVariable UUID postId) {
    return ResponseEntity.ok(PostResponse.from(postService.getPost(postId)));
}
```

### Missing `@Transactional` on Multi-Step Writes
```java
// Bad — if the second save fails, the first is not rolled back
public Post createPostWithNotification(CreatePostRequest request, UUID authorId) {
    Post post = postRepository.save(toEntity(request, authorId));
    notificationRepository.save(new Notification(authorId, "Post created"));
    return post;
}

// Good — @Transactional wraps both writes in one commit/rollback unit
@Transactional
public Post createPostWithNotification(CreatePostRequest request, UUID authorId) {
    Post post = postRepository.save(toEntity(request, authorId));
    notificationRepository.save(new Notification(authorId, "Post created"));
    return post;
}
```

### Skipping the "Post Exists" Check Before Commenting
```java
// Bad — silently creates an orphaned comment if postId doesn't exist
public Comment createComment(UUID postId, CreateCommentRequest request, UUID authorId) {
    Comment comment = new Comment();
    comment.setPostId(postId);
    // ...
    return commentRepository.save(comment);
}

// Good — fail fast with a proper 404 before writing
public Comment createComment(UUID postId, CreateCommentRequest request, UUID authorId) {
    if (!postRepository.existsById(postId)) {
        throw new EntityNotFoundException("Post not found: " + postId);
    }
    // ...
}
```

## Extending This Domain

Natural next phases once the core CRUD is working:
- **Post tags/categories**: new `tags` table + `@ManyToMany` (a good place to finally introduce
  real JPA relationship mapping, once students are comfortable with the plain-FK approach)
- **Soft deletes**: add `deleted_at` column instead of hard `DELETE`, filter in repository queries
- **Full-text search**: Postgres `tsvector` column + a custom `@Query` using `@@`
- **Rate limiting**: Bucket4j + a `@Component` filter, applied to `POST` endpoints only
- **Optimistic locking**: `@Version` field on `Post` to prevent lost updates on concurrent edits
