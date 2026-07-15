# Blog API — Service Template

`@Service` classes for the posts/comments/users domain. All business logic and
`@Transactional` boundaries live here — controllers stay thin (see `blog-controller.md`).

## service/UserService.java

```java
package com.example.blogapi.service;

import com.example.blogapi.model.User;
import com.example.blogapi.repository.UserRepository;
import com.example.blogapi.web.dto.RegisterRequest;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public User register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new IllegalArgumentException("Email already registered: " + request.email());
        }

        User user = new User();
        user.setEmail(request.email());
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        user.setFullName(request.fullName());

        User saved = userRepository.save(user);
        log.info("Registered user {}", saved.getId());
        return saved;
    }

    public User findByEmailOrThrow(String email) {
        return userRepository.findByEmail(email)
            .orElseThrow(() -> new IllegalArgumentException("Invalid credentials"));
    }
}
```

## service/PostService.java

```java
package com.example.blogapi.service;

import com.example.blogapi.model.Post;
import com.example.blogapi.repository.PostRepository;
import com.example.blogapi.web.dto.CreatePostRequest;
import jakarta.persistence.EntityNotFoundException;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class PostService {

    private final PostRepository postRepository;

    @Transactional
    public Post createPost(CreatePostRequest request, UUID authorId) {
        if (request.title().length() < 3) {
            throw new IllegalArgumentException("Title must be at least 3 characters");
        }

        Post post = new Post();
        post.setTitle(request.title());
        post.setContent(request.content());
        post.setAuthorId(authorId);

        Post saved = postRepository.save(post);
        log.info("Created post {} for author {}", saved.getId(), authorId);
        return saved;
    }

    public Post getPost(UUID postId) {
        return postRepository.findById(postId)
            .orElseThrow(() -> new EntityNotFoundException("Post not found: " + postId));
    }

    public Page<Post> listPosts(Pageable pageable) {
        return postRepository.findAllByOrderByCreatedAtDesc(pageable);
    }
}
```

## service/CommentService.java

```java
package com.example.blogapi.service;

import com.example.blogapi.model.Comment;
import com.example.blogapi.repository.CommentRepository;
import com.example.blogapi.repository.PostRepository;
import com.example.blogapi.web.dto.CreateCommentRequest;
import jakarta.persistence.EntityNotFoundException;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class CommentService {

    private final CommentRepository commentRepository;
    private final PostRepository postRepository;

    @Transactional
    public Comment createComment(UUID postId, CreateCommentRequest request, UUID authorId) {
        if (!postRepository.existsById(postId)) {
            throw new EntityNotFoundException("Post not found: " + postId);
        }

        Comment comment = new Comment();
        comment.setPostId(postId);
        comment.setAuthorId(authorId);
        comment.setContent(request.content());

        Comment saved = commentRepository.save(comment);
        log.info("Created comment {} on post {}", saved.getId(), postId);
        return saved;
    }

    public List<Comment> listComments(UUID postId) {
        if (!postRepository.existsById(postId)) {
            throw new EntityNotFoundException("Post not found: " + postId);
        }
        return commentRepository.findByPostIdOrderByCreatedAtAsc(postId);
    }
}
```

## Design Notes

- **`@Transactional` lives on the service method**, never on the controller — see `rules/300-java-spring-style.mdc`. Read-only methods (`getPost`, `listPosts`, `listComments`) intentionally omit `@Transactional`; Spring Data repository calls are transactional by default for a single query.
- **Business-rule validation** beyond `jakarta.validation` (e.g. "email already registered", "post must exist before commenting") lives here, not in the controller or the DTO.
- **Cross-entity checks** (does `postId` exist before creating a comment) belong in the service that owns the write, using another repository's `existsById()` rather than duplicating a full fetch.
- **Typed exceptions** (`EntityNotFoundException`, `IllegalArgumentException`) are thrown here and mapped to HTTP status codes centrally by `@RestControllerAdvice` — see `blog-controller.md`.
