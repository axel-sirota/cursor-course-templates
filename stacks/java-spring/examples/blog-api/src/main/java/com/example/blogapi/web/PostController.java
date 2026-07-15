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
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    /** Creates a new blog post for the authenticated user. */
    @PostMapping
    public ResponseEntity<PostResponse> createPost(
            @Valid @RequestBody CreatePostRequest request,
            @AuthenticationPrincipal UserDetails currentUser) {
        UUID authorId = UUID.fromString(currentUser.getUsername());
        Post created = postService.createPost(request, authorId);
        return ResponseEntity.ok(PostResponse.from(created));
    }

    /** Fetches a single post by id. Publicly readable. */
    @GetMapping("/{postId}")
    public ResponseEntity<PostResponse> getPost(@PathVariable UUID postId) {
        Post post = postService.getPost(postId);
        return ResponseEntity.ok(PostResponse.from(post));
    }

    /** Lists posts newest-first, paginated. Publicly readable. */
    @GetMapping
    public ResponseEntity<Page<PostResponse>> listPosts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<PostResponse> response = postService.listPosts(pageable).map(PostResponse::from);
        return ResponseEntity.ok(response);
    }
}
