# Blog API — Controller Template

`@RestController` classes for the posts/comments/users domain, plus the request/response
DTOs and the global exception handler. Controllers are intentionally thin: validate input,
delegate to a `@Service`, map the result to a DTO.

## web/dto/RegisterRequest.java

```java
package com.example.blogapi.web.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record RegisterRequest(
    @NotBlank @Email String email,
    @NotBlank @Size(min = 8) String password,
    @NotBlank String fullName
) {}
```

## web/dto/AuthResponse.java

```java
package com.example.blogapi.web.dto;

import java.util.UUID;

public record AuthResponse(String accessToken, UUID userId, String email, String fullName) {}
```

## web/dto/CreatePostRequest.java

```java
package com.example.blogapi.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record CreatePostRequest(
    @NotBlank @Size(max = 200) String title,
    @NotBlank @Size(max = 10000) String content
) {}
```

## web/dto/PostResponse.java

```java
package com.example.blogapi.web.dto;

import com.example.blogapi.model.Post;
import java.time.Instant;
import java.util.UUID;

public record PostResponse(
    UUID postId,
    String title,
    String content,
    UUID authorId,
    Instant createdAt
) {
    public static PostResponse from(Post post) {
        return new PostResponse(
            post.getId(), post.getTitle(), post.getContent(), post.getAuthorId(), post.getCreatedAt());
    }
}
```

## web/dto/CreateCommentRequest.java

```java
package com.example.blogapi.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateCommentRequest(@NotBlank @Size(max = 1000) String content) {}
```

## web/dto/CommentResponse.java

```java
package com.example.blogapi.web.dto;

import com.example.blogapi.model.Comment;
import java.time.Instant;
import java.util.UUID;

public record CommentResponse(UUID commentId, UUID postId, String content, UUID authorId, Instant createdAt) {
    public static CommentResponse from(Comment comment) {
        return new CommentResponse(
            comment.getId(), comment.getPostId(), comment.getContent(), comment.getAuthorId(), comment.getCreatedAt());
    }
}
```

## web/AuthController.java

```java
package com.example.blogapi.web;

import com.example.blogapi.model.User;
import com.example.blogapi.security.JwtService;
import com.example.blogapi.service.UserService;
import com.example.blogapi.web.dto.AuthResponse;
import com.example.blogapi.web.dto.LoginRequest;
import com.example.blogapi.web.dto.RegisterRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final UserService userService;
    private final JwtService jwtService;
    private final AuthenticationManager authenticationManager;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        User user = userService.register(request);
        String token = jwtService.generateToken(user.getId());
        return ResponseEntity.ok(new AuthResponse(token, user.getId(), user.getEmail(), user.getFullName()));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        authenticationManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.email(), request.password()));
        User user = userService.findByEmailOrThrow(request.email());
        String token = jwtService.generateToken(user.getId());
        return ResponseEntity.ok(new AuthResponse(token, user.getId(), user.getEmail(), user.getFullName()));
    }
}
```

## web/PostController.java

```java
package com.example.blogapi.web;

import com.example.blogapi.model.Post;
import com.example.blogapi.service.PostService;
import com.example.blogapi.web.dto.CreatePostRequest;
import com.example.blogapi.web.dto.PostResponse;
import jakarta.validation.Valid;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    @PostMapping
    public ResponseEntity<PostResponse> createPost(
            @Valid @RequestBody CreatePostRequest request,
            @AuthenticationPrincipal UserDetails currentUser) {
        UUID authorId = UUID.fromString(currentUser.getUsername());
        Post created = postService.createPost(request, authorId);
        return ResponseEntity.ok(PostResponse.from(created));
    }

    @GetMapping("/{postId}")
    public ResponseEntity<PostResponse> getPost(@PathVariable UUID postId) {
        Post post = postService.getPost(postId);
        return ResponseEntity.ok(PostResponse.from(post));
    }

    @GetMapping
    public ResponseEntity<Page<PostResponse>> listPosts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<PostResponse> response = postService.listPosts(pageable).map(PostResponse::from);
        return ResponseEntity.ok(response);
    }
}
```

## web/CommentController.java

```java
package com.example.blogapi.web;

import com.example.blogapi.model.Comment;
import com.example.blogapi.service.CommentService;
import com.example.blogapi.web.dto.CommentResponse;
import com.example.blogapi.web.dto.CreateCommentRequest;
import jakarta.validation.Valid;
import java.util.List;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/posts/{postId}/comments")
@RequiredArgsConstructor
public class CommentController {

    private final CommentService commentService;

    @PostMapping
    public ResponseEntity<CommentResponse> createComment(
            @PathVariable UUID postId,
            @Valid @RequestBody CreateCommentRequest request,
            @AuthenticationPrincipal UserDetails currentUser) {
        UUID authorId = UUID.fromString(currentUser.getUsername());
        Comment created = commentService.createComment(postId, request, authorId);
        return ResponseEntity.ok(CommentResponse.from(created));
    }

    @GetMapping
    public ResponseEntity<List<CommentResponse>> listComments(@PathVariable UUID postId) {
        List<CommentResponse> response = commentService.listComments(postId).stream()
            .map(CommentResponse::from)
            .toList();
        return ResponseEntity.ok(response);
    }
}
```

## exception/GlobalExceptionHandler.java

```java
package com.example.blogapi.exception;

import jakarta.persistence.EntityNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(EntityNotFoundException.class)
    public ProblemDetail handleNotFound(EntityNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Resource Not Found");
        return problem;
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ProblemDetail handleBadRequest(IllegalArgumentException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, ex.getMessage());
        problem.setTitle("Invalid Request");
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
            .map(err -> err.getField() + ": " + err.getDefaultMessage())
            .collect(Collectors.joining(", "));
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, detail);
        problem.setTitle("Validation Failed");
        return problem;
    }
}
```

## Design Notes

- **`AuthController` uses Spring Security's `AuthenticationManager`** rather than hand-rolled password comparison — this is the idiomatic Spring way to verify credentials and keeps `PasswordEncoder` usage centralized.
- **`@AuthenticationPrincipal UserDetails currentUser`** is how the authenticated user's identity reaches a controller method; the JWT filter (see `blog-tests.md` / example app `SecurityConfig`) is responsible for populating the `SecurityContext` before the controller runs.
- **Every response DTO has a `from(entity)` static factory** — a small, explicit, greppable mapping point instead of a generic reflection-based mapper (MapStruct is a valid alternative for larger domains, but for this teaching-sized example, manual mapping keeps the data flow visible).
- **Pagination surfaces Spring's `Page<T>` directly** in the list-posts response — `Page` already serializes to JSON with `content`, `totalElements`, `totalPages`, etc., so no bespoke `PostListResponse` wrapper is needed for this endpoint.
