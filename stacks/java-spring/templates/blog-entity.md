# Blog API — Entity Template

`@Entity` classes for the posts/comments/users domain. These live in `model/` and never
leave the service layer — controllers only ever see DTOs (see `blog-controller.md`).

## model/User.java

```java
package com.example.blogapi.model;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true, length = 255)
    private String email;

    @Column(name = "password_hash", nullable = false)
    private String passwordHash;

    @Column(name = "full_name", nullable = false, length = 200)
    private String fullName;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private Instant createdAt;
}
```

## model/Post.java

```java
package com.example.blogapi.model;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

@Entity
@Table(name = "posts")
@Getter
@Setter
@NoArgsConstructor
public class Post {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, length = 200)
    private String title;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Column(name = "author_id", nullable = false)
    private UUID authorId;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private Instant createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private Instant updatedAt;
}
```

## model/Comment.java

```java
package com.example.blogapi.model;

import jakarta.persistence.*;
import java.time.Instant;
import java.util.UUID;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;

@Entity
@Table(name = "comments")
@Getter
@Setter
@NoArgsConstructor
public class Comment {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "post_id", nullable = false)
    private UUID postId;

    @Column(name = "author_id", nullable = false)
    private UUID authorId;

    @Column(nullable = false, length = 1000)
    private String content;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private Instant createdAt;
}
```

## Design Notes

- **UUID primary keys** generated at the JPA layer (`GenerationType.UUID`, Hibernate 6+), not database `SERIAL` — keeps IDs opaque and consistent with the OpenAPI schema (`format: uuid`).
- **No `@ManyToOne`/`@OneToMany` object graph** between `Post` and `Comment` in this teaching example — `postId`/`authorId` are plain `UUID` foreign-key columns. This is a deliberate simplification: it keeps each entity independently loadable without lazy-loading/`N+1` traps for students who haven't covered fetch strategies yet. A follow-up lesson can introduce `@OneToMany(mappedBy = "post")` once lazy loading is taught.
- **`@CreationTimestamp`/`@UpdateTimestamp`** (Hibernate-specific annotations) populate audit columns without needing `@PrePersist`/`@PreUpdate` callbacks.
- **`columnDefinition = "TEXT"`** on `content` fields avoids the default `VARCHAR(255)` truncation for long post bodies and comments.
