# Blog API — Repository Template

Spring Data `JpaRepository` interfaces for the posts/comments/users domain. Each interface
gets `save()`, `findById()`, `findAll()`, and `deleteById()` for free from `JpaRepository`;
only add methods actually needed by a session's endpoint.

## repository/UserRepository.java

```java
package com.example.blogapi.repository;

import com.example.blogapi.model.User;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, UUID> {

    Optional<User> findByEmail(String email);

    boolean existsByEmail(String email);
}
```

## repository/PostRepository.java

```java
package com.example.blogapi.repository;

import com.example.blogapi.model.Post;
import java.util.List;
import java.util.UUID;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface PostRepository extends JpaRepository<Post, UUID> {

    // Derived query method — Spring Data parses the method name into SQL
    List<Post> findByAuthorIdOrderByCreatedAtDesc(UUID authorId);

    // Pagination support for list endpoints
    Page<Post> findAllByOrderByCreatedAtDesc(Pageable pageable);

    // Custom JPQL for a case-insensitive title search
    @Query("SELECT p FROM Post p WHERE LOWER(p.title) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    List<Post> searchByTitle(@Param("keyword") String keyword);
}
```

## repository/CommentRepository.java

```java
package com.example.blogapi.repository;

import com.example.blogapi.model.Comment;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CommentRepository extends JpaRepository<Comment, UUID> {

    List<Comment> findByPostIdOrderByCreatedAtAsc(UUID postId);

    long countByPostId(UUID postId);
}
```

## Design Notes

- **Derived query methods** (`findByAuthorIdOrderByCreatedAtDesc`) are preferred over `@Query` whenever the method name alone can express the intent — Spring Data generates the JPQL automatically and it's checked at context-startup time, catching typos before runtime.
- **`@Query`** is reserved for cases a derived method name can't express cleanly (e.g. `LIKE` with `LOWER()`), matching the guidance in `rules/301-endpoint-phase.mdc`.
- **Pagination** (`Page<Post> findAllByOrderByCreatedAtDesc(Pageable)`) is used for the `GET /api/posts` list endpoint instead of returning an unbounded `List<Post>` — this mirrors the `limit`/`offset` pattern in the OpenAPI template but expressed as Spring's `Pageable`.
- **No repository method returns an `@Entity` to the controller directly** — the service layer always converts `Post`/`Comment`/`User` to a DTO before it reaches `web/`.
