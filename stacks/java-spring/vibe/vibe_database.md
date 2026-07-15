# Database Guide (JPA / Hibernate + Flyway)

This guide covers entity mapping, migration authoring, query patterns, connection pooling, and
transaction management for Spring Data JPA against PostgreSQL.

## Entity Mapping Fundamentals

### `@Entity` / `@Id` / `@GeneratedValue`

```java
@Entity
@Table(name = "posts")
@Getter
@Setter
@NoArgsConstructor
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)  // Hibernate 6+ generates a UUID in Java, not DB-side
    private UUID id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;
}
```

`GenerationType.UUID` (available since Hibernate 6 / Spring Boot 3) generates the UUID in the
application layer before the INSERT — this avoids a round-trip to fetch a database-generated ID
and keeps IDs consistent whether the row came from a migration seed or the application.

### `@OneToMany` / `@ManyToOne`

```java
@Entity
@Table(name = "posts")
public class Post {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;

    @OneToMany(mappedBy = "post", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Comment> comments = new ArrayList<>();
}

@Entity
@Table(name = "comments")
public class Comment {
    @Id @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "post_id", nullable = false)
    private Post post;
}
```

**Always default to `FetchType.LAZY`** on `@ManyToOne`/`@OneToMany`. Eager fetching pulls the
entire object graph on every query, which silently turns a simple `findById` into a cascade of
joins or N+1 queries. Note: the `templates/blog-*.md` teaching example intentionally uses plain
`UUID` foreign-key columns instead of `@ManyToOne` object references for its first pass through
the domain — introduce true relationship mapping (as shown here) once lazy loading has been
taught explicitly.

### `@CreationTimestamp` / `@UpdateTimestamp`

```java
@CreationTimestamp
@Column(name = "created_at", updatable = false)
private Instant createdAt;

@UpdateTimestamp
@Column(name = "updated_at")
private Instant updatedAt;
```

These are Hibernate-specific annotations (`org.hibernate.annotations.*`) that populate audit
timestamps automatically — no `@PrePersist`/`@PreUpdate` lifecycle callback needed.

## Flyway Migrations

### Naming Convention

```
src/main/resources/db/migration/
├── V1__create_users_table.sql
├── V2__create_posts_table.sql
├── V3__create_comments_table.sql
└── V4__add_post_status_column.sql
```

`V{version}__{description}.sql` — version numbers are strictly increasing integers (or
dot-separated like `V1.1__`), double underscore separates version from description, description
uses underscores not spaces.

### Migration Authoring Rules

- **Never edit an already-applied migration.** Flyway checksums each migration; editing a
  historical file after it has run in any environment breaks `flyway validate`. Write a new
  migration to fix or undo something instead.
- **Every table gets:** a UUID primary key, `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`,
  indexes on foreign key columns and any column used in `WHERE`/`ORDER BY`.
- **Foreign keys use `REFERENCES`** for referential integrity, even when the corresponding
  `@Entity` uses a plain `UUID` column instead of a JPA relationship (see the design note in
  `templates/blog-entity.md`).

```sql
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
```

### Applying Migrations

Flyway runs automatically on application startup when `spring.flyway.enabled=true` (the
default once `flyway-core` is on the classpath). To preview pending migrations without starting
the full app:

```bash
./mvnw flyway:info
./mvnw flyway:migrate    # apply pending migrations directly, outside app startup
```

### `ddl-auto` Must Be `validate`, Never `update`

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate  # Hibernate checks the schema matches entities, but never mutates it
```

Flyway is the single source of truth for schema changes. `ddl-auto: update` (or worse,
`create-drop`) lets Hibernate silently alter the schema based on entity changes — this causes
schema drift between environments and defeats the purpose of versioned migrations. `validate`
makes Hibernate fail fast at startup if the entity mapping and the migrated schema disagree.

## Spring Data Query-Method Naming

Spring Data parses repository method names into JPQL automatically — no implementation needed:

```java
public interface PostRepository extends JpaRepository<Post, UUID> {

    // SELECT p FROM Post p WHERE p.authorId = ?1 ORDER BY p.createdAt DESC
    List<Post> findByAuthorIdOrderByCreatedAtDesc(UUID authorId);

    // SELECT p FROM Post p WHERE p.title = ?1
    Optional<Post> findByTitle(String title);

    // SELECT COUNT(p) FROM Post p WHERE p.authorId = ?1
    long countByAuthorId(UUID authorId);

    // SELECT CASE WHEN COUNT(p) > 0 THEN true ELSE false END FROM Post p WHERE p.id = ?1
    boolean existsById(UUID id);  // inherited from JpaRepository, shown for clarity

    // Pagination
    Page<Post> findAllByOrderByCreatedAtDesc(Pageable pageable);
}
```

### `@Query` for Anything a Method Name Can't Express

```java
public interface PostRepository extends JpaRepository<Post, UUID> {

    @Query("SELECT p FROM Post p WHERE LOWER(p.title) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    List<Post> searchByTitle(@Param("keyword") String keyword);

    // Native SQL when JPQL can't express it (e.g. Postgres full-text search)
    @Query(value = "SELECT * FROM posts WHERE to_tsvector('english', content) @@ plainto_tsquery(:query)",
           nativeQuery = true)
    List<Post> fullTextSearch(@Param("query") String query);
}
```

Prefer derived method names first; reach for `@Query` only when the method-name DSL genuinely
can't express the query — this keeps most repository code declarative and typo-checked at
context-startup time.

## HikariCP Tuning

Spring Boot uses HikariCP by default — the pool almost never needs manual tuning for a teaching
app, but know the levers for production:

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10       # default: 10; size to (core_count * 2) + effective_spindle_count as a starting heuristic
      minimum-idle: 5
      connection-timeout: 30000   # ms to wait for a connection before throwing
      idle-timeout: 600000        # ms before an idle connection is retired
      max-lifetime: 1800000       # ms before a connection is forcibly recycled
```

For a single Spring Boot instance behind Postgres, the default pool size (10) is usually
sufficient up to moderate load — the first tuning lever to reach for is almost always the
`maximum-pool-size`, matched against Postgres's own `max_connections`.

## `@Transactional` Propagation and Isolation Basics

```java
@Service
@RequiredArgsConstructor
public class PostService {

    private final PostRepository postRepository;

    @Transactional  // REQUIRED propagation (default): joins an existing tx or starts a new one
    public Post createPost(CreatePostRequest request, UUID authorId) {
        return postRepository.save(toEntity(request, authorId));
    }

    @Transactional(readOnly = true)  // hints Hibernate to skip dirty-checking, minor perf win
    public Post getPost(UUID postId) {
        return postRepository.findById(postId)
            .orElseThrow(() -> new EntityNotFoundException("Post not found: " + postId));
    }

    @Transactional(isolation = Isolation.READ_COMMITTED)  // Postgres default; rarely needs overriding
    public void transferOwnership(UUID postId, UUID newAuthorId) {
        Post post = postRepository.findById(postId).orElseThrow();
        post.setAuthorId(newAuthorId);
        // no explicit save() needed — dirty checking flushes the change at commit
    }
}
```

Key rules:
- `@Transactional` belongs on `@Service` methods, never on `@RestController` methods (see
  `rules/300-java-spring-style.mdc`)
- Default propagation (`REQUIRED`) is correct for almost all service methods
- Use `readOnly = true` on pure read methods — it's a hint to Hibernate/the JDBC driver, not a
  hard constraint, but it documents intent and can skip unnecessary dirty-checking
- Postgres's default isolation level (`READ_COMMITTED`) is almost always the right choice;
  reach for `SERIALIZABLE` only for genuine race-condition-sensitive logic (rare in a teaching app)
