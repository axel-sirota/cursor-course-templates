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
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/posts/{postId}/comments")
@RequiredArgsConstructor
public class CommentController {

    private final CommentService commentService;

    /** Adds a comment to an existing post. */
    @PostMapping
    public ResponseEntity<CommentResponse> createComment(
            @PathVariable UUID postId,
            @Valid @RequestBody CreateCommentRequest request,
            @AuthenticationPrincipal UserDetails currentUser) {
        UUID authorId = UUID.fromString(currentUser.getUsername());
        Comment created = commentService.createComment(postId, request, authorId);
        return ResponseEntity.ok(CommentResponse.from(created));
    }

    /** Lists all comments for a post, oldest first. Publicly readable. */
    @GetMapping
    public ResponseEntity<List<CommentResponse>> listComments(@PathVariable UUID postId) {
        List<CommentResponse> response = commentService.listComments(postId).stream()
            .map(CommentResponse::from)
            .toList();
        return ResponseEntity.ok(response);
    }
}
